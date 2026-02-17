import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt
from erpnext.stock.utils import get_stock_balance


class SkalSatis(Document):
	def validate(self):
		self.stok_kontrolu()

	def before_save(self):
		self.hesapla_toplam_tutar()

	def on_submit(self):
		self.stok_cikisi_olustur()

	def hesapla_toplam_tutar(self):
		"""Toplam tutar = miktar_ton × birim_fiyat (Requirement 13.2)."""
		self.toplam_tutar = flt(self.miktar_ton) * flt(self.birim_fiyat)

	def stok_kontrolu(self):
		"""Satış miktarı mevcut stok miktarını aşamaz (Requirement 13.4)."""
		miktar_kg = flt(self.miktar_ton) * 1000
		mevcut_stok = get_stock_balance(self.urun_turu, "Skal Deposu - IME")
		if miktar_kg > mevcut_stok:
			frappe.throw(_("Satış miktarı mevcut stok miktarını aşıyor"))

	def stok_cikisi_olustur(self):
		"""on_submit: Material Issue tipinde Stock Entry oluşturur (Requirement 13.3)."""
		stock_entry = frappe.get_doc(
			{
				"doctype": "Stock Entry",
				"stock_entry_type": "Material Issue",
				"posting_date": self.satis_tarihi,
				"items": [
					{
						"item_code": self.urun_turu,
						"qty": flt(self.miktar_ton) * 1000,
						"s_warehouse": "Skal Deposu - IME",
						"uom": "Kg",
					}
				],
			}
		)
		stock_entry.insert(ignore_permissions=True)
		stock_entry.submit()
