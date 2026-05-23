from __future__ import annotations

from enum import Enum
from typing import Union


class HatKodlamasiError(Exception):
    """Hat kodlama ve gecikme hesapları için temel istisna."""


class GecersizBitDizisiError(HatKodlamasiError):
    """Bit dizisi yalnızca '0' ve '1' içermelidir."""


class GecersizParametreError(HatKodlamasiError):
    """R, d veya v pozitif olmalıdır."""


class GecersizKodlamaTipiError(HatKodlamasiError):
    """Desteklenmeyen kodlama türü."""


class KodlamaTipi(str, Enum):
    """Desteklenen hat kodlama türleri."""

    NRZ_L = "NRZ-L"
    MANCHESTER = "MANCHESTER"


class HatKodlamasiBackend:
    """
    NRZ-L ve Manchester hat kodlaması, tek yönlü gecikme ve geçiş analizi.

    - NRZ-L: 1 -> H, 0 -> L
    - Manchester: 1 -> HL (önce yüksek, sonra düşük), 0 -> LH
    - Transmission delay: n / R (n: bit sayısı, R: bit hızı)
    - Propagation delay: d / v (d: bağlantı uzunluğu, v: yayılma hızı)
    """

    _KODLAMA_ALIAS = {
        "nrz-l": KodlamaTipi.NRZ_L,
        "nrzl": KodlamaTipi.NRZ_L,
        "nrz_l": KodlamaTipi.NRZ_L,
        "manchester": KodlamaTipi.MANCHESTER,
    }

    def __init__(
        self,
        bit_dizisi: str,
        kodlama_turu: Union[KodlamaTipi, str],
        bit_hizi_R: float,
        baglanti_uzunlugu_d: float,
        yayilma_hizi_v: float,
    ) -> None:
        self._bit_dizisi = self._dogrula_bit_dizisi(bit_dizisi)
        self._kodlama = self._cozumle_kodlama_turu(kodlama_turu)
        self._R = self._dogrula_pozitif(bit_hizi_R, "bit_hizi_R")
        self._d = self._dogrula_pozitif(baglanti_uzunlugu_d, "baglanti_uzunlugu_d")
        self._v = self._dogrula_pozitif(yayilma_hizi_v, "yayilma_hizi_v")

        self._n = len(self._bit_dizisi)
        self._kodlanmis = self._kodla(self._bit_dizisi, self._kodlama)

    @property
    def bit_sayisi(self) -> int:
        return self._n

    @property
    def kodlama_turu(self) -> KodlamaTipi:
        return self._kodlama

    def kodlanmis_diziyi_al(self) -> str:
        """Seviye dizisi: 'H' ve 'L' karakterleri (Manchester'ta bit başına 2 sembol)."""
        return self._kodlanmis

    def toplam_sembol_sayisi(self) -> int:
        """Kodlanmış dizideki toplam sembol (H/L) sayısı."""
        return len(self._kodlanmis)

    def gecis_sayisi(self) -> int:
        """Komşu semboller arasında H<->L geçiş sayısı."""
        if self._n == 0:
            return 0
        s = self._kodlanmis
        return sum(1 for i in range(1, len(s)) if s[i] != s[i - 1])

    def gecis_yogunlugu_bit_basina(self) -> float:
        """
        Sinyal geçiş yoğunluğu: geçiş sayısı / bit sayısı.
        Bit yoksa 0.0 döner (sıfıra bölme koruması).
        """
        if self._n == 0:
            return 0.0
        return self.gecis_sayisi() / self._n

    def iletim_gecikmesi(self) -> float:
        """
        Transmission delay: n / R (saniye).
        n: bit sayısı, R: bit hızı (bps).
        """
        return self._n / self._R

    def yayilma_gecikmesi(self) -> float:
        """
        Propagation delay: d / v (saniye).
        d: bağlantı uzunluğu (m), v: yayılma hızı (m/s).
        """
        return self._d / self._v

    def tek_yonlu_toplam_gecikme(self) -> float:
        """Tek yönlü toplam gecikme: iletim + yayılma (saniye)."""
        return self.iletim_gecikmesi() + self.yayilma_gecikmesi()

    @staticmethod
    def _dogrula_bit_dizisi(bit_dizisi: str) -> str:
        """
        Bit dizisi doğrulama.
        Boş string kabul edilir (n=0 durumu için).
        """
        if not isinstance(bit_dizisi, str):
            raise GecersizBitDizisiError("Bit dizisi str olmalıdır.")
        if len(bit_dizisi) > 0 and any(c not in ("0", "1") for c in bit_dizisi):
            raise GecersizBitDizisiError("Bit dizisi yalnızca '0' ve '1' içerebilir.")
        return bit_dizisi

    @staticmethod
    def _dogrula_pozitif(value: float, ad: str) -> float:
        """
        Pozitif sayı doğrulama.
        Sıfır ve negatif değerler reddedilir (sıfıra bölme koruması).
        """
        try:
            x = float(value)
        except (TypeError, ValueError) as exc:
            raise GecersizParametreError(f"{ad} sayısal olmalıdır.") from exc
        if x <= 0:
            raise GecersizParametreError(f"{ad} sıfırdan büyük olmalıdır.")
        return x

    @classmethod
    def _cozumle_kodlama_turu(cls, kodlama_turu: Union[KodlamaTipi, str]) -> KodlamaTipi:
        """Kodlama türü çözümleme - alias desteği ile."""
        if isinstance(kodlama_turu, KodlamaTipi):
            return kodlama_turu
        if not isinstance(kodlama_turu, str) or not kodlama_turu.strip():
            raise GecersizKodlamaTipiError("Kodlama türü boş veya geçersiz.")
        key = kodlama_turu.strip().upper().replace(" ", "")
        if key == "NRZ-L":
            return KodlamaTipi.NRZ_L
        if key == "MANCHESTER":
            return KodlamaTipi.MANCHESTER
        alias = kodlama_turu.strip().lower().replace(" ", "")
        if alias in cls._KODLAMA_ALIAS:
            return cls._KODLAMA_ALIAS[alias]
        raise GecersizKodlamaTipiError(
            "Kodlama türü 'NRZ-L' veya 'MANCHESTER' olmalıdır."
        )

    @staticmethod
    def _kodla(bits: str, tur: KodlamaTipi) -> str:
        """
        Sinyal kodlama algoritması.
        NRZ-L: 1 -> H, 0 -> L
        Manchester: 1 -> HL (önce yüksek, sonra düşük), 0 -> LH (önce düşük, sonra yüksek)
        """
        if tur == KodlamaTipi.NRZ_L:
            return "".join("H" if b == "1" else "L" for b in bits)
        # Manchester: Her bit 2 sembole genişler
        parcalar: list[str] = []
        for b in bits:
            parcalar.append("HL" if b == "1" else "LH")
        return "".join(parcalar)
