import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt


class BakimKaydi(Document):
	def before_save(self):
		self.hesapla_parca_tutarlari()

	def on_submit(self):
		self.makine_durumu_guncelle()

	def hesapla_parca_tutarlari(self):
		"""Kullanılan parçaların tutar hesaplaması: tutar = miktar × birim_fiyat."""
		for row in self.kullanilan_parcalar:
			row.tutar = flt(row.miktar) * flt(row.birim_fiyat)

	def makine_durumu_guncelle(self):
		"""on_submit: makine durumunu 'Bakımda' olarak güncelle (Requirement 9.4)."""
		if self.bakim_tipi in ("Periyodik Bakım", "Arıza Onarımı"):
			frappe.db.set_value("Makine", self.makine, "durum", "Bakımda")
