import frappe
from frappe import _


def execute(filters=None):
	rapor_tipi = filters.get("rapor_tipi", "Makine")
	if rapor_tipi == "Makine":
		columns = get_makine_columns()
		data = get_makine_data(filters)
	else:
		columns = get_personel_columns()
		data = get_personel_data(filters)
	return columns, data


def get_makine_columns():
	return [
		{
			"fieldname": "makine",
			"label": _("Makine"),
			"fieldtype": "Link",
			"options": "Makine",
			"width": 180,
		},
		{
			"fieldname": "makine_adi",
			"label": _("Makine Adı"),
			"fieldtype": "Data",
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
			"fieldname": "toplam_gun",
			"label": _("Toplam Gün"),
			"fieldtype": "Float",
			"width": 100,
		},
		{
			"fieldname": "toplam_saat",
			"label": _("Toplam Saat"),
			"fieldtype": "Float",
			"width": 100,
		},
	]


def get_personel_columns():
	return [
		{
			"fieldname": "personel",
			"label": _("Personel"),
			"fieldtype": "Link",
			"options": "Employee",
			"width": 180,
		},
		{
			"fieldname": "personel_adi",
			"label": _("Personel Adı"),
			"fieldtype": "Data",
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
			"fieldname": "toplam_gun",
			"label": _("Toplam Gün"),
			"fieldtype": "Float",
			"width": 100,
		},
		{
			"fieldname": "normal_saat",
			"label": _("Normal Saat"),
			"fieldtype": "Float",
			"width": 100,
		},
		{
			"fieldname": "mesai_saati",
			"label": _("Mesai Saati"),
			"fieldtype": "Float",
			"width": 100,
		},
	]


def get_makine_data(filters):
	conditions = "WHERE mp.tarih BETWEEN %(from_date)s AND %(to_date)s"
	if filters.get("makine"):
		conditions += " AND mp.makine = %(makine)s"
	if filters.get("proje"):
		conditions += " AND mp.proje = %(proje)s"

	return frappe.db.sql(
		"""
		SELECT
			mp.makine,
			m.makine_adi,
			mp.proje,
			COUNT(*) as toplam_gun,
			SUM(mp.calisma_saati) as toplam_saat
		FROM `tabMakine Puantaj` mp
		LEFT JOIN `tabMakine` m ON m.name = mp.makine
		{conditions}
		GROUP BY mp.makine, mp.proje
		ORDER BY mp.makine, mp.proje
	""".format(conditions=conditions),
		filters,
		as_dict=True,
	)


def get_personel_data(filters):
	conditions = "WHERE pp.tarih BETWEEN %(from_date)s AND %(to_date)s"
	if filters.get("personel"):
		conditions += " AND pp.personel = %(personel)s"
	if filters.get("proje"):
		conditions += " AND pp.proje = %(proje)s"

	return frappe.db.sql(
		"""
		SELECT
			pp.personel,
			e.employee_name as personel_adi,
			pp.proje,
			COUNT(*) as toplam_gun,
			SUM(pp.calisma_saati) as normal_saat,
			SUM(pp.mesai_saati) as mesai_saati
		FROM `tabPersonel Puantaj` pp
		LEFT JOIN `tabEmployee` e ON e.name = pp.personel
		{conditions}
		GROUP BY pp.personel, pp.proje
		ORDER BY pp.personel, pp.proje
	""".format(conditions=conditions),
		filters,
		as_dict=True,
	)
