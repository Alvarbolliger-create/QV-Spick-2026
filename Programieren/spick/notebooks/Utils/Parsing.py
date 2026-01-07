import re

SI_PREFIXES = {
    'p': 1e-12,
    'n': 1e-9,
    'u': 1e-6,   # micro
    'µ': 1e-6,   # optional
    'm': 1e-3,
    '':  1.0,
    'k': 1e3,
    'M': 1e6,
    'G': 1e9
}

def parse_value(val_str):
    """
    Parst Zahlen mit optionalem SI-Präfix:
    z.B. 10k, 4.7u, 100n, 1M
    """
    if val_str is None:
        return None

    val_str = val_str.strip()
    if val_str == "":
        return None

    # Zahl + optionales Präfix
    match = re.fullmatch(r'([-+]?\d*\.?\d+)\s*([pnumkMGµ]?)', val_str)
    if not match:
        raise ValueError(f"Ungültiger Wert: '{val_str}'")

    value, prefix = match.groups()
    return float(value) * SI_PREFIXES[prefix]