"""
Hat Kodlamasi Backend - Birim Testleri
Köşe durumları, gecikme formülleri ve sinyal kodlama doğrulamaları
"""

import unittest
from hat_kodlamasi_backend import (
    HatKodlamasiBackend,
    KodlamaTipi,
    GecersizBitDizisiError,
    GecersizParametreError,
    GecersizKodlamaTipiError,
)


class TestBitDizisiDogrulama(unittest.TestCase):
    """Bit dizisi doğrulama - Edge cases"""

    def test_bos_bit_dizisi(self):
        """Boş bit dizisi kabul edilmeli mi?"""
        # Şu an kabul ediliyor, bu bir feature mı bug mı?
        backend = HatKodlamasiBackend("", "NRZ-L", 1000.0, 100.0, 2e8)
        self.assertEqual(backend.bit_sayisi, 0)
        self.assertEqual(backend.kodlanmis_diziyi_al(), "")

    def test_none_bit_dizisi(self):
        """None bit dizisi reddedilmeli"""
        with self.assertRaises(GecersizBitDizisiError):
            HatKodlamasiBackend(None, "NRZ-L", 1000.0, 100.0, 2e8)

    def test_gecersiz_karakterler(self):
        """0 ve 1 dışı karakterler reddedilmeli"""
        with self.assertRaises(GecersizBitDizisiError):
            HatKodlamasiBackend("10102", "NRZ-L", 1000.0, 100.0, 2e8)

    def test_sadece_birler(self):
        """Sadece 1'lerden oluşan dizi"""
        backend = HatKodlamasiBackend("1111", "NRZ-L", 1000.0, 100.0, 2e8)
        self.assertEqual(backend.kodlanmis_diziyi_al(), "HHHH")

    def test_sadece_sifirlar(self):
        """Sadece 0'lardan oluşan dizi"""
        backend = HatKodlamasiBackend("0000", "NRZ-L", 1000.0, 100.0, 2e8)
        self.assertEqual(backend.kodlanmis_diziyi_al(), "LLLL")


class TestParametreDogrulama(unittest.TestCase):
    """Pozitif parametre doğrulama - Sıfıra bölünme kontrolü"""

    def test_sifir_bit_hizi(self):
        """Sıfır bit hızı reddedilmeli - Sıfıra bölünme!"""
        with self.assertRaises(GecersizParametreError):
            HatKodlamasiBackend("1010", "NRZ-L", 0.0, 100.0, 2e8)

    def test_negatif_bit_hizi(self):
        """Negatif bit hızı reddedilmeli"""
        with self.assertRaises(GecersizParametreError):
            HatKodlamasiBackend("1010", "NRZ-L", -1000.0, 100.0, 2e8)

    def test_sifir_baglanti_uzunlugu(self):
        """Sıfır bağlantı uzunluğu reddedilmeli"""
        with self.assertRaises(GecersizParametreError):
            HatKodlamasiBackend("1010", "NRZ-L", 1000.0, 0.0, 2e8)

    def test_sifir_yayilma_hizi(self):
        """Sıfır yayılma hızı reddedilmeli - Sıfıra bölünme!"""
        with self.assertRaises(GecersizParametreError):
            HatKodlamasiBackend("1010", "NRZ-L", 1000.0, 100.0, 0.0)

    def test_cok_kucuk_degerler(self):
        """Çok küçük pozitif değerler kabul edilmeli"""
        # Float underflow testi
        backend = HatKodlamasiBackend("1", "NRZ-L", 1e-10, 1e-10, 1e-10)
        self.assertGreater(backend.iletim_gecikmesi(), 0)
        self.assertGreater(backend.yayilma_gecikmesi(), 0)

    def test_none_parametreler(self):
        """None parametreler reddedilmeli"""
        with self.assertRaises(GecersizParametreError):
            HatKodlamasiBackend("1010", "NRZ-L", None, 100.0, 2e8)


