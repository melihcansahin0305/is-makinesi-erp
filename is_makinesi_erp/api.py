import json

import frappe
from frappe import _


@frappe.whitelist()
def toplu_puantaj_kaydet(data):
	"""Toplu puantaj girişi API'si (Requirements 4.5, 5.5).

	Tarih ve proje seçildikten sonra birden fazla makine/personel için
	tek seferde puantaj kaydı oluşturur.
	"""
	data = json.loads(data)
	tarih = data.get("tarih")
	proje = data.get("proje")
	puantaj_tipi = data.get("puantaj_tipi")
	entries = data.get("entries", [])

	created = 0
	errors = []

	for entry in entries:
		try:
			if puantaj_tipi == "Makine Puantaj":
				doc = frappe.get_doc(
					{
						"doctype": "Makine Puantaj",
						"makine": entry.get("resource"),
						"tarih": tarih,
						"proje": proje,
						"operator": entry.get("operator"),
						"calisma_saati": entry.get("calisma_saati", 0),
						"yakit_tuketimi": entry.get("yakit_tuketimi", 0),
						"aciklama": entry.get("aciklama", ""),
					}
				)
			else:
				doc = frappe.get_doc(
					{
						"doctype": "Personel Puantaj",
						"personel": entry.get("resource"),
						"tarih": tarih,
						"proje": proje,
						"calisma_saati": entry.get("calisma_saati", 0),
						"mesai_saati": entry.get("mesai_saati", 0),
						"aciklama": entry.get("aciklama", ""),
					}
				)

			doc.insert()
			created += 1
		except Exception as e:
			resource_name = entry.get("resource", "?")
			errors.append(f"{resource_name}: {str(e)}")

	if created:
		frappe.db.commit()

	return {"created": created, "errors": errors}


@frappe.whitelist()
def get_makine_ozeti(makine):
	"""Makine detay sayfası için özet bilgiler (Requirement 1.5).

	Bakım geçmişi, puantaj özeti, yakıt tüketimi ve toplam maliyet.
	"""
	# Puantaj özeti
	puantaj = frappe.db.sql(
		"""
		SELECT COUNT(*) as toplam_gun, COALESCE(SUM(calisma_saati), 0) as toplam_saat
		FROM `tabMakine Puantaj`
		WHERE makine = %s
		""",
		makine,
		as_dict=True,
	)[0]

	# Yakıt tüketimi
	yakit = frappe.db.sql(
		"""
		SELECT COALESCE(SUM(miktar_litre), 0) as toplam_yakit,
		       COALESCE(SUM(toplam_tutar), 0) as yakit_maliyet
		FROM `tabYakit Kaydi`
		WHERE makine = %s
		""",
		makine,
		as_dict=True,
	)[0]

	# Bakım maliyeti
	bakim = frappe.db.sql(
		"""
		SELECT COUNT(*) as bakim_sayisi,
		       COALESCE(SUM(toplam_maliyet), 0) as bakim_maliyet
		FROM `tabBakim Kaydi`
		WHERE makine = %s
		""",
		makine,
		as_dict=True,
	)[0]

	toplam_maliyet = float(yakit.yakit_maliyet) + float(bakim.bakim_maliyet)

	return {
		"toplam_gun": puantaj.toplam_gun,
		"toplam_saat": float(puantaj.toplam_saat),
		"toplam_yakit": float(yakit.toplam_yakit),
		"yakit_maliyet": float(yakit.yakit_maliyet),
		"bakim_sayisi": bakim.bakim_sayisi,
		"bakim_maliyet": float(bakim.bakim_maliyet),
		"toplam_maliyet": toplam_maliyet,
	}


def hesapla_proje_kar_zarar(doc, method=None):
	"""Proje tamamlandığında kâr-zarar özeti hesaplar (Requirement 3.4).

	Project DocType'ının on_update hook'u olarak çalışır.
	Durum 'Completed' olduğunda hesaplama yapar.
	"""
	if doc.status != "Completed":
		return

	proje = doc.name

	# Makine hakediş geliri
	makine_hakedis = frappe.db.sql(
		"""
		SELECT COALESCE(SUM(toplam_tutar), 0)
		FROM `tabMakine Hakedis`
		WHERE proje = %s
		""",
		proje,
	)[0][0] or 0

	# Personel hakediş geliri
	personel_hakedis = frappe.db.sql(
		"""
		SELECT COALESCE(SUM(toplam_tutar), 0)
		FROM `tabPersonel Hakedis`
		WHERE proje = %s
		""",
		proje,
	)[0][0] or 0

	toplam_gelir = float(makine_hakedis) + float(personel_hakedis)

	# Bakım gideri
	bakim_gideri = frappe.db.sql(
		"""
		SELECT COALESCE(SUM(toplam_maliyet), 0)
		FROM `tabBakim Kaydi`
		WHERE proje = %s AND docstatus = 1
		""",
		proje,
	)[0][0] or 0

	# Yakıt gideri
	yakit_gideri = frappe.db.sql(
		"""
		SELECT COALESCE(SUM(yk.toplam_tutar), 0)
		FROM `tabYakit Kaydi` yk
		WHERE yk.makine IN (
			SELECT DISTINCT mp.makine FROM `tabMakine Puantaj` mp WHERE mp.proje = %s
		)
		""",
		proje,
	)[0][0] or 0

	# Personel gideri
	personel_gideri = float(personel_hakedis)

	toplam_gider = float(bakim_gideri) + float(yakit_gideri) + personel_gideri
	net_kar_zarar = toplam_gelir - toplam_gider

	# Custom field'ları güncelle
	frappe.db.set_value(
		"Project",
		proje,
		{
			"toplam_gelir": toplam_gelir,
			"toplam_gider": toplam_gider,
			"net_kar_zarar": net_kar_zarar,
		},
		update_modified=False,
	)
