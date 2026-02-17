import frappe
from frappe import _
from frappe.model.document import Document


class MakinePuantaj(Document):
	def validate(self):
		self.validate_calisma_saati()
		self.validate_makine_durumu()
		self.validate_mukerrer_kayit()
		self.warn_kaynak_cakismasi()

	def validate_calisma_saati(self):
		"""Çalışma saati 0-24 arası olmalı (Requirement 4.1)."""
		if self.calisma_saati is not None:
			if self.calisma_saati <= 0 or self.calisma_saati > 24:
				frappe.throw(_("Çalışma saati 0 ile 24 arasında olmalıdır"))

	def validate_makine_durumu(self):
		"""Makine durumu Aktif olmalı (Requirement 4.2)."""
		if self.makine:
			durum = frappe.db.get_value("Makine", self.makine, "durum")
			if durum != "Aktif":
				frappe.throw(_("Sadece durumu 'Aktif' olan makineler için puantaj girişi yapılabilir"))

	def validate_mukerrer_kayit(self):
		"""Aynı makine + tarih + proje için mükerrer kayıt engelleme (Requirement 4.3)."""
		if self.makine and self.tarih and self.proje:
			filters = {
				"makine": self.makine,
				"tarih": self.tarih,
				"proje": self.proje,
			}
			if not self.is_new():
				filters["name"] = ("!=", self.name)

			if frappe.db.exists("Makine Puantaj", filters):
				frappe.throw(
					_("Bu makine için bu tarihte ve projede zaten puantaj kaydı mevcut")
				)

	def warn_kaynak_cakismasi(self):
		"""Aynı makine aynı tarihte farklı projede çalışıyorsa uyarı verir (Requirement 3.2)."""
		if self.makine and self.tarih and self.proje:
			filters = {
				"makine": self.makine,
				"tarih": self.tarih,
				"proje": ("!=", self.proje),
			}
			if not self.is_new():
				filters["name"] = ("!=", self.name)

			conflicting = frappe.db.get_all(
				"Makine Puantaj",
				filters=filters,
				fields=["proje"],
				limit=1,
			)
			if conflicting:
				frappe.msgprint(
					_("Uyarı: Bu makine {0} tarihinde {1} projesinde de kayıtlıdır").format(
						self.tarih, conflicting[0].proje
					),
					indicator="orange",
					alert=True,
				)