class TestKodlamaTuru(unittest.TestCase):
    """Kodlama türü çözümleme"""

    def test_gecerli_nrz_enum(self):
        """NRZ-L enum olarak"""
        backend = HatKodlamasiBackend("1010", KodlamaTipi.NRZ_L, 1000.0, 100.0, 2e8)
        self.assertEqual(backend.kodlama_turu, KodlamaTipi.NRZ_L)

    def test_gecerli_manchester_enum(self):
        """Manchester enum olarak"""
        backend = HatKodlamasiBackend("1010", KodlamaTipi.MANCHESTER, 1000.0, 100.0, 2e8)
        self.assertEqual(backend.kodlama_turu, KodlamaTipi.MANCHESTER)

    def test_nrz_string(self):
        """NRZ-L string olarak"""
        backend = HatKodlamasiBackend("1010", "NRZ-L", 1000.0, 100.0, 2e8)
        self.assertEqual(backend.kodlama_turu, KodlamaTipi.NRZ_L)

    def test_manchester_string(self):
        """Manchester string olarak"""
        backend = HatKodlamasiBackend("1010", "MANCHESTER", 1000.0, 100.0, 2e8)
        self.assertEqual(backend.kodlama_turu, KodlamaTipi.MANCHESTER)

    def test_alias_nrz(self):
        """NRZ alias'ları"""
        for alias in ["nrz-l", "nrzl", "nrz_l"]:
            backend = HatKodlamasiBackend("1010", alias, 1000.0, 100.0, 2e8)
            self.assertEqual(backend.kodlama_turu, KodlamaTipi.NRZ_L)

    def test_bos_kodlama_turu(self):
        """Boş kodlama türü reddedilmeli"""
        with self.assertRaises(GecersizKodlamaTipiError):
            HatKodlamasiBackend("1010", "", 1000.0, 100.0, 2e8)

    def test_whitespace_kodlama_turu(self):
        """Boşluklu kodlama türü temizlenmeli"""
        backend = HatKodlamasiBackend("1010", "  NRZ-L  ", 1000.0, 100.0, 2e8)
        self.assertEqual(backend.kodlama_turu, KodlamaTipi.NRZ_L)

    def test_gecersiz_kodlama_turu(self):
        """Geçersiz kodlama türü reddedilmeli"""
        with self.assertRaises(GecersizKodlamaTipiError):
            HatKodlamasiBackend("1010", "INVALID", 1000.0, 100.0, 2e8)

    def test_none_kodlama_turu(self):
        """None kodlama türü reddedilmeli"""
        with self.assertRaises(GecersizKodlamaTipiError):
            HatKodlamasiBackend("1010", None, 1000.0, 100.0, 2e8)


class TestNRZKodlama(unittest.TestCase):
    """NRZ-L sinyal kodlama algoritması"""

    def test_nrz_1_deger(self):
        """NRZ-L: 1 -> H"""
        backend = HatKodlamasiBackend("1", "NRZ-L", 1000.0, 100.0, 2e8)
        self.assertEqual(backend.kodlanmis_diziyi_al(), "H")

    def test_nrz_0_deger(self):
        """NRZ-L: 0 -> L"""
        backend = HatKodlamasiBackend("0", "NRZ-L", 1000.0, 100.0, 2e8)
        self.assertEqual(backend.kodlanmis_diziyi_al(), "L")

    def test_nrz_karisik(self):
        """NRZ-L: Karışık bit dizisi"""
        backend = HatKodlamasiBackend("1010", "NRZ-L", 1000.0, 100.0, 2e8)
        self.assertEqual(backend.kodlanmis_diziyi_al(), "HLHL")

    def test_nrz_bos(self):
        """NRZ-L: Boş dizi"""
        backend = HatKodlamasiBackend("", "NRZ-L", 1000.0, 100.0, 2e8)
        self.assertEqual(backend.kodlanmis_diziyi_al(), "")


