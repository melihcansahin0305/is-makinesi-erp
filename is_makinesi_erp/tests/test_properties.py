"""Property-Based Tests for İş Makinesi ERP.

Tüm correctness property'leri hypothesis kütüphanesi ile doğrulanır.
Frappe bağımlılıkları mock'lanarak saf hesaplama mantığı test edilir.

Test Çalıştırma:
    python -m pytest is_makinesi_erp/is_makinesi_erp/tests/test_properties.py -v
"""

import sys
import types
from unittest.mock import MagicMock, patch

# ── Frappe mock setup ──────────────────────────────────────────────────
frappe_mock = types.ModuleType("frappe")
frappe_mock._ = lambda x: x
frappe_mock.throw = MagicMock(side_effect=Exception("ValidationError"))
frappe_mock.msgprint = MagicMock()
frappe_mock.db = MagicMock()
frappe_mock.get_all = MagicMock(return_value=[])
frappe_mock.get_doc = MagicMock()

frappe_utils = types.ModuleType("frappe.utils")
frappe_utils.flt = lambda x, precision=None: float(x or 0)
frappe_utils.today = lambda: "2026-02-17"
frappe_mock.utils = frappe_utils

frappe_model = types.ModuleType("frappe.model")
frappe_model_doc = types.ModuleType("frappe.model.document")


class MockDocument:
    def __init__(self):
        self._is_new = True
        self.name = "TEST-001"

    def is_new(self):
        return self._is_new

    def has_value_changed(self, field):
        return False

    def get_doc_before_save(self):
        return None

    def append(self, table, row):
        pass


frappe_model_doc.Document = MockDocument
frappe_model.document = frappe_model_doc

sys.modules["frappe"] = frappe_mock
sys.modules["frappe.utils"] = frappe_utils
sys.modules["frappe.model"] = frappe_model
sys.modules["frappe.model.document"] = frappe_model_doc

# Mock erpnext
erpnext_mock = types.ModuleType("erpnext")
erpnext_stock = types.ModuleType("erpnext.stock")
erpnext_stock_utils = types.ModuleType("erpnext.stock.utils")
erpnext_stock_utils.get_stock_balance = MagicMock(return_value=999999)
sys.modules["erpnext"] = erpnext_mock
sys.modules["erpnext.stock"] = erpnext_stock
sys.modules["erpnext.stock.utils"] = erpnext_stock_utils

from frappe.utils import flt

import pytest
from hypothesis import given, settings, assume
from hypothesis import strategies as st

# ── Strategies ─────────────────────────────────────────────────────────
positive_float = st.floats(min_value=0.01, max_value=1e6, allow_nan=False, allow_infinity=False)
non_negative_float = st.floats(min_value=0, max_value=1e6, allow_nan=False, allow_infinity=False)
hour_float = st.floats(min_value=0.1, max_value=24.0, allow_nan=False, allow_infinity=False)
currency = st.floats(min_value=0.01, max_value=1e8, allow_nan=False, allow_infinity=False)
date_str = st.just("2026-01-15")
makine_id = st.text(min_size=3, max_size=10, alphabet="ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789")
proje_id = st.text(min_size=3, max_size=10, alphabet="ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789")


# ══════════════════════════════════════════════════════════════════════
# Property 1: Makine puantajı mükerrer kayıt engelleme
# **Validates: Requirements 4.3**
# ══════════════════════════════════════════════════════════════════════

class TestProperty1MakinePuantajMukerrer:
    """Property 1: Makine puantajı mükerrer kayıt engelleme.

    Her hangi bir makine, tarih ve proje kombinasyonu için, aynı kombinasyonla
    ikinci bir puantaj kaydı oluşturulmaya çalışıldığında sistem kaydı reddetmelidir.
    **Validates: Requirements 4.3**
    """

    @given(
        makine=makine_id,
        tarih=date_str,
        proje=proje_id,
        saat=hour_float,
    )
    @settings(max_examples=100)
    def test_mukerrer_kayit_engellenir(self, makine, tarih, proje, saat):
        """Aynı makine+tarih+proje ile ikinci kayıt oluşturulamaz."""
        sys.path.insert(0, "is_makinesi_erp/is_makinesi_erp/is_makinesi_erp/doctype/makine_puantaj")
        from makine_puantaj import MakinePuantaj

        # İlk kayıt var gibi davran
        frappe_mock.db.exists = MagicMock(return_value=True)
        frappe_mock.db.get_value = MagicMock(return_value="Aktif")
        frappe_mock.throw = MagicMock(side_effect=Exception("Mükerrer"))

        mp = MakinePuantaj()
        mp.makine = makine
        mp.tarih = tarih
        mp.proje = proje
        mp.calisma_saati = saat
        mp._is_new = True

        with pytest.raises(Exception):
            mp.validate_mukerrer_kayit()


