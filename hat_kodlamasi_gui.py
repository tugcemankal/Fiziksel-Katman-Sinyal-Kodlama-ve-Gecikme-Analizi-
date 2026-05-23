"""
Hat Kodlaması Simülatörü — Profesyonel PyQt5 GUI
Backend: hat_kodlamasi_backend_fixed.py (dokunulmaz)
"""

import sys
import numpy as np
import matplotlib
matplotlib.use("Qt5Agg")
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.ticker as mticker

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QFrame, QMessageBox,
    QScrollArea, QSizePolicy, QGraphicsDropShadowEffect,
)
from PyQt5.QtCore import Qt, QTimer, QPropertyAnimation, QRect, pyqtSignal
from PyQt5.QtGui import QFont, QColor, QPalette, QIntValidator, QDoubleValidator

from hat_kodlamasi_backend_fixed import (
    HatKodlamasiBackend, KodlamaTipi, HatKodlamasiError
)

# ─────────────────────────── THEME ───────────────────────────
C = {
    "bg":         "#0D1117",
    "surface":    "#161B22",
    "surface2":   "#1C2330",
    "border":     "#30363D",
    "accent":     "#58A6FF",
    "green":      "#3FB950",
    "green_bg":   "#0D2818",
    "green_brd":  "#238636",
    "purple":     "#BC8CFF",
    "orange":     "#F0883E",
    "red":        "#F85149",
    "red_bg":     "#2D1117",
    "text":       "#E6EDF3",
    "muted":      "#8B949E",
    "nrz_sel":    "#1C3550",
    "man_sel":    "#1E1040",
}