class TestManchesterKodlama(unittest.TestCase):
    """Manchester sinyal kodlama algoritması"""

    def test_manchester_1_deger(self):
        """Manchester: 1 -> HL"""
        backend = HatKodlamasiBackend("1", "MANCHESTER", 1000.0, 100.0, 2e8)
        self.assertEqual(backend.kodlanmis_diziyi_al(), "HL")

    def test_manchester_0_deger(self):
        """Manchester: 0 -> LH"""
        backend = HatKodlamasiBackend("0", "MANCHESTER", 1000.0, 100.0, 2e8)
        self.assertEqual(backend.kodlanmis_diziyi_al(), "LH")

    def test_manchester_karisik(self):
        """Manchester: Karışık bit dizisi"""
        backend = HatKodlamasiBackend("10", "MANCHESTER", 1000.0, 100.0, 2e8)
        self.assertEqual(backend.kodlanmis_diziyi_al(), "HLLH")

    def test_manchester_sembol_sayisi(self):
        """Manchester: Her bit 2 sembol olmalı"""
        backend = HatKodlamasiBackend("1010", "MANCHESTER", 1000.0, 100.0, 2e8)
        self.assertEqual(backend.toplam_sembol_sayisi(), 8)
        self.assertEqual(backend.bit_sayisi, 4)

    def test_manchester_bos(self):
        """Manchester: Boş dizi"""
        backend = HatKodlamasiBackend("", "MANCHESTER", 1000.0, 100.0, 2e8)
        self.assertEqual(backend.kodlanmis_diziyi_al(), "")


class TestGecisSayisi(unittest.TestCase):
    """Geçiş sayısı hesaplama - Mantık kontrolü"""

    def test_nrz_hic_gecis_yok(self):
        """NRZ-L: Aynı seviyeler arasında geçiş yok"""
        backend = HatKodlamasiBackend("1111", "NRZ-L", 1000.0, 100.0, 2e8)
        self.assertEqual(backend.gecis_sayisi(), 0)

    def test_nrz_surekli_gecis(self):
        """NRZ-L: Sürekli değişim"""
        backend = HatKodlamasiBackend("1010", "NRZ-L", 1000.0, 100.0, 2e8)
        self.assertEqual(backend.gecis_sayisi(), 3)  # H-L-H-L -> 3 geçiş

    def test_nrz_tek_gecis(self):
        """NRZ-L: Tek geçiş"""
        backend = HatKodlamasiBackend("111000", "NRZ-L", 1000.0, 100.0, 2e8)
        self.assertEqual(backend.gecis_sayisi(), 1)

    def test_manchester_her_bit_gecis(self):
        """Manchester: Her bit içinde zaten 1 geçiş var (HL veya LH)"""
        backend = HatKodlamasiBackend("11", "MANCHESTER", 1000.0, 100.0, 2e8)
        # "HLHL" -> H-L (geçiş), L-H (geçiş), H-L (geçiş) = 3 geçiş
        self.assertEqual(backend.gecis_sayisi(), 3)

    def test_manchester_00_pattern(self):
        """Manchester: 00 -> LHLH"""
        backend = HatKodlamasiBackend("00", "MANCHESTER", 1000.0, 100.0, 2e8)
        # LHLH -> L-H, H-L, L-H = 3 geçiş
        self.assertEqual(backend.gecis_sayisi(), 3)

    def test_bos_dizi_gecis(self):
        """Boş dizi: 0 geçiş"""
        backend = HatKodlamasiBackend("", "NRZ-L", 1000.0, 100.0, 2e8)
        self.assertEqual(backend.gecis_sayisi(), 0)

    def test_tek_bit_gecis(self):
        """Tek bit: 0 geçiş (komşu yok)"""
        backend = HatKodlamasiBackend("1", "NRZ-L", 1000.0, 100.0, 2e8)
        self.assertEqual(backend.gecis_sayisi(), 0)


class TestGecisYogunlugu(unittest.TestCase):
    """Geçiş yoğunluğu hesaplama - Sıfıra bölünme kontrolü"""

    def test_yogunluk_nrz(self):
        """NRZ-L geçiş yoğunluğu"""
        backend = HatKodlamasiBackend("1010", "NRZ-L", 1000.0, 100.0, 2e8)
        # 3 geçiş / 4 bit = 0.75
        self.assertEqual(backend.gecis_yogunlugu_bit_basina(), 0.75)

    def test_yogunluk_manchester(self):
        """Manchester geçiş yoğunluğu"""
        backend = HatKodlamasiBackend("11", "MANCHESTER", 1000.0, 100.0, 2e8)
        # 3 geçiş / 2 bit = 1.5
        self.assertEqual(backend.gecis_yogunlugu_bit_basina(), 1.5)

    def test_yogunluk_bos_dizi(self):
        """Boş dizi: 0.0 (sıfıra bölme koruması)"""
        backend = HatKodlamasiBackend("", "NRZ-L", 1000.0, 100.0, 2e8)
        self.assertEqual(backend.gecis_yogunlugu_bit_basina(), 0.0)


