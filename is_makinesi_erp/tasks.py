import frappe
from frappe import _
from frappe.utils import today, add_days, nowdate, getdate


def check_bakim_bildirimi():
	"""Periyodik bakım zamanı gelen makineler için bildirim oluşturur (Requirement 15.1).

	Aktif makinelerde saat_sayaci >= sonraki_bakim_saati olan makineleri bulur
	ve yöneticiye Notification Log ile bildirim gönderir.
	"""
	machines = frappe.get_all(
		"Makine",
		filters={
			"durum": "Aktif",
			"sonraki_bakim_saati": [">", 0],
		},
		fields=["name", "makine_adi", "saat_sayaci", "sonraki_bakim_saati"],
	)

	for m in machines:
		if m.saat_sayaci >= m.sonraki_bakim_saati:
			message = _(
				"{0} ({1}) makinesi için periyodik bakım zamanı geldi. "
				"Saat sayacı: {2}, Bakım saati: {3}"
			).format(m.makine_adi, m.name, m.saat_sayaci, m.sonraki_bakim_saati)

			_create_notification(
				subject=_("Periyodik Bakım Bildirimi: {0}").format(m.makine_adi),
				message=message,
				document_type="Makine",
				document_name=m.name,
			)


def check_hakedis_vade_bildirimi():
	"""Hakediş ödeme vadesi yaklaşan kayıtlar için bildirim oluşturur (Requirement 15.2).

	Dönem bitiş tarihi geçmiş ve ödeme durumu 'Beklemede' veya 'Kısmi Ödendi' olan
	makine ve personel hakedişlerini bulur.
	"""
	bugun = today()

	# Makine hakedişleri
	makine_hakedisler = frappe.get_all(
		"Makine Hakedis",
		filters={
			"odeme_durumu": ["in", ["Beklemede", "Kısmi Ödendi"]],
			"donem_bitis": ["<=", bugun],
		},
		fields=["name", "makine", "proje", "toplam_tutar", "kalan_tutar", "donem_bitis"],
	)

	for h in makine_hakedisler:
		message = _(
			"Makine hakedişi {0} için ödeme vadesi geçti. "
			"Makine: {1}, Proje: {2}, Kalan tutar: {3}"
		).format(h.name, h.makine, h.proje, h.kalan_tutar)

		_create_notification(
			subject=_("Hakediş Ödeme Hatırlatması: {0}").format(h.name),
			message=message,
			document_type="Makine Hakedis",
			document_name=h.name,
		)

	# Personel hakedişleri
	personel_hakedisler = frappe.get_all(
		"Personel Hakedis",
		filters={
			"odeme_durumu": ["in", ["Beklemede", "Kısmi Ödendi"]],
			"donem_bitis": ["<=", bugun],
		},
		fields=["name", "personel", "proje", "toplam_tutar", "kalan_tutar", "donem_bitis"],
	)

	for h in personel_hakedisler:
		message = _(
			"Personel hakedişi {0} için ödeme vadesi geçti. "
			"Personel: {1}, Proje: {2}, Kalan tutar: {3}"
		).format(h.name, h.personel, h.proje, h.kalan_tutar)

		_create_notification(
			subject=_("Hakediş Ödeme Hatırlatması: {0}").format(h.name),
			message=message,
			document_type="Personel Hakedis",
			document_name=h.name,
		)


