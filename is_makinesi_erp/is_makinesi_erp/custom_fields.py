import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields


def setup_custom_fields():
	"""ERPNext Customer, Project ve Employee DocType'larına custom field'lar ekler."""
	custom_fields = {
		"Customer": [
			{
				"fieldname": "musteri_tipi",
				"label": "Müşteri Tipi",
				"fieldtype": "Select",
				"options": "\nSkal Alıcısı\nİşveren",
				"insert_after": "customer_type",
				"module": "Is Makinesi ERP",
			},
		],
		"Project": [
			{
				"fieldname": "proje_tipi",
				"label": "Proje Tipi",
				"fieldtype": "Select",
				"options": "\nTaşeron\nKendi İşi",
				"insert_after": "project_type",
				"module": "Is Makinesi ERP",
			},
			{
				"fieldname": "sozlesme_bedeli",
				"label": "Sözleşme Bedeli",
				"fieldtype": "Currency",
				"insert_after": "proje_tipi",
				"module": "Is Makinesi ERP",
			},
			{
				"fieldname": "lokasyon",
				"label": "Lokasyon",
				"fieldtype": "Data",
				"insert_after": "sozlesme_bedeli",
				"module": "Is Makinesi ERP",
			},
			{
				"fieldname": "kar_zarar_section",
				"label": "Kâr-Zarar Özeti",
				"fieldtype": "Section Break",
				"insert_after": "lokasyon",
				"module": "Is Makinesi ERP",
				"depends_on": "eval:doc.status=='Completed'",
			},
			{
				"fieldname": "toplam_gelir",
				"label": "Toplam Gelir",
				"fieldtype": "Currency",
				"insert_after": "kar_zarar_section",
				"read_only": 1,
				"module": "Is Makinesi ERP",
			},
			{
				"fieldname": "toplam_gider",
				"label": "Toplam Gider",
				"fieldtype": "Currency",
				"insert_after": "toplam_gelir",
				"read_only": 1,
				"module": "Is Makinesi ERP",
			},
			{
				"fieldname": "kar_zarar_cb",
				"fieldtype": "Column Break",
				"insert_after": "toplam_gider",
				"module": "Is Makinesi ERP",
			},
			{
				"fieldname": "net_kar_zarar",
				"label": "Net Kâr/Zarar",
				"fieldtype": "Currency",
				"insert_after": "kar_zarar_cb",
				"read_only": 1,
				"module": "Is Makinesi ERP",
			},
		],
		"Employee": [
			{
				"fieldname": "pozisyon_tipi",
				"label": "Pozisyon Tipi",
				"fieldtype": "Select",
				"options": "\nOperatör\nŞoför\nTeknisyen\nİdari",
				"insert_after": "designation",
				"module": "Is Makinesi ERP",
			},
			{
				"fieldname": "gunluk_ucret",
				"label": "Günlük Ücret",
				"fieldtype": "Currency",
				"insert_after": "pozisyon_tipi",
				"module": "Is Makinesi ERP",
			},
			{
				"fieldname": "ehliyet_bilgisi",
				"label": "Ehliyet/Sertifika Bilgisi",
				"fieldtype": "Small Text",
				"insert_after": "gunluk_ucret",
				"module": "Is Makinesi ERP",
			},
		],
	}
	create_custom_fields(custom_fields)