STYLE = f"""
* {{ font-family: 'Segoe UI', 'Inter', sans-serif; }}

QMainWindow, QWidget#root {{
    background-color: {C['bg']};
    color: {C['text']};
}}

QWidget {{
    background-color: transparent;
    color: {C['text']};
}}

QScrollArea {{
    background-color: {C['bg']};
    border: none;
}}

QLineEdit {{
    background-color: {C['surface2']};
    border: 1.5px solid {C['border']};
    border-radius: 10px;
    color: {C['text']};
    padding: 10px 16px;
    font-size: 13px;
    font-family: 'Consolas', 'Courier New', monospace;
    selection-background-color: {C['accent']};
}}
QLineEdit:focus {{
    border-color: {C['accent']};
    background-color: #141C28;
}}
QLineEdit[invalid="true"] {{
    border-color: {C['red']};
    background-color: #1C1318;
}}
QLineEdit::placeholder {{ color: {C['muted']}; }}

QPushButton#calc {{
    background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
        stop:0 #1F6FEB, stop:1 {C['accent']});
    color: #ffffff;
    border: none;
    border-radius: 10px;
    padding: 13px 0px;
    font-size: 14px;
    font-weight: 700;
    letter-spacing: 0.5px;
}}
QPushButton#calc:hover {{
    background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
        stop:0 {C['accent']}, stop:1 #79BFFF);
}}
QPushButton#calc:pressed {{ background: #1158CC; }}
QPushButton#calc:disabled {{
    background: {C['surface2']};
    color: {C['muted']};
}}

QPushButton#clr {{
    background-color: {C['surface2']};
    color: {C['muted']};
    border: 1.5px solid {C['border']};
    border-radius: 10px;
    padding: 12px 20px;
    font-size: 13px;
    font-weight: 600;
}}
QPushButton#clr:hover {{
    background-color: {C['surface']};
    color: {C['text']};
    border-color: {C['muted']};
}}

QPushButton#nrz_off, QPushButton#man_off {{
    background-color: {C['surface2']};
    color: {C['muted']};
    border: 1.5px solid {C['border']};
    border-radius: 10px;
    padding: 11px 24px;
    font-size: 13px;
    font-weight: 600;
}}
QPushButton#nrz_on {{
    background-color: {C['nrz_sel']};
    color: {C['accent']};
    border: 1.5px solid {C['accent']};
    border-radius: 10px;
    padding: 11px 24px;
    font-size: 13px;
    font-weight: 700;
}}
QPushButton#man_on {{
    background-color: {C['man_sel']};
    color: {C['purple']};
    border: 1.5px solid {C['purple']};
    border-radius: 10px;
    padding: 11px 24px;
    font-size: 13px;
    font-weight: 700;
}}
QPushButton#nrz_off:hover {{
    background-color: {C['nrz_sel']};
    color: {C['accent']};
    border-color: {C['accent']};
}}
QPushButton#man_off:hover {{
    background-color: {C['man_sel']};
    color: {C['purple']};
    border-color: {C['purple']};
}}

QLabel#page_title {{
    color: {C['text']};
    font-size: 22px;
    font-weight: 700;
    letter-spacing: 1px;
}}
QLabel#page_sub {{
    color: {C['muted']};
    font-size: 12px;
}}
QLabel#sec {{
    color: {C['muted']};
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 1.2px;
}}
QLabel#field_label {{
    color: {C['text']};
    font-size: 13px;
    font-weight: 600;
}}
QLabel#hint {{
    color: {C['muted']};
    font-size: 11px;
    padding-left: 2px;
}}

QFrame#card {{
    background-color: {C['surface']};
    border: 1px solid {C['border']};
    border-radius: 12px;
}}
QFrame#divider {{
    background-color: {C['border']};
    max-height: 1px;
    min-height: 1px;
}}
QFrame#result_card {{
    background-color: {C['surface']};
    border: 1px solid {C['border']};
    border-radius: 14px;
}}
QFrame#success_banner {{
    background-color: {C['green_bg']};
    border: 1px solid {C['green_brd']};
    border-radius: 8px;
}}
QFrame#error_banner {{
    background-color: {C['red_bg']};
    border: 1px solid {C['red']};
    border-radius: 8px;
}}

QLabel#res_section {{
    color: {C['muted']};
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 1.2px;
    padding-bottom: 2px;
}}
QLabel#res_key {{
    color: {C['muted']};
    font-size: 12px;
}}
QLabel#res_val_green {{
    color: {C['green']};
    font-size: 16px;
    font-weight: 700;
    font-family: 'Consolas', monospace;
}}
QLabel#res_val_blue {{
    color: {C['accent']};
    font-size: 16px;
    font-weight: 700;
    font-family: 'Consolas', monospace;
}}
QLabel#res_val_orange {{
    color: {C['orange']};
    font-size: 16px;
    font-weight: 700;
    font-family: 'Consolas', monospace;
}}
QLabel#res_val_purple {{
    color: {C['purple']};
    font-size: 16px;
    font-weight: 700;
    font-family: 'Consolas', monospace;
}}
QLabel#encoded_seq {{
    color: {C['green']};
    font-size: 13px;
    font-family: 'Consolas', monospace;
    background-color: #0A1E14;
    border: 1px solid #1A4228;
    border-radius: 8px;
    padding: 10px 14px;
}}
QLabel#banner_text_ok {{
    color: {C['green']};
    font-size: 13px;
    font-weight: 700;
}}
QLabel#banner_text_err {{
    color: {C['red']};
    font-size: 13px;
    font-weight: 700;
}}
"""


# ─────────────────────────── WAVEFORM CANVAS ───────────────────────────

WAVEFORM_STYLE = {
    "figure.facecolor":  C["surface"],
    "axes.facecolor":    C["surface2"],
    "axes.edgecolor":    C["border"],
    "axes.labelcolor":   C["muted"],
    "axes.titlecolor":   C["text"],
    "axes.grid":         True,
    "grid.color":        C["border"],
    "grid.linewidth":    0.5,
    "grid.alpha":        0.6,
    "text.color":        C["text"],
    "xtick.color":       C["muted"],
    "ytick.color":       C["muted"],
    "xtick.labelsize":   9,
    "ytick.labelsize":   9,
    "axes.labelsize":    11,
    "axes.titlesize":    13,
    "axes.titleweight":  "bold",
    "figure.dpi":        100,
}


