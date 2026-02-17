from frappe import _


def get_data(data):
	"""Müşteri detay sayfasına satış geçmişi ve kantar fişleri bağlantısı ekler."""
	data["transactions"].append(
		{
			"label": _("İş Makinesi ERP"),
			"items": ["Skal Satis", "Kantar Fisi"],
		}
	)
	return data
