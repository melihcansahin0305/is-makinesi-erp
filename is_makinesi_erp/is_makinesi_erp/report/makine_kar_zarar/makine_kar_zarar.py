import frappe
from frappe import _


def execute(filters=None):
	columns = get_columns()
	data = get_data(filters)
	return columns, data


def get_columns():
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
			"fieldname": "hakedis_geliri",
			"label": _("Hakediş Geliri"),
			"fieldtype": "Currency",
			"width": 150,
		},
		{
			"fieldname": "bakim_gideri",
			"label": _("Bakım Gideri"),
			"fieldtype": "Currency",
			"width": 150,
		},
		{
			"fieldname": "yakit_gideri",
			"label": _("Yakıt Gideri"),
			"fieldtype": "Currency",
			"width": 150,
		},
		{
			"fieldname": "toplam_gider",
			"label": _("Toplam Gider"),
			"fieldtype": "Currency",
			"width": 150,
		},
		{
			"fieldname": "net_kar_zarar",
			"label": _("Net Kâr/Zarar"),
			"fieldtype": "Currency",
			"width": 150,
		},
	]


def get_data(filters):
	conditions = ""
	if filters.get("makine"):
		conditions += " AND m.name = %(makine)s"

	# Get all machines
	machines = frappe.db.sql(
		"""
		SELECT m.name as makine, m.makine_adi
		FROM `tabMakine` m
		WHERE 1=1 {conditions}
		ORDER BY m.name
	""".format(conditions=conditions),
		filters,
		as_dict=True,
	)

	data = []
	for machine in machines:
		# Hakediş geliri
		hakedis_filters = {"makine": machine.makine}
		hakedis_conditions = "WHERE mh.makine = %(makine)s"
		if filters.get("from_date"):
			hakedis_conditions += " AND mh.donem_baslangic >= %(from_date)s"
			hakedis_filters["from_date"] = filters["from_date"]
		if filters.get("to_date"):
			hakedis_conditions += " AND mh.donem_bitis <= %(to_date)s"
			hakedis_filters["to_date"] = filters["to_date"]

		hakedis_geliri = frappe.db.sql(
			"""
			SELECT COALESCE(SUM(mh.toplam_tutar), 0) as toplam
			FROM `tabMakine Hakedis` mh
			{conditions}
		""".format(conditions=hakedis_conditions),
			hakedis_filters,
		)[0][0] or 0

		# Bakım gideri
		bakim_filters = {"makine": machine.makine}
		bakim_conditions = "WHERE bk.makine = %(makine)s AND bk.docstatus = 1"
		if filters.get("from_date"):
			bakim_conditions += " AND bk.tarih >= %(from_date)s"
			bakim_filters["from_date"] = filters["from_date"]
		if filters.get("to_date"):
			bakim_conditions += " AND bk.tarih <= %(to_date)s"
			bakim_filters["to_date"] = filters["to_date"]

		bakim_gideri = frappe.db.sql(
			"""
			SELECT COALESCE(SUM(bk.toplam_maliyet), 0) as toplam
			FROM `tabBakim Kaydi` bk
			{conditions}
		""".format(conditions=bakim_conditions),
			bakim_filters,
		)[0][0] or 0

		# Yakıt gideri
		yakit_filters = {"makine": machine.makine}
		yakit_conditions = "WHERE yk.makine = %(makine)s"
		if filters.get("from_date"):
			yakit_conditions += " AND yk.tarih >= %(from_date)s"
			yakit_filters["from_date"] = filters["from_date"]
		if filters.get("to_date"):
			yakit_conditions += " AND yk.tarih <= %(to_date)s"
			yakit_filters["to_date"] = filters["to_date"]

		yakit_gideri = frappe.db.sql(
			"""
			SELECT COALESCE(SUM(yk.toplam_tutar), 0) as toplam
			FROM `tabYakit Kaydi` yk
			{conditions}
		""".format(conditions=yakit_conditions),
			yakit_filters,
		)[0][0] or 0

		toplam_gider = bakim_gideri + yakit_gideri
		net_kar_zarar = hakedis_geliri - toplam_gider

		if hakedis_geliri or toplam_gider:
			data.append(
				{
					"makine": machine.makine,
					"makine_adi": machine.makine_adi,
					"hakedis_geliri": hakedis_geliri,
					"bakim_gideri": bakim_gideri,
					"yakit_gideri": yakit_gideri,
					"toplam_gider": toplam_gider,
					"net_kar_zarar": net_kar_zarar,
				}
			)

	return data
