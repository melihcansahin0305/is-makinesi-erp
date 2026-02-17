import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import today


class Makine(Document):
	def validate(self):
		self.validate_bakimda_proje_atama()
		self.update_proje_gecmisi()

	def validate_bakimda_proje_atama(self):
		"""Bakımda olan makine projeye atanamaz (Requirement 9.4)."""
		if self.durum == "Bakımda" and self.mevcut_proje:
			frappe.throw(_("Bakımda olan makine projeye atanamaz"))

	def update_proje_gecmisi(self):
		"""Proje atandığında geçmişe otomatik ekleme (Requirement 1.4)."""
		if not self.has_value_changed("mevcut_proje"):
			return

		# Önceki projenin bitiş tarihini güncelle
		old_proje = self.get_doc_before_save()
		if old_proje and old_proje.mevcut_proje:
			for row in self.proje_gecmisi:
				if row.proje == old_proje.mevcut_proje and not row.bitis_tarihi:
					row.bitis_tarihi = today()
					break

		# Yeni proje atandıysa geçmişe ekle
		if self.mevcut_proje:
			self.append("proje_gecmisi", {
				"proje": self.mevcut_proje,
				"baslangic_tarihi": today(),
			})