class WaveformCanvas(FigureCanvas):
    """Matplotlib canvas — NRZ-L ve Manchester dalga formu çizici."""

    NRZ_COLOR  = C["accent"]   # #58A6FF  mavi
    MAN_COLOR  = C["purple"]   # #BC8CFF  mor
    BIT_COLOR  = C["text"]     # bit etiketi rengi
    DASH_COLOR = C["border"]   # kesikli dikey çizgi rengi

    def __init__(self, parent=None):
        import matplotlib.pyplot as plt
        plt.rcParams.update(WAVEFORM_STYLE)
        self.fig = Figure(figsize=(9, 3.2), tight_layout=True)
        super().__init__(self.fig)
        self.setParent(parent)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self._draw_placeholder()

    def _draw_placeholder(self):
        self.fig.clear()
        ax = self.fig.add_subplot(111)
        ax.text(
            0.5, 0.5,
            "Hesapla dusumune basinca dalga formu buraya cizilecek",
            ha="center", va="center", fontsize=12,
            color=C["muted"], transform=ax.transAxes,
        )
        ax.set_xticks([])
        ax.set_yticks([])
        self.draw()

    def plot(self, bits: str, encoded: str, coding: KodlamaTipi):
        """Verilen bit dizisi ve kodlamaya göre dalga formunu ciz."""
        self.fig.clear()
        ax = self.fig.add_subplot(111)

        n = len(bits)
        is_manchester = (coding == KodlamaTipi.MANCHESTER)
        line_color = self.MAN_COLOR if is_manchester else self.NRZ_COLOR

        # ── Sinyal seviyesi dizisi oluştur (step fonksiyonu için) ──
        # Her bit için bir (veya iki) sembol H=+1, L=-1
        samples_per_bit = 2 if is_manchester else 1
        total_symbols = n * samples_per_bit

        # X: her sembol 0.5 birim genişliğinde (bit aralığı = samples_per_bit * 0.5)
        # Bit aralığını 1 birim yapmak için: her sembol = 1/samples_per_bit
        symbol_width = 1.0 / samples_per_bit

        # Kodlanmış dizi -> sayısal dizi
        levels = [+1.0 if ch == "H" else -1.0 for ch in encoded]

        # Step plot için X ve Y dizileri
        x_step = []
        y_step = []
        for i, lv in enumerate(levels):
            t_start = i * symbol_width
            t_end   = (i + 1) * symbol_width
            x_step += [t_start, t_end]
            y_step += [lv, lv]

        # Son noktayı tam kapansın diye ekle
        ax.plot(x_step, y_step, color=line_color, linewidth=2.4,
                solid_capstyle="butt", zorder=4)

        # Dikey geçişleri bağla (H->L, L->H)
        for i in range(len(levels) - 1):
            if levels[i] != levels[i + 1]:
                tx = (i + 1) * symbol_width
                ax.plot([tx, tx], [levels[i], levels[i + 1]],
                        color=line_color, linewidth=2.4,
                        solid_capstyle="butt", zorder=4)

        # ── Bit sınır çizgileri (kesikli) ──
        for i in range(n + 1):
            ax.axvline(x=i, color=self.DASH_COLOR, linewidth=0.9,
                       linestyle="--", alpha=0.7, zorder=2)

        # ── Bit etiketleri (her bit aralığının üstüne) ──
        for i, bit in enumerate(bits):
            mid = i + 0.5
            ax.text(
                mid, 1.35, bit,
                ha="center", va="center",
                fontsize=11, fontweight="bold",
                color=self.NRZ_COLOR if bit == "1" else C["orange"],
                zorder=6,
            )

        # ── Bant etiket çizgisi (bit etiketi kuşağı ayırma) ──
        ax.axhline(y=1.15, color=C["border"], linewidth=0.6,
                   linestyle=":", alpha=0.5, zorder=1)

        # ── Eksen ayarları ──
        coding_label = "NRZ-L" if coding == KodlamaTipi.NRZ_L else "Manchester"
        ax.set_title(
            f"{coding_label}  Dalga Formu  —  Bit Dizisi: {bits}",
            pad=10
        )
        ax.set_xlabel("Bit Araligi (zaman)", labelpad=8)
        ax.set_ylabel("Sinyal (V)", labelpad=8)

        ax.set_xlim(-0.1, n + 0.1)
        ax.set_ylim(-1.55, 1.65)

        # X ticks: bit sınırları
        ax.set_xticks(range(n + 1))
        ax.set_xticklabels([str(t) for t in range(n + 1)], fontsize=8)

        # Y ticks: +1V ve -1V
        ax.set_yticks([-1.0, 0.0, 1.0])
        ax.set_yticklabels(["-1 V (L)", "0", "+1 V (H)"], fontsize=9)

        # Yatay referans çizgisi
        ax.axhline(y=0, color=C["muted"], linewidth=0.7,
                   linestyle="-", alpha=0.4, zorder=1)

        # Arka plan şeritler: her çift bit açık, tek bit koyu (okunabilirlik)
        for i in range(n):
            if i % 2 == 0:
                ax.axvspan(i, i + 1, facecolor="#FFFFFF", alpha=0.025, zorder=0)

        self.draw()


