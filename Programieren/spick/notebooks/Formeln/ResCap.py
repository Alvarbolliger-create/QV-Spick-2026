import numpy as np

# ---- RC-Kreis Funktionen ----
def rc_tau(R, C):
    """Berechnet die Zeitkonstante tau eines RC-Kreises"""
    return R * C

def u_lade(t, R, C, U0=5):
    """Ladespannung am Kondensator"""
    tau = rc_tau(R, C)
    return U0 * (1 - np.exp(-t / tau))

def u_entlade(t, R, C, U0=5):
    """Entladungsspannung am Kondensator"""
    tau = rc_tau(R, C)
    return U0 * np.exp(-t / tau)

def i_lade(t, R, C, U0=5):
    """Ladestrom"""
    tau = rc_tau(R, C)
    return (U0 / R) * np.exp(-t / tau)

def q_lade(C, U):
    """
    Berechnet die gespeicherte Ladung auf einem Kondensator.
    C: Kapazität in Farad
    U: Spannung in Volt
    Rückgabe: Q in Coulomb
    """
    if C is None or U is None:
        raise ValueError("C und U müssen angegeben werden")
    return C * U