from frappe import _


def get_data():
	return {
		"heatmap": True,
		"heatmap_message": _("Bu makineye ait puantaj kayıtlarına göre aktivite"),
		"fieldname": "makine",
		"non_standard_fieldnames": {},
		"transactions": [
			{
				"label": _("Puantaj"),
				"items": ["Makine Puantaj"],
			},
			{
				"label": _("Hakediş"),
				"items": ["Makine Hakedis"],
			},
			{
				"label": _("Bakım ve Yakıt"),
				"items": ["Bakim Kaydi", "Yakit Kaydi"],
			},
		],
	}