# ─────────────────────────── HELPERS ───────────────────────────

def make_card():
    f = QFrame()
    f.setObjectName("card")
    return f


def divider():
    f = QFrame()
    f.setObjectName("divider")
    return f


def shadow(color=C['accent'], blur=18):
    s = QGraphicsDropShadowEffect()
    s.setBlurRadius(blur)
    s.setColor(QColor(color))
    s.setOffset(0, 0)
    return s


def section_label(text):
    l = QLabel(text.upper())
    l.setObjectName("sec")
    return l


def field_label(text):
    l = QLabel(text)
    l.setObjectName("field_label")
    return l


def hint_label(text):
    l = QLabel(text)
    l.setObjectName("hint")
    return l


def make_input(placeholder, hint_text=""):
    container = QWidget()
    lay = QVBoxLayout(container)
    lay.setContentsMargins(0, 0, 0, 0)
    lay.setSpacing(4)
    inp = QLineEdit()
    inp.setPlaceholderText(placeholder)
    inp.setMinimumHeight(44)
    lay.addWidget(inp)
    if hint_text:
        lay.addWidget(hint_label(hint_text))
    return container, inp


def res_row(key: str, value: str, color_name: str) -> QWidget:
    w = QWidget()
    h = QHBoxLayout(w)
    h.setContentsMargins(0, 0, 0, 0)
    h.setSpacing(8)
    k = QLabel(key)
    k.setObjectName("res_key")
    v = QLabel(value)
    v.setObjectName(f"res_val_{color_name}")
    v.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
    v.setWordWrap(True)
    h.addWidget(k, 1)
    h.addWidget(v, 1)
    return w


# ─────────────────────────── MAIN WINDOW ───────────────────────────

class HatKodlamasiGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Hat Kodlaması Simülatörü  •  Bilgisayar Ağları")
        self.setMinimumSize(900, 720)
        self.resize(1060, 860)
        self._selected_coding = KodlamaTipi.NRZ_L

        root = QWidget()
        root.setObjectName("root")
        self.setCentralWidget(root)

        scroll = QScrollArea()
        scroll.setWidget(root)
        scroll.setWidgetResizable(True)
        scroll.setObjectName("")
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setCentralWidget(scroll)

        main = QVBoxLayout(root)
        main.setContentsMargins(28, 24, 28, 28)
        main.setSpacing(20)

        main.addLayout(self._build_header())
        main.addWidget(divider())
        main.addWidget(self._build_input_card())
        self._result_widget = self._build_result_placeholder()
        main.addWidget(self._result_widget)
        main.addWidget(self._build_chart_card())
        main.addWidget(self._build_footer())

    # ── Header ──
    def _build_header(self):
        h = QHBoxLayout()
        left = QVBoxLayout()
        left.setSpacing(4)
        logo = QLabel("◈ HAT KODLAMASI")
        logo.setObjectName("page_title")
        sub = QLabel("NRZ-L & Manchester  •  İletim & Yayılma Gecikmesi Analizi")
        sub.setObjectName("page_sub")
        left.addWidget(logo)
        left.addWidget(sub)
        h.addLayout(left)
        h.addStretch()
        badge = QLabel("v1.0")
        badge.setStyleSheet(
            f"background:{C['surface2']};color:{C['muted']};"
            f"border:1px solid {C['border']};border-radius:5px;"
            f"padding:3px 12px;font-size:11px;"
        )
        h.addWidget(badge, alignment=Qt.AlignTop)
        return h

    # ── Input Card ──
    def _build_input_card(self):
        card = make_card()
        lay = QVBoxLayout(card)
        lay.setContentsMargins(24, 22, 24, 22)
        lay.setSpacing(18)

        # ── Bit dizisi ──
        lay.addWidget(section_label("Giriş Parametreleri"))
        lay.addWidget(field_label("Bit Dizisi"))
        bw, self.inp_bits = make_input(
            "Örnek: 10110010",
            "💡  Yalnızca 0 ve 1 içermeli"
        )
        lay.addWidget(bw)

        # ── R / d / v ──
        row = QHBoxLayout()
        row.setSpacing(14)

        rw, self.inp_R = make_input("Örnek: 1000000", "bps  (bit/s)")
        dw, self.inp_d = make_input("Örnek: 5000", "metre (m)")
        vw, self.inp_v = make_input("Örnek: 200000000", "m/s")

        for label_txt, w in [("Bit Hızı  R", rw), ("Bağlantı Uzunluğu  d", dw), ("Yayılma Hızı  v", vw)]:
            col = QVBoxLayout()
            col.setSpacing(6)
            col.addWidget(field_label(label_txt))
            col.addWidget(w)
            row.addLayout(col)

        lay.addLayout(row)

        # ── Kodlama türü ──
        lay.addWidget(divider())
        lay.addWidget(section_label("Kodlama Türü"))

        enc_row = QHBoxLayout()
        enc_row.setSpacing(12)

        self.btn_nrz = QPushButton("⬛  NRZ-L")
        self.btn_man = QPushButton("⬜  Manchester")
        self.btn_nrz.setObjectName("nrz_on")
        self.btn_man.setObjectName("man_off")
        self.btn_nrz.setMinimumHeight(46)
        self.btn_man.setMinimumHeight(46)
        self.btn_nrz.clicked.connect(lambda: self._select_coding(KodlamaTipi.NRZ_L))
        self.btn_man.clicked.connect(lambda: self._select_coding(KodlamaTipi.MANCHESTER))
        enc_row.addWidget(self.btn_nrz)
        enc_row.addWidget(self.btn_man)
        enc_row.addStretch()

        nrz_desc = QLabel(
            "NRZ-L:  1 → <b>H</b>&nbsp; 0 → <b>L</b>&nbsp;&nbsp;&nbsp;"
            "Manchester:  1 → <b>HL</b>&nbsp; 0 → <b>LH</b>"
        )
        nrz_desc.setObjectName("hint")
        nrz_desc.setStyleSheet(f"color:{C['muted']};font-size:11px;")

        lay.addLayout(enc_row)
        lay.addWidget(nrz_desc)

        # ── Butonlar ──
        lay.addWidget(divider())
        btn_row = QHBoxLayout()
        btn_row.setSpacing(12)
        self.btn_calc = QPushButton("▶   Hesapla")
        self.btn_calc.setObjectName("calc")
        self.btn_calc.setMinimumHeight(50)
        self.btn_calc.clicked.connect(self._hesapla)
        self.btn_clr = QPushButton("↺  Temizle")
        self.btn_clr.setObjectName("clr")
        self.btn_clr.setMinimumHeight(50)
        self.btn_clr.setMaximumWidth(130)
        self.btn_clr.clicked.connect(self._temizle)
        btn_row.addWidget(self.btn_calc)
        btn_row.addWidget(self.btn_clr)
        lay.addLayout(btn_row)

        return card

    # ── Sonuç placeholder ──
    def _build_result_placeholder(self):
        w = QWidget()
        lay = QVBoxLayout(w)
        lay.setContentsMargins(0, 0, 0, 0)
        return w

    # ── Waveform chart kartı ──
    def _build_chart_card(self):
        c = make_card()
        lay = QVBoxLayout(c)
        lay.setContentsMargins(18, 14, 18, 14)
        lay.setSpacing(10)
        hdr = QHBoxLayout()
        hdr.addWidget(section_label("Sinyal Dalga Formu  —  NRZ-L / Manchester"))
        hdr.addStretch()
        self._wave_type_lbl = QLabel("")
        self._wave_type_lbl.setStyleSheet(
            f"color:{C['muted']};font-size:11px;font-weight:600;"
        )
        hdr.addWidget(self._wave_type_lbl)
        lay.addLayout(hdr)
        self.canvas = WaveformCanvas()
        self.canvas.setMinimumHeight(220)
        lay.addWidget(self.canvas)
        return c

    # ── Footer ──
    def _build_footer(self):
        l = QLabel("Backend: hat_kodlamasi_backend_fixed.py  •  NRZ-L / Manchester Encoding  •  İletim & Yayılma Gecikmesi")
        l.setAlignment(Qt.AlignCenter)
        l.setStyleSheet(f"color:{C['muted']};font-size:10px;padding-top:4px;")
        return l

    # ─────────── Kodlama seçimi ───────────
    def _select_coding(self, typ: KodlamaTipi):
        self._selected_coding = typ
        if typ == KodlamaTipi.NRZ_L:
            self.btn_nrz.setObjectName("nrz_on")
            self.btn_man.setObjectName("man_off")
        else:
            self.btn_nrz.setObjectName("nrz_off")
            self.btn_man.setObjectName("man_on")
        self.btn_nrz.setStyle(self.btn_nrz.style())
        self.btn_man.setStyle(self.btn_man.style())

    # ─────────── Input validation ───────────
    def _validate(self):
        errors = []
        bits = self.inp_bits.text().strip()
        R_txt = self.inp_R.text().strip()
        d_txt = self.inp_d.text().strip()
        v_txt = self.inp_v.text().strip()

        def mark(inp, bad):
            inp.setProperty("invalid", "true" if bad else "false")
            inp.setStyle(inp.style())

        bad_bits = not bits or any(c not in "01" for c in bits)
        mark(self.inp_bits, bad_bits)
        if not bits:
            errors.append("Bit dizisi boş olamaz.")
        elif bad_bits:
            errors.append("Bit dizisi yalnızca '0' ve '1' içermeli.")

        for lbl, txt, inp in [
            ("Bit Hızı (R)", R_txt, self.inp_R),
            ("Bağlantı Uzunluğu (d)", d_txt, self.inp_d),
            ("Yayılma Hızı (v)", v_txt, self.inp_v),
        ]:
            bad = False
            if not txt:
                errors.append(f"{lbl} boş olamaz.")
                bad = True
            else:
                try:
                    val = float(txt)
                    if val <= 0:
                        errors.append(f"{lbl} sıfırdan büyük olmalı.")
                        bad = True
                except ValueError:
                    errors.append(f"{lbl} geçerli bir sayı olmalı.")
                    bad = True
            mark(inp, bad)

        return errors

    # ─────────── Hesapla ───────────
    def _hesapla(self):
        errors = self._validate()
        if errors:
            msg = QMessageBox(self)
            msg.setWindowTitle("Giriş Hatası")
            msg.setIcon(QMessageBox.Warning)
            msg.setText("<b>Lütfen aşağıdaki hataları düzeltin:</b>")
            msg.setInformativeText("\n".join(f"• {e}" for e in errors))
            msg.setStyleSheet(
                f"QWidget{{background:{C['surface']};color:{C['text']};}}"
                f"QLabel{{background:transparent;}}"
            )
            msg.exec_()
            return

        try:
            backend = HatKodlamasiBackend(
                bit_dizisi=self.inp_bits.text().strip(),
                kodlama_turu=self._selected_coding,
                bit_hizi_R=float(self.inp_R.text().strip()),
                baglanti_uzunlugu_d=float(self.inp_d.text().strip()),
                yayilma_hizi_v=float(self.inp_v.text().strip()),
            )
            self._show_results(backend)
        except HatKodlamasiError as exc:
            self._show_error(str(exc))
        except Exception as exc:
            self._show_error(f"Beklenmeyen hata: {exc}")

    # ─────────── Sonuç paneli ───────────
    def _show_results(self, b: HatKodlamasiBackend):
        self._clear_result_widget()
        lay = self._result_widget.layout()

        # Banner
        banner = QFrame()
        banner.setObjectName("success_banner")
        bl = QHBoxLayout(banner)
        bl.setContentsMargins(14, 10, 14, 10)
        bl_lbl = QLabel("✅  Hesaplama başarılı")
        bl_lbl.setObjectName("banner_text_ok")
        bl.addWidget(bl_lbl)
        bl.addStretch()
        enc_lbl = QLabel(b.kodlama_turu.value)
        enc_lbl.setStyleSheet(
            f"background:{C['nrz_sel'] if b.kodlama_turu==KodlamaTipi.NRZ_L else C['man_sel']};"
            f"color:{C['accent'] if b.kodlama_turu==KodlamaTipi.NRZ_L else C['purple']};"
            f"border:1px solid {C['accent'] if b.kodlama_turu==KodlamaTipi.NRZ_L else C['purple']};"
            f"border-radius:5px;padding:2px 12px;font-size:12px;font-weight:700;"
        )
        bl.addWidget(enc_lbl)
        lay.addWidget(banner)

        # ── Kodlanmış dizi kartı ──
        seq_card = make_card()
        sc_lay = QVBoxLayout(seq_card)
        sc_lay.setContentsMargins(20, 16, 20, 16)
        sc_lay.setSpacing(8)

        sc_title = section_label("Kodlanmış Sinyal Dizisi")
        sc_lay.addWidget(sc_title)

        encoded = b.kodlanmis_diziyi_al()
        # Wrap long sequence every 64 chars
        wrapped = "\n".join(encoded[i:i+64] for i in range(0, len(encoded), 64))
        seq_lbl = QLabel(wrapped if wrapped else "—")
        seq_lbl.setObjectName("encoded_seq")
        seq_lbl.setWordWrap(True)
        seq_lbl.setTextInteractionFlags(Qt.TextSelectableByMouse)
        sc_lay.addWidget(seq_lbl)

        lay.addWidget(seq_card)

        # ── Metrik kartları ──
        metrics_row = QHBoxLayout()
        metrics_row.setSpacing(14)

        # Bit analizi
        bit_card = self._metric_card(
            "Bit Analizi",
            [
                ("Bit Sayısı (n)", str(b.bit_sayisi), "blue"),
                ("Toplam Sembol", str(b.toplam_sembol_sayisi()), "purple"),
                ("Geçiş Sayısı", str(b.gecis_sayisi()), "orange"),
                ("Geçiş Yoğunluğu", f"{b.gecis_yogunlugu_bit_basina():.3f} / bit", "orange"),
            ]
        )
        metrics_row.addWidget(bit_card)

        # Gecikme analizi
        it = b.iletim_gecikmesi()
        yy = b.yayilma_gecikmesi()
        top = b.tek_yonlu_toplam_gecikme()

        delay_card = self._metric_card(
            "Gecikme Analizi",
            [
                ("İletim Gecikmesi  (n/R)", self._fmt_time(it), "green"),
                ("Yayılma Gecikmesi  (d/v)", self._fmt_time(yy), "green"),
                ("Tek Yönlü Toplam", self._fmt_time(top), "blue"),
            ]
        )
        metrics_row.addWidget(delay_card)
        lay.addLayout(metrics_row)

        # ── Dalga formu grafiği ──
        bits_str = self.inp_bits.text().strip()
        # Çok uzun bit dizisinde grafik kalabalık olur; max 48 bit göster
        bits_display = bits_str[:48]
        encoded_display = encoded[:48 * (2 if b.kodlama_turu == KodlamaTipi.MANCHESTER else 1)]
        color = C['accent'] if b.kodlama_turu == KodlamaTipi.NRZ_L else C['purple']
        self._wave_type_lbl.setText(
            f"{b.kodlama_turu.value}  •  {len(bits_str)} bit"
            + ("  (ilk 48 bit gösteriliyor)" if len(bits_str) > 48 else "")
        )
        self._wave_type_lbl.setStyleSheet(f"color:{color};font-size:11px;font-weight:600;")
        self.canvas.plot(bits_display, encoded_display, b.kodlama_turu)

    def _metric_card(self, title: str, rows: list) -> QFrame:
        card = make_card()
        lay = QVBoxLayout(card)
        lay.setContentsMargins(20, 16, 20, 16)
        lay.setSpacing(12)
        lay.addWidget(section_label(title))
        lay.addWidget(divider())
        for key, val, color in rows:
            lay.addWidget(res_row(key, val, color))
        lay.addStretch()
        return card

    def _show_error(self, message: str):
        self._clear_result_widget()
        lay = self._result_widget.layout()

        banner = QFrame()
        banner.setObjectName("error_banner")
        bl = QHBoxLayout(banner)
        bl.setContentsMargins(14, 12, 14, 12)
        err_lbl = QLabel(f"❌  {message}")
        err_lbl.setObjectName("banner_text_err")
        err_lbl.setWordWrap(True)
        bl.addWidget(err_lbl)
        lay.addWidget(banner)

    def _clear_result_widget(self):
        lay = self._result_widget.layout()
        while lay.count():
            item = lay.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                self._clear_layout(item.layout())

    def _clear_layout(self, lay):
        while lay.count():
            item = lay.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                self._clear_layout(item.layout())

    @staticmethod
    def _fmt_time(seconds: float) -> str:
        """Saniyeyi okunabilir birime dönüştür."""
        if seconds == 0:
            return "0 s"
        if seconds >= 1:
            return f"{seconds:.6f} s"
        if seconds >= 1e-3:
            return f"{seconds*1e3:.6f} ms"
        if seconds >= 1e-6:
            return f"{seconds*1e6:.6f} µs"
        return f"{seconds*1e9:.6f} ns"

    def _temizle(self):
        for inp in [self.inp_bits, self.inp_R, self.inp_d, self.inp_v]:
            inp.clear()
            inp.setProperty("invalid", "false")
            inp.setStyle(inp.style())
        self._select_coding(KodlamaTipi.NRZ_L)
        self._clear_result_widget()


# ─────────────────────────── ENTRY ───────────────────────────

def main():
    app = QApplication(sys.argv)
    app.setStyleSheet(STYLE)

    pal = QPalette()
    pal.setColor(QPalette.Window, QColor(C["bg"]))
    pal.setColor(QPalette.WindowText, QColor(C["text"]))
    pal.setColor(QPalette.Base, QColor(C["surface2"]))
    pal.setColor(QPalette.Text, QColor(C["text"]))
    pal.setColor(QPalette.Button, QColor(C["surface"]))
    pal.setColor(QPalette.ButtonText, QColor(C["text"]))
    app.setPalette(pal)

    win = HatKodlamasiGUI()
    win.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
