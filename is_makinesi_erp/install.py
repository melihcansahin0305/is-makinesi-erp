from is_makinesi_erp.setup.setup_items import create_skal_items
from is_makinesi_erp.is_makinesi_erp.custom_fields import setup_custom_fields


def after_install():
	"""Uygulama kurulumu sonrası skal ürünlerini ve custom field'ları oluşturur."""
	create_skal_items()
	setup_custom_fields()