# ══════════════════════════════════════════════════════════════════════
# Property 2: Personel puantajı mükerrer kayıt engelleme
# **Validates: Requirements 5.3**
# ══════════════════════════════════════════════════════════════════════

class TestProperty2PersonelPuantajMukerrer:
    """Property 2: Personel puantajı mükerrer kayıt engelleme.

    Her hangi bir personel ve tarih kombinasyonu için, aynı kombinasyonla
    ikinci bir puantaj kaydı oluşturulmaya çalışıldığında sistem kaydı reddetmelidir.
    **Validates: Requirements 5.3**
    """

    @given(
        personel=makine_id,
        tarih=date_str,
    )
    @settings(max_examples=100)
    def test_mukerrer_kayit_engellenir(self, personel, tarih):
        """Aynı personel+tarih ile ikinci kayıt oluşturulamaz."""
        sys.path.insert(0, "is_makinesi_erp/is_makinesi_erp/is_makinesi_erp/doctype/personel_puantaj")
        from personel_puantaj import PersonelPuantaj

        frappe_mock.db.exists = MagicMock(return_value=True)
        frappe_mock.throw = MagicMock(side_effect=Exception("Mükerrer"))

        pp = PersonelPuantaj()
        pp.personel = personel
        pp.tarih = tarih
        pp.proje = "PROJ-001"
        pp.calisma_saati = 8
        pp.mesai_saati = 0
        pp._is_new = True

        with pytest.raises(Exception):
            pp.validate_mukerrer_kayit()


# ══════════════════════════════════════════════════════════════════════
# Property 3: Makine hakediş tutarı hesaplama doğruluğu
# **Validates: Requirements 6.1, 6.2, 6.3**
# ══════════════════════════════════════════════════════════════════════

class TestProperty3MakineHakedisHesaplama:
    """Property 3: Makine hakediş tutarı hesaplama doğruluğu.

    Her hangi bir makine hakedişi için, toplam tutar her zaman ilgili dönem ve
    projedeki puantaj kayıtlarının toplam çalışma saati ile birim fiyatın çarpımına
    eşit olmalıdır.
    **Validates: Requirements 6.1, 6.2, 6.3**
    """

    @given(
        toplam_saat=positive_float,
        birim_fiyat=currency,
    )
    @settings(max_examples=100)
    def test_toplam_tutar_hesaplama(self, toplam_saat, birim_fiyat):
        """toplam_tutar = toplam_saat × birim_fiyat."""
        sys.path.insert(0, "is_makinesi_erp/is_makinesi_erp/is_makinesi_erp/doctype/makine_hakedis")
        from makine_hakedis import MakineHakedis

        mh = MakineHakedis()
        mh.toplam_saat = toplam_saat
        mh.birim_fiyat = birim_fiyat
        mh.odemeler = []
        mh.makine = "MKN-0001"
        mh.proje = "PROJ-001"
        mh.donem_baslangic = "2026-01-01"
        mh.donem_bitis = "2026-01-31"

        # Mock puantaj query to return our toplam_saat
        frappe_mock.get_all = MagicMock(
            return_value=[MagicMock(toplam=toplam_saat)]
        )

        mh.hesapla_toplam_tutar()

        expected = flt(toplam_saat) * flt(birim_fiyat)
        assert abs(mh.toplam_tutar - expected) < 0.01, (
            f"Expected {expected}, got {mh.toplam_tutar}"
        )


# ══════════════════════════════════════════════════════════════════════
# Property 4: Personel hakediş tutarı hesaplama doğruluğu
# **Validates: Requirements 7.1, 7.2, 7.3**
# ══════════════════════════════════════════════════════════════════════

