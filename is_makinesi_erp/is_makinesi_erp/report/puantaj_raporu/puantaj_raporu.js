frappe.query_reports["Puantaj Raporu"] = {
	filters: [
		{
			fieldname: "from_date",
			label: __("Başlangıç Tarihi"),
			fieldtype: "Date",
			default: frappe.datetime.add_months(frappe.datetime.get_today(), -1),
			reqd: 1,
		},
		{
			fieldname: "to_date",
			label: __("Bitiş Tarihi"),
			fieldtype: "Date",
			default: frappe.datetime.get_today(),
			reqd: 1,
		},
		{
			fieldname: "rapor_tipi",
			label: __("Rapor Tipi"),
			fieldtype: "Select",
			options: "Makine\nPersonel",
			default: "Makine",
			reqd: 1,
		},
		{
			fieldname: "makine",
			label: __("Makine"),
			fieldtype: "Link",
			options: "Makine",
			depends_on: "eval:doc.rapor_tipi=='Makine'",
		},
		{
			fieldname: "personel",
			label: __("Personel"),
			fieldtype: "Link",
			options: "Employee",
			depends_on: "eval:doc.rapor_tipi=='Personel'",
		},
		{
			fieldname: "proje",
			label: __("Proje"),
			fieldtype: "Link",
			options: "Project",
		},
	],
};
