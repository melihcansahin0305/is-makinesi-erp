import frappe
from frappe import _


def execute(filters=None):
	columns = get_columns()
	data = get_data(filters)
	return columns, data


def get_columns():
	return [
		{
			"fieldname": "urun_turu",
			"label": _("Ürün Türü"),
			"fieldtype": "Link",
			"options": "Item",
			"width": 200,
		},
		{
			"fieldname": "toplam_uretim",
			"label": _("Toplam Üretim (Ton)"),
			"fieldtype": "Float",
			"width": 150,
		},
		{
			"fieldname": "toplam_satis",
			"label": _("Toplam Satış (Ton)"),
			"fieldtype": "Float",
			"width": 150,
		},
		{
			"fieldname": "mevcut_stok",
			"label": _("Mevcut Stok (Ton)"),
			"fieldtype": "Float",
			"width": 150,
		},
	]


def get_data(filters):
	# Get all skal product items from Curuf Isleme child table
	urun_turleri = frappe.db.sql(
		"""
		SELECT DISTINCT uu.urun_turu
		FROM `tabUretilen Urun` uu
		INNER JOIN `tabCuruf Isleme` ci ON ci.name = uu.parent
		WHERE ci.docstatus = 1
		ORDER BY uu.urun_turu
	""",
		as_dict=True,
	)

	# Also include items that have sales but no production
	satis_urunleri = frappe.db.sql(
		"""
		SELECT DISTINCT ss.urun_turu
		FROM `tabSkal Satis` ss
		WHERE ss.docstatus = 1
	""",
		as_dict=True,
	)

	all_items = set()
	for row in urun_turleri:
		all_items.add(row.urun_turu)
	for row in satis_urunleri:
		all_items.add(row.urun_turu)

	data = []
	for urun in sorted(all_items):
		# Toplam üretim
		toplam_uretim = frappe.db.sql(
			"""
			SELECT COALESCE(SUM(uu.miktar_ton), 0)
			FROM `tabUretilen Urun` uu
			INNER JOIN `tabCuruf Isleme` ci ON ci.name = uu.parent
			WHERE ci.docstatus = 1 AND uu.urun_turu = %s
		""",
			urun,
		)[0][0] or 0

		# Toplam satış
		toplam_satis = frappe.db.sql(
			"""
			SELECT COALESCE(SUM(ss.miktar_ton), 0)
			FROM `tabSkal Satis` ss
			WHERE ss.docstatus = 1 AND ss.urun_turu = %s
		""",
			urun,
		)[0][0] or 0

		mevcut_stok = toplam_uretim - toplam_satis

		data.append(
			{
				"urun_turu": urun,
				"toplam_uretim": toplam_uretim,
				"toplam_satis": toplam_satis,
				"mevcut_stok": mevcut_stok,
			}
		)

	return data
