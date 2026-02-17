from frappe import _


def get_data(data):
	"""Personel detay sayfasına puantaj özeti ve hakediş geçmişi bağlantıları ekler."""
	data["transactions"].append(
		{
			"label": _("İş Makinesi ERP"),
			"items": ["Personel Puantaj", "Personel Hakedis"],
		}
	)
	return data