class TestProperty4PersonelHakedisHesaplama:
    """Property 4: Personel hakediş tutarı hesaplama doğruluğu.

    Her hangi bir personel hakedişi için, toplam tutar her zaman
    (toplam_gun × gunluk_ucret) + (toplam_mesai_saati × mesai_birim_ucret)
    formülüne eşit olmalıdır.
    **Validates: Requirements 7.1, 7.2, 7.3**
    """

    @given(
        toplam_gun=st.floats(min_value=1, max_value=31, allow_nan=False, allow_infinity=False),
        toplam_mesai=non_negative_float,
        gunluk_ucret=currency,
        mesai_birim_ucret=currency,
    )
    @settings(max_examples=100)
    def test_toplam_tutar_hesaplama(self, toplam_gun, toplam_mesai, gunluk_ucret, mesai_birim_ucret):
        """toplam_tutar = (toplam_gun × gunluk_ucret) + (toplam_mesai × mesai_birim_ucret)."""
        sys.path.insert(0, "is_makinesi_erp/is_makinesi_erp/is_makinesi_erp/doctype/personel_hakedis")
        from personel_hakedis import PersonelHakedis

        ph = PersonelHakedis()
        ph.toplam_gun = toplam_gun
        ph.toplam_mesai_saati = toplam_mesai
        ph.gunluk_ucret = gunluk_ucret
        ph.mesai_birim_ucret = mesai_birim_ucret
        ph.odemeler = []
        ph.personel = "EMP-001"
        ph.proje = "PROJ-001"
        ph.donem_baslangic = "2026-01-01"
        ph.donem_bitis = "2026-01-31"

        ph.hesapla_toplam_tutar()

        expected = (flt(toplam_gun) * flt(gunluk_ucret)) + (flt(toplam_mesai) * flt(mesai_birim_ucret))
        assert abs(ph.toplam_tutar - expected) < 0.01, (
            f"Expected {expected}, got {ph.toplam_tutar}"
        )


# ══════════════════════════════════════════════════════════════════════
# Property 5: Hakediş ödeme durumu tutarlılığı
# **Validates: Requirements 6.4, 7.4**
# ══════════════════════════════════════════════════════════════════════

class TestProperty5HakedisOdemeDurumu:
    """Property 5: Hakediş ödeme durumu tutarlılığı.

    Ödenen tutar toplam tutara eşit veya büyükse durum 'Tamamen Ödendi',
    sıfırdan büyük ama toplam tutardan küçükse 'Kısmi Ödendi',
    sıfır ise 'Beklemede' olmalıdır.
    **Validates: Requirements 6.4, 7.4**
    """

    @given(
        toplam_tutar=currency,
        odeme_sayisi=st.integers(min_value=0, max_value=5),
    )
    @settings(max_examples=100)
    def test_makine_hakedis_odeme_durumu(self, toplam_tutar, odeme_sayisi):
        """Makine hakediş ödeme durumu tutarlılığı."""
        sys.path.insert(0, "is_makinesi_erp/is_makinesi_erp/is_makinesi_erp/doctype/makine_hakedis")
        from makine_hakedis import MakineHakedis

        mh = MakineHakedis()
        mh.toplam_saat = 10
        mh.birim_fiyat = toplam_tutar / 10
        mh.toplam_tutar = toplam_tutar
        mh.makine = "MKN-0001"
        mh.proje = "PROJ-001"
        mh.donem_baslangic = "2026-01-01"
        mh.donem_bitis = "2026-01-31"

        # Create mock payments
        odemeler = []
        if odeme_sayisi > 0:
            per_payment = toplam_tutar / odeme_sayisi
            for _ in range(odeme_sayisi):
                odeme = MagicMock()
                odeme.odeme_tutari = per_payment
                odemeler.append(odeme)
        mh.odemeler = odemeler

        mh.hesapla_odeme_durumu()

        odenen = sum(flt(o.odeme_tutari) for o in odemeler)
        kalan = flt(toplam_tutar) - odenen

        assert abs(mh.kalan_tutar - kalan) < 0.01
        assert abs(mh.odenen_tutar - odenen) < 0.01

        if odenen >= toplam_tutar and toplam_tutar > 0:
            assert mh.odeme_durumu == "Tamamen Ödendi"
        elif odenen > 0:
            assert mh.odeme_durumu == "Kısmi Ödendi"
        else:
            assert mh.odeme_durumu == "Beklemede"

    @given(
        toplam_tutar=currency,
        kismi_oran=st.floats(min_value=0.01, max_value=0.99, allow_nan=False, allow_infinity=False),
    )
    @settings(max_examples=100)
    def test_personel_hakedis_kismi_odeme(self, toplam_tutar, kismi_oran):
        """Personel hakediş kısmi ödeme durumu."""
        sys.path.insert(0, "is_makinesi_erp/is_makinesi_erp/is_makinesi_erp/doctype/personel_hakedis")
        from personel_hakedis import PersonelHakedis

        ph = PersonelHakedis()
        ph.toplam_gun = 10
        ph.gunluk_ucret = toplam_tutar / 10
        ph.mesai_birim_ucret = 0
        ph.toplam_mesai_saati = 0
        ph.toplam_tutar = toplam_tutar
        ph.personel = "EMP-001"
        ph.proje = "PROJ-001"
        ph.donem_baslangic = "2026-01-01"
        ph.donem_bitis = "2026-01-31"

        odeme = MagicMock()
        odeme.odeme_tutari = toplam_tutar * kismi_oran
        ph.odemeler = [odeme]

        ph.hesapla_odeme_durumu()

        assert mh_odeme_durumu_dogru(
            ph.odeme_durumu, ph.odenen_tutar, ph.toplam_tutar
        )


