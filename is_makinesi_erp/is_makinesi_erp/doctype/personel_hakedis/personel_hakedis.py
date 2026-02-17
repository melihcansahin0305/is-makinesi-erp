import frappe
from frappe.model.document import Document
from frappe.utils import flt


class PersonelHakedis(Document):
	def before_save(self):
		self.hesapla_toplam_gun_ve_mesai()
		self.hesapla_toplam_tutar()
		self.hesapla_odeme_durumu()

	def hesapla_toplam_gun_ve_mesai(self):
		"""Puantajlardan toplam çalışma günü ve mesai saati hesapla (Requirement 7.1)."""
		puantajlar = frappe.get_all(
			"Personel Puantaj",
			filters={
				"personel": self.personel,
				"proje": self.proje,
				"tarih": ["between", [self.donem_baslangic, self.donem_bitis]],
			},
			fields=["count(distinct tarih) as toplam_gun", "sum(mesai_saati) as toplam_mesai"],
		)
		if puantajlar:
			self.toplam_gun = flt(puantajlar[0].toplam_gun)
			self.toplam_mesai_saati = flt(puantajlar[0].toplam_mesai)
		else:
			self.toplam_gun = 0
			self.toplam_mesai_saati = 0

	def hesapla_toplam_tutar(self):
		"""toplam_tutar = (toplam_gun × gunluk_ucret) + (toplam_mesai_saati × mesai_birim_ucret) (Requirement 7.2)."""
		self.toplam_tutar = (flt(self.toplam_gun) * flt(self.gunluk_ucret)) + (
			flt(self.toplam_mesai_saati) * flt(self.mesai_birim_ucret)
		)

	def hesapla_odeme_durumu(self):
		"""Ödeme child table'dan odenen_tutar, kalan_tutar ve odeme_durumu hesapla (Requirement 7.4)."""
		self.odenen_tutar = sum(flt(odeme.odeme_tutari) for odeme in self.odemeler)
		self.kalan_tutar = flt(self.toplam_tutar) - flt(self.odenen_tutar)

		if flt(self.odenen_tutar) >= flt(self.toplam_tutar) and flt(self.toplam_tutar) > 0:
			self.odeme_durumu = "Tamamen Ödendi"
		elif flt(self.odenen_tutar) > 0:
			self.odeme_durumu = "Kısmi Ödendi"
		else:
			self.odeme_durumu = "Beklemede"
