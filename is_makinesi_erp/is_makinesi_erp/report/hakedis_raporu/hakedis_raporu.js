frappe.query_reports["Hakedis Raporu"] = {
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
			fieldname: "proje",
			label: __("Proje"),
			fieldtype: "Link",
			options: "Project",
		},
		{
			fieldname: "hakedis_tipi",
			label: __("Hakediş Tipi"),
			fieldtype: "Select",
			options: "Makine\nPersonel",
			default: "Makine",
			reqd: 1,
		},
	],
};