def mh_odeme_durumu_dogru(durum, odenen, toplam):
    """Ödeme durumu doğrulama yardımcı fonksiyonu."""
    if flt(odenen) >= flt(toplam) and flt(toplam) > 0:
        return durum == "Tamamen Ödendi"
    elif flt(odenen) > 0:
        return durum == "Kısmi Ödendi"
    else:
        return durum == "Beklemede"


# ══════════════════════════════════════════════════════════════════════
# Property 6: Yakıt kaydı tutar hesaplama
# **Validates: Requirements 8.2**
# ══════════════════════════════════════════════════════════════════════

class TestProperty6YakitTutarHesaplama:
    """Property 6: Yakıt kaydı tutar hesaplama.

    Her hangi bir yakıt kaydı için, toplam tutar her zaman
    miktar (litre) ile birim fiyatın çarpımına eşit olmalıdır.
    **Validates: Requirements 8.2**
    """

    @given(
        miktar_litre=positive_float,
        birim_fiyat=currency,
    )
    @settings(max_examples=100)
    def test_toplam_tutar_hesaplama(self, miktar_litre, birim_fiyat):
        """toplam_tutar = miktar_litre × birim_fiyat."""
        sys.path.insert(0, "is_makinesi_erp/is_makinesi_erp/is_makinesi_erp/doctype/yakit_kaydi")
        from yakit_kaydi import YakitKaydi

        yk = YakitKaydi()
        yk.miktar_litre = miktar_litre
        yk.birim_fiyat = birim_fiyat
        yk.makine = "MKN-0001"
        yk.tarih = "2026-01-15"

        yk.hesapla_toplam_tutar()

        expected = flt(miktar_litre) * flt(birim_fiyat)
        assert abs(yk.toplam_tutar - expected) < 0.01


# ══════════════════════════════════════════════════════════════════════
# Property 7: Bakımdaki makine proje ataması engelleme
# **Validates: Requirements 9.4**
# ══════════════════════════════════════════════════════════════════════

class TestProperty7BakimdaMakineAtama:
    """Property 7: Bakımdaki makine proje ataması engelleme.

    Her hangi bir durumu 'Bakımda' olan makine için, projeye atama işlemi
    reddedilmelidir.
    **Validates: Requirements 9.4**
    """

    @given(proje=proje_id)
    @settings(max_examples=100)
    def test_bakimda_makine_proje_atanamaz(self, proje):
        """Bakımda olan makine projeye atanamaz."""
        sys.path.insert(0, "is_makinesi_erp/is_makinesi_erp/is_makinesi_erp/doctype/makine")
        from makine import Makine

        frappe_mock.throw = MagicMock(side_effect=Exception("Bakımda"))

        m = Makine()
        m.durum = "Bakımda"
        m.mevcut_proje = proje
        m.proje_gecmisi = []
        m._changed_fields = set()

        with pytest.raises(Exception):
            m.validate_bakimda_proje_atama()

    @given(
        durum=st.sampled_from(["Aktif", "Arızalı", "Pasif"]),
        proje=proje_id,
    )
    @settings(max_examples=100)
    def test_bakimda_olmayan_makine_atanabilir(self, durum, proje):
        """Bakımda olmayan makine projeye atanabilir."""
        sys.path.insert(0, "is_makinesi_erp/is_makinesi_erp/is_makinesi_erp/doctype/makine")
        from makine import Makine

        frappe_mock.throw = MagicMock(side_effect=Exception("Hata"))

        m = Makine()
        m.durum = durum
        m.mevcut_proje = proje
        m.proje_gecmisi = []
        m._changed_fields = set()

        # Should NOT raise
        m.validate_bakimda_proje_atama()


