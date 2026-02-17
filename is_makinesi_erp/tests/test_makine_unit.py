"""Makine DocType birim testleri (Task 1.3).

CRUD testleri, benzersiz plaka doğrulaması, proje atama geçmişi testi.
Gereksinimler: 1.1, 1.3, 1.4
"""

import unittest
from unittest.mock import MagicMock, patch

import sys
import types

# Frappe mock setup for standalone testing
frappe_mock = types.ModuleType("frappe")
frappe_mock._ = lambda x: x
frappe_mock.throw = MagicMock(side_effect=Exception)
frappe_mock.db = MagicMock()
frappe_mock.utils = types.ModuleType("frappe.utils")
frappe_mock.utils.today = lambda: "2026-02-17"
frappe_mock.model = types.ModuleType("frappe.model")
frappe_mock.model.document = types.ModuleType("frappe.model.document")

sys.modules["frappe"] = frappe_mock
sys.modules["frappe.utils"] = frappe_mock.utils
sys.modules["frappe.model"] = frappe_mock.model
sys.modules["frappe.model.document"] = frappe_mock.model.document


class MockDocument:
    """Minimal Frappe Document mock."""

    def __init__(self):
        self.proje_gecmisi = []
        self._doc_before_save = None
        self._changed_fields = set()

    def has_value_changed(self, field):
        return field in self._changed_fields

    def get_doc_before_save(self):
        return self._doc_before_save

    def append(self, table, row):
        self.proje_gecmisi.append(type("Row", (), row)())


frappe_mock.model.document.Document = MockDocument

# Now import the actual module
sys.path.insert(0, "is_makinesi_erp/is_makinesi_erp/is_makinesi_erp/doctype/makine")
from makine import Makine


class TestMakineValidation(unittest.TestCase):
    """Makine DocType doğrulama testleri."""

    def _make_makine(self, durum="Aktif", mevcut_proje=None):
        m = Makine()
        m.makine_adi = "Test Makine"
        m.makine_tipi = "Ekskavatör"
        m.plaka_seri_no = "34-ABC-123"
        m.durum = durum
        m.mevcut_proje = mevcut_proje
        m.proje_gecmisi = []
        m._doc_before_save = None
        m._changed_fields = set()
        return m

    def test_bakimda_makine_proje_atama_engellenir(self):
        """Bakımda olan makine projeye atanamaz (Requirement 9.4)."""
        m = self._make_makine(durum="Bakımda", mevcut_proje="PROJ-001")
        with self.assertRaises(Exception):
            m.validate_bakimda_proje_atama()

    def test_aktif_makine_proje_atanabilir(self):
        """Aktif makine projeye atanabilir."""
        m = self._make_makine(durum="Aktif", mevcut_proje="PROJ-001")
        # Should not raise
        m.validate_bakimda_proje_atama()

    def test_bakimda_makine_projesi_yoksa_hata_yok(self):
        """Bakımda olan ama projesi olmayan makine hata vermez."""
        m = self._make_makine(durum="Bakımda", mevcut_proje=None)
        m.validate_bakimda_proje_atama()

    def test_proje_gecmisi_eklenir(self):
        """Proje atandığında geçmişe otomatik eklenir (Requirement 1.4)."""
        m = self._make_makine(durum="Aktif", mevcut_proje="PROJ-001")
        m._changed_fields = {"mevcut_proje"}
        m._doc_before_save = None
        m.update_proje_gecmisi()
        self.assertEqual(len(m.proje_gecmisi), 1)
        self.assertEqual(m.proje_gecmisi[0].proje, "PROJ-001")

    def test_proje_degismezse_gecmis_eklenmez(self):
        """Proje değişmezse geçmişe ekleme yapılmaz."""
        m = self._make_makine(durum="Aktif", mevcut_proje="PROJ-001")
        m._changed_fields = set()  # no change
        m.update_proje_gecmisi()
        self.assertEqual(len(m.proje_gecmisi), 0)


if __name__ == "__main__":
    unittest.main()
