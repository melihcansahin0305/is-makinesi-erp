import frappe
from frappe import _


def execute(filters=None):
	hakedis_tipi = filters.get("hakedis_tipi", "Makine")
	if hakedis_tipi == "Makine":
		columns = get_makine_columns()
		data = get_makine_data(filters)
	else:
		columns = get_personel_columns()
		data = get_personel_data(filters)
	return columns, data


def get_makine_columns():
	return [
		{
			"fieldname": "hakedis_no",
			"label": _("Hakediş No"),
			"fieldtype": "Link",
			"options": "Makine Hakedis",
			"width": 150,
		},
		{
			"fieldname": "makine",
			"label": _("Makine"),
			"fieldtype": "Link",
			"options": "Makine",
			"width": 150,
		},
		{
			"fieldname": "proje",
			"label": _("Proje"),
			"fieldtype": "Link",
			"options": "Project",
			"width": 150,
		},
		{
			"fieldname": "donem",
			"label": _("Dönem"),
			"fieldtype": "Data",
			"width": 180,
		},
		{
			"fieldname": "toplam_tutar",
			"label": _("Toplam Tutar"),
			"fieldtype": "Currency",
			"width": 130,
		},
		{
			"fieldname": "odenen_tutar",
			"label": _("Ödenen"),
			"fieldtype": "Currency",
			"width": 130,
		},
		{
			"fieldname": "kalan_tutar",
			"label": _("Kalan"),
			"fieldtype": "Currency",
			"width": 130,
		},
		{
			"fieldname": "odeme_durumu",
			"label": _("Durum"),
			"fieldtype": "Data",
			"width": 120,
		},
	]


def get_personel_columns():
	return [
		{
			"fieldname": "hakedis_no",
			"label": _("Hakediş No"),
			"fieldtype": "Link",
			"options": "Personel Hakedis",
			"width": 150,
		},
		{
			"fieldname": "personel",
			"label": _("Personel"),
			"fieldtype": "Link",
			"options": "Employee",
			"width": 150,
		},
		{
			"fieldname": "proje",
			"label": _("Proje"),
			"fieldtype": "Link",
			"options": "Project",
			"width": 150,
		},
		{
			"fieldname": "donem",
			"label": _("Dönem"),
			"fieldtype": "Data",
			"width": 180,
		},
		{
			"fieldname": "toplam_tutar",
			"label": _("Toplam Tutar"),
			"fieldtype": "Currency",
			"width": 130,
		},
		{
			"fieldname": "odenen_tutar",
			"label": _("Ödenen"),
			"fieldtype": "Currency",
			"width": 130,
		},
		{
			"fieldname": "kalan_tutar",
			"label": _("Kalan"),
			"fieldtype": "Currency",
			"width": 130,
		},
		{
			"fieldname": "odeme_durumu",
			"label": _("Durum"),
			"fieldtype": "Data",
			"width": 120,
		},
	]


def get_makine_data(filters):
	conditions = "WHERE mh.donem_baslangic >= %(from_date)s AND mh.donem_bitis <= %(to_date)s"
	if filters.get("proje"):
		conditions += " AND mh.proje = %(proje)s"

	rows = frappe.db.sql(
		"""
		SELECT
			mh.name as hakedis_no,
			mh.makine,
			mh.proje,
			mh.donem_baslangic,
			mh.donem_bitis,
			mh.toplam_tutar,
			mh.odenen_tutar,
			mh.kalan_tutar,
			mh.odeme_durumu
		FROM `tabMakine Hakedis` mh
		{conditions}
		ORDER BY mh.donem_baslangic DESC
	""".format(conditions=conditions),
		filters,
		as_dict=True,
	)

	for row in rows:
		row["donem"] = "{0} - {1}".format(
			frappe.format(row.pop("donem_baslangic"), {"fieldtype": "Date"}),
			frappe.format(row.pop("donem_bitis"), {"fieldtype": "Date"}),
		)

	return rows


def get_personel_data(filters):
	conditions = "WHERE ph.donem_baslangic >= %(from_date)s AND ph.donem_bitis <= %(to_date)s"
	if filters.get("proje"):
		conditions += " AND ph.proje = %(proje)s"

	rows = frappe.db.sql(
		"""
		SELECT
			ph.name as hakedis_no,
			ph.personel,
			ph.proje,
			ph.donem_baslangic,
			ph.donem_bitis,
			ph.toplam_tutar,
			ph.odenen_tutar,
			ph.kalan_tutar,
			ph.odeme_durumu
		FROM `tabPersonel Hakedis` ph
		{conditions}
		ORDER BY ph.donem_baslangic DESC
	""".format(conditions=conditions),
		filters,
		as_dict=True,
	)

	for row in rows:
		row["donem"] = "{0} - {1}".format(
			frappe.format(row.pop("donem_baslangic"), {"fieldtype": "Date"}),
			frappe.format(row.pop("donem_bitis"), {"fieldtype": "Date"}),
		)

	return rows