class TestGecikmeFormulleri(unittest.TestCase):
    """Gecikme formülleri - Float/Integer bölme doğruluğu"""

    def test_iletim_gecikmesi_formulu(self):
        """Transmission delay: n / R"""
        backend = HatKodlamasiBackend("1010", "NRZ-L", 1000.0, 100.0, 2e8)
        # n = 4, R = 1000 -> 4/1000 = 0.004 saniye
        self.assertAlmostEqual(backend.iletim_gecikmesi(), 0.004, places=6)

    def test_yayilma_gecikmesi_formulu(self):
        """Propagation delay: d / v"""
        backend = HatKodlamasiBackend("1010", "NRZ-L", 1000.0, 100.0, 2e8)
        # d = 100, v = 2e8 -> 100/2e8 = 5e-7 saniye
        self.assertAlmostEqual(backend.yayilma_gecikmesi(), 5e-7, places=10)

    def test_toplam_gecikme(self):
        """Toplam gecikme: iletim + yayılma"""
        backend = HatKodlamasiBackend("1010", "NRZ-L", 1000.0, 100.0, 2e8)
        expected = 0.004 + 5e-7
        self.assertAlmostEqual(backend.tek_yonlu_toplam_gecikme(), expected, places=6)

    def test_iletim_birim_kontrol(self):
        """İletim gecikmesi birimleri doğru mu?"""
        # R = bits per second, n = bits -> saniye
        backend = HatKodlamasiBackend("1000000", "NRZ-L", 1e6, 100.0, 2e8)
        # 7 bit / 1Mbps = 7 mikrosaniye (7e-6 saniye)
        self.assertAlmostEqual(backend.iletim_gecikmesi(), 7e-6, places=10)

    def test_float_bolme_dogrulugu(self):
        """Float bölme hassasiyeti"""
        backend = HatKodlamasiBackend("1", "NRZ-L", 3.0, 1.0, 3.0)
        # 1/3 -> 0.333333...
        self.assertAlmostEqual(backend.iletim_gecikmesi(), 1/3, places=10)
        self.assertAlmostEqual(backend.yayilma_gecikmesi(), 1/3, places=10)


class TestEntegrasyon(unittest.TestCase):
    """Tam senaryo testleri"""

    def test_tam_senaryo_nrz(self):
        """Tam senaryo: NRZ-L"""
        backend = HatKodlamasiBackend("101100", "NRZ-L", 1000.0, 50.0, 2e8)
        self.assertEqual(backend.bit_sayisi, 6)
        self.assertEqual(backend.kodlanmis_diziyi_al(), "HLHHLL")
        # H-L(1), L-H(2), H-H(yok), H-L(3), L-L(yok) = 3 geçiş
        self.assertEqual(backend.gecis_sayisi(), 3)
        self.assertAlmostEqual(backend.gecis_yogunlugu_bit_basina(), 3/6, places=6)
        self.assertAlmostEqual(backend.iletim_gecikmesi(), 6/1000, places=6)
        self.assertAlmostEqual(backend.yayilma_gecikmesi(), 50/2e8, places=10)

    def test_tam_senaryo_manchester(self):
        """Tam senaryo: Manchester"""
        backend = HatKodlamasiBackend("10", "MANCHESTER", 1000.0, 100.0, 2e8)
        self.assertEqual(backend.bit_sayisi, 2)
        self.assertEqual(backend.kodlanmis_diziyi_al(), "HLLH")
        self.assertEqual(backend.toplam_sembol_sayisi(), 4)
        # H-L(1), L-L(yok), L-H(2) = 2 geçiş (bit sınırında geçiş yok)
        self.assertEqual(backend.gecis_sayisi(), 2)
        self.assertEqual(backend.gecis_yogunlugu_bit_basina(), 2/2)


if __name__ == "__main__":
    unittest.main(verbosity=2)
