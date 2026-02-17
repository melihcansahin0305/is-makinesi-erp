from frappe import _


def get_data(data):
	"""Proje detay sayfasına makine/personel atamaları, puantaj ve hakediş bağlantıları ekler."""
	data["transactions"].append(
		{
			"label": _("Makine Yönetimi"),
			"items": ["Makine Puantaj", "Makine Hakedis"],
		}
	)
	data["transactions"].append(
		{
			"label": _("Personel Yönetimi"),
			"items": ["Personel Puantaj", "Personel Hakedis"],
		}
	)
	data["transactions"].append(
		{
			"label": _("Bakım ve Yakıt"),
			"items": ["Bakim Kaydi"],
		}
	)
	return data