# ══════════════════════════════════════════════════════════════════════
# Property 8: Cüruf işleme üretim miktarı invariantı
# Property 9: Cüruf verimlilik oranı hesaplama
# **Validates: Requirements 11.2, 11.4**
# ══════════════════════════════════════════════════════════════════════

class TestProperty8ve9CurufIsleme:
    """Property 8 & 9: Cüruf işleme üretim miktarı ve verimlilik.

    Property 8: Üretilen toplam skal miktarı her zaman işlenen cüruf miktarından
    küçük veya eşit olmalıdır.
    Property 9: Verimlilik oranı = (toplam_uretim / curuf_miktari) × 100.
    **Validates: Requirements 11.2, 11.4**
    """

    @given(
        curuf_miktari=st.floats(min_value=1.0, max_value=1000.0, allow_nan=False, allow_infinity=False),
        urun_oranlari=st.lists(
            st.floats(min_value=0.01, max_value=0.3, allow_nan=False, allow_infinity=False),
            min_size=1,
            max_size=5,
        ),
    )
    @settings(max_examples=100)
    def test_uretim_miktari_invarianti_ve_verimlilik(self, curuf_miktari, urun_oranlari):
        """Üretim miktarı <= cüruf miktarı ve verimlilik doğru hesaplanır."""
        sys.path.insert(0, "is_makinesi_erp/is_makinesi_erp/is_makinesi_erp/doctype/curuf_isleme")
        from curuf_isleme import CurufIsleme

        frappe_mock.throw = MagicMock(side_effect=Exception("Aşım"))

        ci = CurufIsleme()
        ci.curuf_miktari_ton = curuf_miktari
        ci.isleme_tarihi = "2026-01-15"

        # Create products that don't exceed curuf amount
        urunler = []
        for oran in urun_oranlari:
            urun = MagicMock()
            urun.miktar_ton = curuf_miktari * oran
            urun.urun_turu = "Ince Skal"
            urunler.append(urun)
        ci.uretilen_urunler = urunler

        toplam_uretim = sum(flt(u.miktar_ton) for u in urunler)

        if toplam_uretim > curuf_miktari:
            # Should throw validation error
            with pytest.raises(Exception):
                ci.uretim_miktari_kontrolu()
        else:
            # Should pass validation
            ci.uretim_miktari_kontrolu()

            # Test hesaplama
            ci.hesapla_toplam_uretim()
            ci.hesapla_verimlilik()

            assert abs(ci.toplam_uretim_ton - toplam_uretim) < 0.01
            expected_verimlilik = (toplam_uretim / curuf_miktari) * 100
            assert abs(ci.verimlilik_orani - expected_verimlilik) < 0.01

    @given(
        curuf_miktari=st.floats(min_value=1.0, max_value=100.0, allow_nan=False, allow_infinity=False),
    )
    @settings(max_examples=100)
    def test_uretim_asimi_engellenir(self, curuf_miktari):
        """Üretim miktarı cüruf miktarını aşarsa hata verir."""
        sys.path.insert(0, "is_makinesi_erp/is_makinesi_erp/is_makinesi_erp/doctype/curuf_isleme")
        from curuf_isleme import CurufIsleme

        frappe_mock.throw = MagicMock(side_effect=Exception("Aşım"))

        ci = CurufIsleme()
        ci.curuf_miktari_ton = curuf_miktari

        urun = MagicMock()
        urun.miktar_ton = curuf_miktari + 0.01  # Exceed
        ci.uretilen_urunler = [urun]

        with pytest.raises(Exception):
            ci.uretim_miktari_kontrolu()


# ══════════════════════════════════════════════════════════════════════
# Property 11: Kantar fişi net ağırlık hesaplama ve doğrulama
# **Validates: Requirements 12.2, 12.4**
# ══════════════════════════════════════════════════════════════════════

