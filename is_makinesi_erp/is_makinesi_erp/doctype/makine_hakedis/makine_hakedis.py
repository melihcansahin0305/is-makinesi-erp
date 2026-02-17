import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt


class MakineHakedis(Document):
	def before_save(self):
		self.hesapla_toplam_saat()
		self.hesapla_toplam_tutar()
		self.hesapla_odeme_durumu()

	def hesapla_toplam_saat(self):
		"""Puantajlardan toplam çalışma saatini hesapla (Requirement 6.1)."""
		puantajlar = frappe.get_all(
			"Makine Puantaj",
			filters={
				"makine": self.makine,
				"proje": self.proje,
				"tarih": ["between", [self.donem_baslangic, self.donem_bitis]],
			},
			fields=["sum(calisma_saati) as toplam"],
		)
		self.toplam_saat = flt(puantajlar[0].toplam) if puantajlar else 0

	def hesapla_toplam_tutar(self):
		"""toplam_tutar = toplam_saat × birim_fiyat (Requirement 6.2)."""
		self.toplam_tutar = flt(self.toplam_saat) * flt(self.birim_fiyat)

	def hesapla_odeme_durumu(self):
		"""Ödeme child table'dan odenen_tutar, kalan_tutar ve odeme_durumu hesapla (Requirement 6.4)."""
		self.odenen_tutar = sum(flt(odeme.odeme_tutari) for odeme in self.odemeler)
		self.kalan_tutar = flt(self.toplam_tutar) - flt(self.odenen_tutar)

		if flt(self.odenen_tutar) >= flt(self.toplam_tutar) and flt(self.toplam_tutar) > 0:
			self.odeme_durumu = "Tamamen \u00d6dendi"
		elif flt(self.odenen_tutar) > 0:
			self.odeme_durumu = "K\u0131smi \u00d6dendi"
		else:
			self.odeme_durumu = "Beklemede"
