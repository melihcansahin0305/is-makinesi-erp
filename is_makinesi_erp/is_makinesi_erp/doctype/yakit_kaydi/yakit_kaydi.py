import frappe
from frappe.model.document import Document
from frappe.utils import flt


class YakitKaydi(Document):
	def before_save(self):
		self.hesapla_toplam_tutar()

	def hesapla_toplam_tutar(self):
		"""toplam_tutar = miktar_litre × birim_fiyat (Requirement 8.2)."""
		self.toplam_tutar = flt(self.miktar_litre) * flt(self.birim_fiyat)