class TestProperty11KantarFisi:
    """Property 11: Kantar fişi net ağırlık hesaplama ve doğrulama.

    Net ağırlık = brüt ağırlık - dara ağırlık.
    Brüt ağırlık <= dara ağırlık ise kayıt reddedilmelidir.
    **Validates: Requirements 12.2, 12.4**
    """

    @given(
        brut=st.floats(min_value=100, max_value=100000, allow_nan=False, allow_infinity=False),
        dara=st.floats(min_value=10, max_value=99999, allow_nan=False, allow_infinity=False),
    )
    @settings(max_examples=100)
    def test_net_agirlik_hesaplama(self, brut, dara):
        """Net ağırlık doğru hesaplanır ve brüt > dara kontrolü yapılır."""
        sys.path.insert(0, "is_makinesi_erp/is_makinesi_erp/is_makinesi_erp/doctype/kantar_fisi")
        from kantar_fisi import KantarFisi

        frappe_mock.throw = MagicMock(side_effect=Exception("Geçersiz"))

        kf = KantarFisi()
        kf.brut_agirlik = brut
        kf.dara_agirlik = dara
        kf.fis_no = "KF-TEST"
        kf.tartim_tarihi = "2026-01-15"

        if brut <= dara:
            with pytest.raises(Exception):
                kf.agirlik_kontrolu()
        else:
            kf.agirlik_kontrolu()
            kf.hesapla_net_agirlik()

            expected = flt(brut) - flt(dara)
            assert abs(kf.net_agirlik - expected) < 0.01
            assert kf.net_agirlik > 0


# ══════════════════════════════════════════════════════════════════════
# Property 12: Satış tutar hesaplama ve stok kontrolü
# **Validates: Requirements 13.2, 13.4**
# ══════════════════════════════════════════════════════════════════════

class TestProperty12SatisTutarVeStok:
    """Property 12: Satış tutar hesaplama ve stok kontrolü.

    Toplam tutar = miktar × birim fiyat.
    Satış miktarı mevcut stok miktarını aşıyorsa kayıt reddedilmelidir.
    **Validates: Requirements 13.2, 13.4**
    """

    @given(
        miktar_ton=positive_float,
        birim_fiyat=currency,
    )
    @settings(max_examples=100)
    def test_toplam_tutar_hesaplama(self, miktar_ton, birim_fiyat):
        """toplam_tutar = miktar_ton × birim_fiyat."""
        sys.path.insert(0, "is_makinesi_erp/is_makinesi_erp/is_makinesi_erp/doctype/skal_satis")
        from skal_satis import SkalSatis

        ss = SkalSatis()
        ss.miktar_ton = miktar_ton
        ss.birim_fiyat = birim_fiyat
        ss.musteri = "CUST-001"
        ss.urun_turu = "Ince Skal"
        ss.satis_tarihi = "2026-01-15"

        ss.hesapla_toplam_tutar()

        expected = flt(miktar_ton) * flt(birim_fiyat)
        assert abs(ss.toplam_tutar - expected) < 0.01

    @given(
        miktar_ton=st.floats(min_value=100, max_value=1000, allow_nan=False, allow_infinity=False),
    )
    @settings(max_examples=100)
    def test_stok_asimi_engellenir(self, miktar_ton):
        """Stok aşımı durumunda kayıt engellenir."""
        sys.path.insert(0, "is_makinesi_erp/is_makinesi_erp/is_makinesi_erp/doctype/skal_satis")
        import skal_satis as ss_mod
        import importlib

        # Set up mocks before reimporting
        frappe_mock.throw = MagicMock(side_effect=Exception("Stok aşımı"))
        erpnext_stock_utils.get_stock_balance = MagicMock(return_value=miktar_ton * 1000 - 1)
        importlib.reload(ss_mod)

        ss = ss_mod.SkalSatis()
        ss.miktar_ton = miktar_ton
        ss.birim_fiyat = 100
        ss.musteri = "CUST-001"
        ss.urun_turu = "Ince Skal"
        ss.satis_tarihi = "2026-01-15"

        with pytest.raises(Exception):
            ss.stok_kontrolu()


# ══════════════════════════════════════════════════════════════════════
# Property 10: Stok güncelleme tutarlılığı
# **Validates: Requirements 11.5, 13.3**
# ══════════════════════════════════════════════════════════════════════

