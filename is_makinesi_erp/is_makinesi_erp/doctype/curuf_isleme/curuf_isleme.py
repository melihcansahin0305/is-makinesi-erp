import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt


class CurufIsleme(Document):
	def validate(self):
		self.uretim_miktari_kontrolu()

	def before_save(self):
		self.hesapla_toplam_uretim()
		self.hesapla_verimlilik()

	def on_submit(self):
		self.stok_girisi_olustur()

	def hesapla_toplam_uretim(self):
		"""Üretilen ürünlerin toplam miktarını hesaplar."""
		self.toplam_uretim_ton = sum(flt(row.miktar_ton) for row in self.uretilen_urunler)

	def hesapla_verimlilik(self):
		"""Verimlilik oranı = (toplam_uretim_ton / curuf_miktari_ton) × 100 (Requirement 11.4)."""
		if flt(self.curuf_miktari_ton):
			self.verimlilik_orani = (flt(self.toplam_uretim_ton) / flt(self.curuf_miktari_ton)) * 100
		else:
			self.verimlilik_orani = 0

	def uretim_miktari_kontrolu(self):
		"""Üretilen toplam skal miktarı işlenen cüruf miktarını aşamaz (Requirement 11.2)."""
		toplam = sum(flt(row.miktar_ton) for row in self.uretilen_urunler)
		if flt(toplam) > flt(self.curuf_miktari_ton):
			frappe.throw(_("Üretilen toplam skal miktarı işlenen cüruf miktarını aşamaz"))

	def stok_girisi_olustur(self):
		"""on_submit: Material Receipt tipinde Stock Entry oluşturur (Requirement 11.5)."""
		if not self.uretilen_urunler:
			return

		stock_entry = frappe.get_doc(
			{
				"doctype": "Stock Entry",
				"stock_entry_type": "Material Receipt",
				"posting_date": self.isleme_tarihi,
				"items": [
					{
						"item_code": row.urun_turu,
						"qty": flt(row.miktar_ton) * 1000,  # ton -> kg
						"t_warehouse": "Skal Deposu - IME",
						"uom": "Kg",
					}
					for row in self.uretilen_urunler
				],
			}
		)
		stock_entry.insert(ignore_permissions=True)
		stock_entry.submit()
