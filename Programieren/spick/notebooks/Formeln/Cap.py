# Formeln/Con.py
def kapazitaet(A, d, eps_r, eps0=8.854e-12):
    """
    Berechnet die Kapazität eines Plattenkondensators.
    Mindestens eines der Felder (C, A, d, eps_r) muss None sein, um berechnet zu werden.
    """
    if None in (A, d, eps_r):
        raise ValueError("A, d und eps_r dürfen nicht None sein für direkte Kapazitätsberechnung")
    C = eps_r * eps0 * A / d
    return C

def platte_berechnen(C=None, A=None, d=None, eps_r=None, eps0=8.854e-12):
    """
    Berechnet das jeweils fehlende Feld, wenn eines None ist.
    Rückgabe: Dictionary mit allen Werten
    """
    # Zählen wie viele None
    none_count = sum(x is None for x in [C, A, d, eps_r])
    if none_count != 1:
        raise ValueError("Genau ein Wert muss None sein, um berechnet zu werden")

    if C is None:
        C = eps_r * eps0 * A / d
    elif A is None:
        A = C * d / (eps_r * eps0)
    elif d is None:
        d = eps_r * eps0 * A / C
    elif eps_r is None:
        eps_r = C * d / (eps0 * A)

    return {"C": C, "A": A, "d": d, "eps_r": eps_r}
