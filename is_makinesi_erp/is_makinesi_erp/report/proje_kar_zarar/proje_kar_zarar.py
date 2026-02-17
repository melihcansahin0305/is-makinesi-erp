import frappe
from frappe import _


def execute(filters=None):
	columns = get_columns()
	data = get_data(filters)
	return columns, data


def get_columns():
	return [
		{
			"fieldname": "proje",
			"label": _("Proje"),
			"fieldtype": "Link",
			"options": "Project",
			"width": 180,
		},
		{
			"fieldname": "makine_hakedis",
			"label": _("Makine Hakediş"),
			"fieldtype": "Currency",
			"width": 140,
		},
		{
			"fieldname": "personel_hakedis",
			"label": _("Personel Hakediş"),
			"fieldtype": "Currency",
			"width": 140,
		},
		{
			"fieldname": "toplam_gelir",
			"label": _("Toplam Gelir"),
			"fieldtype": "Currency",
			"width": 140,
		},
		{
			"fieldname": "bakim_gideri",
			"label": _("Bakım Gideri"),
			"fieldtype": "Currency",
			"width": 130,
		},
		{
			"fieldname": "yakit_gideri",
			"label": _("Yakıt Gideri"),
			"fieldtype": "Currency",
			"width": 130,
		},
		{
			"fieldname": "personel_gideri",
			"label": _("Personel Gideri"),
			"fieldtype": "Currency",
			"width": 130,
		},
		{
			"fieldname": "toplam_gider",
			"label": _("Toplam Gider"),
			"fieldtype": "Currency",
			"width": 140,
		},
		{
			"fieldname": "net_kar_zarar",
			"label": _("Net Kâr/Zarar"),
			"fieldtype": "Currency",
			"width": 140,
		},
	]


def get_data(filters):
	conditions = ""
	if filters.get("proje"):
		conditions += " AND p.name = %(proje)s"

	projects = frappe.db.sql(
		"""
		SELECT p.name as proje
		FROM `tabProject` p
		WHERE 1=1 {conditions}
		ORDER BY p.name
	""".format(conditions=conditions),
		filters,
		as_dict=True,
	)

	data = []
	for project in projects:
		proje = project.proje
		date_filters = {}
		if filters.get("from_date"):
			date_filters["from_date"] = filters["from_date"]
		if filters.get("to_date"):
			date_filters["to_date"] = filters["to_date"]

		# Makine hakediş geliri
		mh_conditions = "WHERE mh.proje = %s"
		mh_params = [proje]
		if date_filters.get("from_date"):
			mh_conditions += " AND mh.donem_baslangic >= %s"
			mh_params.append(date_filters["from_date"])
		if date_filters.get("to_date"):
			mh_conditions += " AND mh.donem_bitis <= %s"
			mh_params.append(date_filters["to_date"])

		makine_hakedis = frappe.db.sql(
			"""
			SELECT COALESCE(SUM(mh.toplam_tutar), 0)
			FROM `tabMakine Hakedis` mh {conditions}
		""".format(conditions=mh_conditions),
			mh_params,
		)[0][0] or 0

		# Personel hakediş geliri
		ph_conditions = "WHERE ph.proje = %s"
		ph_params = [proje]
		if date_filters.get("from_date"):
			ph_conditions += " AND ph.donem_baslangic >= %s"
			ph_params.append(date_filters["from_date"])
		if date_filters.get("to_date"):
			ph_conditions += " AND ph.donem_bitis <= %s"
			ph_params.append(date_filters["to_date"])

		personel_hakedis = frappe.db.sql(
			"""
			SELECT COALESCE(SUM(ph.toplam_tutar), 0)
			FROM `tabPersonel Hakedis` ph {conditions}
		""".format(conditions=ph_conditions),
			ph_params,
		)[0][0] or 0

		toplam_gelir = makine_hakedis + personel_hakedis

		# Bakım gideri
		bk_conditions = "WHERE bk.proje = %s AND bk.docstatus = 1"
		bk_params = [proje]
		if date_filters.get("from_date"):
			bk_conditions += " AND bk.tarih >= %s"
			bk_params.append(date_filters["from_date"])
		if date_filters.get("to_date"):
			bk_conditions += " AND bk.tarih <= %s"
			bk_params.append(date_filters["to_date"])

		bakim_gideri = frappe.db.sql(
			"""
			SELECT COALESCE(SUM(bk.toplam_maliyet), 0)
			FROM `tabBakim Kaydi` bk {conditions}
		""".format(conditions=bk_conditions),
			bk_params,
		)[0][0] or 0

		# Yakıt gideri (proje bazında - makine puantajlarından proje eşleşmesi)
		yk_conditions = """
			WHERE yk.makine IN (
				SELECT DISTINCT mp.makine FROM `tabMakine Puantaj` mp WHERE mp.proje = %s
			)
		"""
		yk_params = [proje]
		if date_filters.get("from_date"):
			yk_conditions += " AND yk.tarih >= %s"
			yk_params.append(date_filters["from_date"])
		if date_filters.get("to_date"):
			yk_conditions += " AND yk.tarih <= %s"
			yk_params.append(date_filters["to_date"])

		yakit_gideri = frappe.db.sql(
			"""
			SELECT COALESCE(SUM(yk.toplam_tutar), 0)
			FROM `tabYakit Kaydi` yk {conditions}
		""".format(conditions=yk_conditions),
			yk_params,
		)[0][0] or 0

		# Personel gideri (personel hakedişleri gider olarak da sayılır)
		personel_gideri = personel_hakedis

		toplam_gider = bakim_gideri + yakit_gideri + personel_gideri
		net_kar_zarar = toplam_gelir - toplam_gider

		if toplam_gelir or toplam_gider:
			data.append(
				{
					"proje": proje,
					"makine_hakedis": makine_hakedis,
					"personel_hakedis": personel_hakedis,
					"toplam_gelir": toplam_gelir,
					"bakim_gideri": bakim_gideri,
					"yakit_gideri": yakit_gideri,
					"personel_gideri": personel_gideri,
					"toplam_gider": toplam_gider,
					"net_kar_zarar": net_kar_zarar,
				}
			)

	return data
