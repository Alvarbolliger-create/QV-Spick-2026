# ============================================================
# utils.py – Gemeinsame Hilfsfunktionen
# Elektrotechnik-Spick | Elektroniker EFZ
# ============================================================
# Verwendung in jedem Notebook:
#   from utils import p, fmt, make_input, make_button, check_inputs
# ============================================================

import re
import math
import ipywidgets as widgets
from IPython.display import display, HTML


# ------------------------------------------------------------
# SI-Präfix Tabelle
# ------------------------------------------------------------
SI_PREFIXES = {
    'p': 1e-12,
    'n': 1e-9,
    'u': 1e-6,
    'µ': 1e-6,
    'm': 1e-3,
    '':  1.0,
    'k': 1e3,
    'M': 1e6,
    'G': 1e9,
}


# ------------------------------------------------------------
# Physikalische Konstanten (direkt importierbar)
# ------------------------------------------------------------
EPS0 = 8.854187817e-12   # Elektrische Feldkonstante [F/m]
MU0  = 4 * math.pi * 1e-7  # Magnetische Feldkonstante [H/m]
K_B  = 1.380649e-23       # Boltzmann-Konstante [J/K]
Q_E  = 1.602176634e-19    # Elementarladung [C]


# ------------------------------------------------------------
# p() – SI-Präfix Parser
# ------------------------------------------------------------
def p(val_str):
    """
    Parst eine Zahl mit optionalem SI-Präfix.

    Beispiele:
        p('10k')    → 10000.0
        p('4.7u')   → 4.7e-6
        p('100n')   → 1e-7
        p('1.5M')   → 1500000.0
        p('230')    → 230.0
        p('')       → None
        p(None)     → None

    Unterstützte Präfixe: p, n, u, µ, m, (leer), k, M, G
    """
    if val_str is None:
        return None
    val_str = val_str.strip()
    if val_str == '':
        return None
    match = re.fullmatch(r'([-+]?\d*\.?\d+)\s*([pnuµmkMG]?)', val_str)
    if not match:
        raise ValueError(f"Ungültiger Wert: '{val_str}'")
    value, prefix = match.groups()
    return float(value) * SI_PREFIXES[prefix]


# ------------------------------------------------------------
# fmt() – Wert mit SI-Präfix formatieren
# ------------------------------------------------------------
def fmt(val, unit=''):
    """
    Formatiert einen Zahlenwert mit passendem SI-Präfix.

    Beispiele:
        fmt(0.001, 'Ω')   → '1 mΩ'
        fmt(12000, 'Hz')  → '12 kHz'
        fmt(4.7e-6, 'F')  → '4.7 µF'
        fmt(0, 'V')       → '0 V'

    Parameter:
        val  – Zahlenwert (float/int)
        unit – Einheitenzeichen als String (optional)
    """
    if val == 0:
        return f"0 {unit}".strip()
    abs_val = abs(val)
    prefixes = [
        ('G', 1e9),
        ('M', 1e6),
        ('k', 1e3),
        ('',  1.0),
        ('m', 1e-3),
        ('µ', 1e-6),
        ('n', 1e-9),
        ('p', 1e-12),
    ]
    for name, factor in prefixes:
        if abs_val >= factor:
            return f"{val / factor:.4g} {name}{unit}".strip()
    return f"{val:.4e} {unit}".strip()


# ------------------------------------------------------------
# check_inputs() – Fehlende Felder prüfen
# ------------------------------------------------------------
def check_inputs(vals: dict):
    """
    Prüft wie viele Felder in einem Rechner leer (None) sind.

    Parameter:
        vals – Dictionary mit Feldname → Wert
               z.B. {'R': R, 'U': U, 'I': I}

    Rückgabe:
        (anzahl_leer, [liste_der_leeren_keys])

    Typische Verwendung:
        miss_n, miss = check_inputs({'R': R, 'U': U, 'I': I})
        if miss_n != 1:
            print("Genau ein Feld leer lassen!" if miss_n > 1 else "Ein Feld leer lassen!")
            return
        m = miss[0]  # Name des fehlenden Feldes
    """
    miss = [k for k, v in vals.items() if v is None]
    return len(miss), miss