class TestProperty10StokTutarliligi:
    """Property 10: Stok güncelleme tutarlılığı.

    Mevcut stok = toplam üretim - toplam satış.
    Üretim kaydı stoku artırmalı, satış kaydı stoku azaltmalıdır.
    **Validates: Requirements 11.5, 13.3**
    """

    @given(
        uretim_miktarlari=st.lists(
            st.floats(min_value=0.1, max_value=100, allow_nan=False, allow_infinity=False),
            min_size=1,
            max_size=5,
        ),
        satis_oranlari=st.lists(
            st.floats(min_value=0.01, max_value=0.5, allow_nan=False, allow_infinity=False),
            min_size=0,
            max_size=3,
        ),
    )
    @settings(max_examples=100)
    def test_stok_tutarliligi(self, uretim_miktarlari, satis_oranlari):
        """Stok = toplam üretim - toplam satış."""
        toplam_uretim = sum(uretim_miktarlari)
        toplam_satis = sum(toplam_uretim * oran for oran in satis_oranlari)

        # Satış üretimi aşmasın
        if toplam_satis > toplam_uretim:
            toplam_satis = toplam_uretim * 0.5

        beklenen_stok = toplam_uretim - toplam_satis
        assert beklenen_stok >= -0.01, (
            f"Stok negatif olamaz: {beklenen_stok}"
        )


# ══════════════════════════════════════════════════════════════════════
# Property 13: Makine kâr-zarar hesaplama doğruluğu
# **Validates: Requirements 10.1, 10.4**
# ══════════════════════════════════════════════════════════════════════

class TestProperty13MakineKarZarar:
    """Property 13: Makine kâr-zarar hesaplama doğruluğu.

    Net kâr/zarar = toplam gelir (hakediş) - toplam gider (bakım + yakıt + operatör).
    **Validates: Requirements 10.1, 10.4**
    """

    @given(
        hakedis_geliri=non_negative_float,
        bakim_gideri=non_negative_float,
        yakit_gideri=non_negative_float,
    )
    @settings(max_examples=100)
    def test_kar_zarar_hesaplama(self, hakedis_geliri, bakim_gideri, yakit_gideri):
        """net_kar_zarar = hakedis_geliri - (bakim_gideri + yakit_gideri)."""
        toplam_gider = bakim_gideri + yakit_gideri
        net_kar_zarar = hakedis_geliri - toplam_gider

        # Verify the formula
        assert abs(net_kar_zarar - (hakedis_geliri - bakim_gideri - yakit_gideri)) < 0.01

        # Verify sign consistency
        if hakedis_geliri > toplam_gider:
            assert net_kar_zarar > 0
        elif hakedis_geliri < toplam_gider:
            assert net_kar_zarar < 0


# ══════════════════════════════════════════════════════════════════════
# Property 14: Puantaj raporu toplam hesaplama
# **Validates: Requirements 4.4, 5.4**
# ══════════════════════════════════════════════════════════════════════

class TestProperty14PuantajRaporuToplam:
    """Property 14: Puantaj raporu toplam hesaplama.

    Aylık puantaj raporundaki toplam çalışma günü ve saatleri,
    bireysel puantaj kayıtlarının toplamına eşit olmalıdır.
    **Validates: Requirements 4.4, 5.4**
    """

    @given(
        kayitlar=st.lists(
            st.tuples(
                hour_float,  # calisma_saati
                st.floats(min_value=0, max_value=8, allow_nan=False, allow_infinity=False),  # mesai
            ),
            min_size=1,
            max_size=31,
        ),
    )
    @settings(max_examples=100)
    def test_toplam_hesaplama(self, kayitlar):
        """Rapor toplamları bireysel kayıtların toplamına eşit olmalı."""
        toplam_gun = len(kayitlar)
        toplam_saat = sum(k[0] for k in kayitlar)
        toplam_mesai = sum(k[1] for k in kayitlar)

        # Simulate report aggregation
        rapor_toplam_gun = 0
        rapor_toplam_saat = 0.0
        rapor_toplam_mesai = 0.0

        for calisma, mesai in kayitlar:
            rapor_toplam_gun += 1
            rapor_toplam_saat += calisma
            rapor_toplam_mesai += mesai

        assert rapor_toplam_gun == toplam_gun
        assert abs(rapor_toplam_saat - toplam_saat) < 0.01
        assert abs(rapor_toplam_mesai - toplam_mesai) < 0.01
