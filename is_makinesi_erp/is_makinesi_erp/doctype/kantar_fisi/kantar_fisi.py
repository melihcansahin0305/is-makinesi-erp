import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt


class KantarFisi(Document):
	def validate(self):
		self.agirlik_kontrolu()

	def before_save(self):
		self.hesapla_net_agirlik()

	def agirlik_kontrolu(self):
		"""Brüt ağırlık dara ağırlığından büyük olmalıdır (Requirement 12.4)."""
		if flt(self.brut_agirlik) <= flt(self.dara_agirlik):
			frappe.throw(_("Brüt ağırlık dara ağırlığından büyük olmalıdır"))

	def hesapla_net_agirlik(self):
		"""Net ağırlık = brüt ağırlık - dara ağırlık (Requirement 12.2)."""
		self.net_agirlik = flt(self.brut_agirlik) - flt(self.dara_agirlik)
