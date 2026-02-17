import frappe
from frappe import _
from frappe.model.document import Document


class PersonelPuantaj(Document):
	def validate(self):
		self.validate_calisma_saati()
		self.validate_mukerrer_kayit()
		self.warn_kaynak_cakismasi()

	def validate_calisma_saati(self):
		"""Çalışma saati > 0 ve <= 24, çalışma + mesai <= 24 (Requirement 5.1)."""
		if self.calisma_saati is not None:
			if self.calisma_saati <= 0 or self.calisma_saati > 24:
				frappe.throw(_("Çalışma saati 0 ile 24 arasında olmalıdır"))

		mesai = self.mesai_saati or 0
		if self.calisma_saati is not None and (self.calisma_saati + mesai) > 24:
			frappe.throw(_("Çalışma saati ve mesai saati toplamı 24 saati aşamaz"))

	def validate_mukerrer_kayit(self):
		"""Aynı personel + tarih için mükerrer kayıt engelleme (Requirement 5.3)."""
		if self.personel and self.tarih:
			filters = {
				"personel": self.personel,
				"tarih": self.tarih,
			}
			if not self.is_new():
				filters["name"] = ("!=", self.name)

			if frappe.db.exists("Personel Puantaj", filters):
				frappe.throw(
					_("Bu personel için bu tarihte zaten puantaj kaydı mevcut")
				)

	def warn_kaynak_cakismasi(self):
		"""Aynı personel aynı tarihte farklı projede çalışıyorsa uyarı verir (Requirement 3.2)."""
		if self.personel and self.tarih and self.proje:
			filters = {
				"personel": self.personel,
				"tarih": self.tarih,
				"proje": ("!=", self.proje),
			}
			if not self.is_new():
				filters["name"] = ("!=", self.name)

			conflicting = frappe.db.get_all(
				"Personel Puantaj",
				filters=filters,
				fields=["proje"],
				limit=1,
			)
			if conflicting:
				frappe.msgprint(
					_("Uyarı: Bu personel {0} tarihinde {1} projesinde de kayıtlıdır").format(
						self.tarih, conflicting[0].proje
					),
					indicator="orange",
					alert=True,
				)