def check_eksik_puantaj_bildirimi():
	"""Gün sonunda puantaj girişi yapılmamış aktif makine/personel bildirimi (Requirement 15.3).

	Bugün için puantaj kaydı olmayan aktif makineleri ve aktif personeli bulur.
	"""
	bugun = today()

	# Aktif makineler
	aktif_makineler = frappe.get_all(
		"Makine",
		filters={"durum": "Aktif", "mevcut_proje": ["is", "set"]},
		fields=["name", "makine_adi"],
	)

	puantaji_olan_makineler = set(
		r.makine
		for r in frappe.get_all(
			"Makine Puantaj",
			filters={"tarih": bugun},
			fields=["makine"],
		)
	)

	eksik_makineler = [
		m for m in aktif_makineler if m.name not in puantaji_olan_makineler
	]

	if eksik_makineler:
		makine_listesi = ", ".join(
			"{0} ({1})".format(m.makine_adi, m.name) for m in eksik_makineler[:10]
		)
		fazla = len(eksik_makineler) - 10
		if fazla > 0:
			makine_listesi += _(" ve {0} makine daha").format(fazla)

		_create_notification(
			subject=_("Eksik Makine Puantajı: {0}").format(bugun),
			message=_("Bugün için puantaj girişi yapılmamış aktif makineler: {0}").format(
				makine_listesi
			),
		)

	# Aktif personel (status = Active olan Employee'ler)
	aktif_personel = frappe.get_all(
		"Employee",
		filters={"status": "Active"},
		fields=["name", "employee_name"],
	)

	puantaji_olan_personel = set(
		r.personel
		for r in frappe.get_all(
			"Personel Puantaj",
			filters={"tarih": bugun},
			fields=["personel"],
		)
	)

	eksik_personel = [
		p for p in aktif_personel if p.name not in puantaji_olan_personel
	]

	if eksik_personel:
		personel_listesi = ", ".join(
			"{0} ({1})".format(p.employee_name, p.name) for p in eksik_personel[:10]
		)
		fazla = len(eksik_personel) - 10
		if fazla > 0:
			personel_listesi += _(" ve {0} personel daha").format(fazla)

		_create_notification(
			subject=_("Eksik Personel Puantajı: {0}").format(bugun),
			message=_("Bugün için puantaj girişi yapılmamış aktif personel: {0}").format(
				personel_listesi
			),
		)


def check_dusuk_stok_uyarisi():
	"""Düşük stok uyarısı - stok miktarı minimum seviyenin altına düştüğünde (Requirement 15.4).

	ERPNext Item'lardaki skal ürünlerinin stok miktarını kontrol eder.
	Varsayılan minimum stok seviyesi: 1 ton.
	"""
	# Skal ürünlerini bul (Is Makinesi ERP modülü ile ilişkili Item'lar)
	skal_items = frappe.get_all(
		"Item",
		filters={"item_group": "Skal Ürünleri"},
		fields=["name", "item_name"],
	)

	if not skal_items:
		return

	for item in skal_items:
		# Mevcut stok miktarını al
		stok_miktari = (
			frappe.db.sql(
				"""
				SELECT SUM(actual_qty) as toplam
				FROM `tabBin`
				WHERE item_code = %s
			""",
				item.name,
				as_dict=True,
			)[0].toplam
			or 0
		)

		# Minimum stok seviyesi (varsayılan 1 ton)
		min_stok = frappe.db.get_single_value("Stock Settings", "auto_indent") or 1

		if stok_miktari < min_stok:
			message = _(
				"{0} ürününün stok miktarı düşük. "
				"Mevcut stok: {1} ton, Minimum seviye: {2} ton"
			).format(item.item_name, stok_miktari, min_stok)

			_create_notification(
				subject=_("Düşük Stok Uyarısı: {0}").format(item.item_name),
				message=message,
				document_type="Item",
				document_name=item.name,
			)


def _create_notification(subject, message, document_type=None, document_name=None):
	"""Sistem yöneticilerine Notification Log oluşturur."""
	# System Manager rolüne sahip kullanıcıları bul
	users = frappe.get_all(
		"Has Role",
		filters={"role": "System Manager", "parenttype": "User"},
		fields=["parent"],
		distinct=True,
	)

	for user in users:
		if user.parent == "Administrator" or user.parent == "Guest":
			continue

		notification = frappe.get_doc(
			{
				"doctype": "Notification Log",
				"for_user": user.parent,
				"from_user": "Administrator",
				"subject": subject,
				"type": "Alert",
				"email_content": message,
				"document_type": document_type or "",
				"document_name": document_name or "",
			}
		)
		notification.insert(ignore_permissions=True)

	frappe.db.commit()