# ------------------------------------------------------------
# make_input() – Einheitliches Eingabefeld
# ------------------------------------------------------------
def make_input(description, placeholder='leer lassen = berechnen'):
    """
    Erstellt ein einheitliches ipywidgets Text-Eingabefeld.

    Parameter:
        description  – Feldbeschriftung (z.B. 'R [Ω]  =')
        placeholder  – Grauer Hinweistext im leeren Feld

    Einheitliches Layout:
        Breite: 320px
        Beschriftungsbreite: 140px

    Beispiel:
        R_input = make_input('R [Ω]  =')
        C_input = make_input('C [F]  =', 'z.B. 100n, 4.7u')
    """
    return widgets.Text(
        description=description,
        placeholder=placeholder,
        layout=widgets.Layout(width='320px'),
        style={'description_width': '140px'},
    )


# ------------------------------------------------------------
# make_button() – Einheitlicher Berechnungs-Button
# ------------------------------------------------------------
def make_button(label='Berechnen'):
    """
    Erstellt einen einheitlichen ipywidgets Button.

    Parameter:
        label – Beschriftung des Buttons (default: 'Berechnen')

    Einheitliches Layout:
        Stil: primary (blau)
        Breite: 180px
        Margin: 8px oben/unten

    Beispiel:
        btn = make_button()
        btn_plot = make_button('Zeichnen')
        btn.on_click(calc_func)
    """
    return widgets.Button(
        description=label,
        button_style='primary',
        layout=widgets.Layout(width='180px', margin='8px 0'),
    )


# ------------------------------------------------------------
# make_dropdown() – Einheitliches Dropdown
# ------------------------------------------------------------
def make_dropdown(description, options):
    """
    Erstellt ein einheitliches ipywidgets Dropdown.

    Parameter:
        description – Feldbeschriftung
        options     – Liste von Tupeln: [('Anzeigetext', wert), ...]
                      oder Liste von Strings: ['Option1', 'Option2']

    Einheitliches Layout:
        Breite: 340px
        Beschriftungsbreite: 140px

    Beispiel:
        mat = make_dropdown('Material:', [
            ('-- wählen --', None),
            ('Kupfer Cu',    0.00393),
            ('Aluminium Al', 0.00403),
        ])
    """
    return widgets.Dropdown(
        description=description,
        options=options,
        style={'description_width': '140px'},
        layout=widgets.Layout(width='340px'),
    )


# ------------------------------------------------------------
# make_toggle() – Einheitlicher ToggleButtons
# ------------------------------------------------------------
def make_toggle(description, options, button_width='140px'):
    """
    Erstellt einheitliche ipywidgets ToggleButtons.

    Parameter:
        description   – Beschriftung
        options       – Liste der Optionen als Strings
        button_width  – Breite je Button (default: '140px')

    Beispiel:
        mode = make_toggle('Schaltung:', ['Reihenschaltung', 'Parallelschaltung'])
        mode.observe(calc_func, names='value')
    """
    return widgets.ToggleButtons(
        description=description,
        options=options,
        style={
            'description_width': '140px',
            'button_width': button_width,
        },
    )


# ------------------------------------------------------------
# Shockley – Diodenstrom (für 2_Elektronik.ipynb)
# ------------------------------------------------------------
def shockley(V, IS=1e-12, n=1.0, T_celsius=27.0):
    """
    Shockley-Gleichung: Diodenstrom I = IS · (e^(V / n·VT) − 1)

    Parameter:
        V         – Diodenspannung in Volt
        IS        – Sättigungssperrstrom (typ. 1e-12 A für Si)
        n         – Idealitätsfaktor (1 = ideal, 1..2 real)
        T_celsius – Temperatur in °C (default 27°C = 300 K)

    Rückgabe:
        Diodenstrom I in Ampere

    Beispiel:
        I = shockley(0.6)         → ~4.4 mA  (Si-Diode, 27°C)
        I = shockley(0.7, n=1.5)  → mit Idealitätsfaktor 1.5
    """
    VT = vt(T_celsius)
    return IS * (math.exp(V / (n * VT)) - 1)


# ------------------------------------------------------------
# vt() – Thermospannung
# ------------------------------------------------------------
def vt(T_celsius=27.0):
    """
    Thermospannung VT = k·T / q

    Parameter:
        T_celsius – Temperatur in °C (default 27°C)

    Rückgabe:
        VT in Volt (typ. 25.85 mV bei 27°C)

    Beispiel:
        vt(27)  → 0.02585 V  ≈ 25.85 mV
        vt(100) → 0.03225 V  ≈ 32.25 mV
    """
    T_kelvin = T_celsius + 273.15
    return K_B * T_kelvin / Q_E