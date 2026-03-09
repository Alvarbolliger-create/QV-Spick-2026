# ============================================================
# calc.py – Reine Berechnungsfunktionen (ohne Widgets)
# Elektrotechnik-Spick | Elektroniker EFZ
# ============================================================
# Alle Funktionen:
#   - nehmen Python-Zahlen entgegen (bereits geparst mit p())
#   - geben ein dict mit ALLEN Ein- und Ausgabewerten zurück
#   - werfen ValueError bei ungültigen Eingaben
#   - werfen ZeroDivisionError bei Division durch Null
# ============================================================

import math
from utils import check_inputs, EPS0, MU0


# ============================================================
# KAPITEL 1: Widerstand
# ============================================================

def kirchhoff_knoten(stroeme: list) -> dict:
    """
    1.0a Knotenregel (KCL): Summe aller Ströme = 0
    stroeme: Liste mit Werten oder None (max. 1x None = Unbekannte)
    Vorzeichen: zufliesend positiv, abfliessend negativ.
    """
    vals    = [v for v in stroeme if v is not None]
    unknown = [i for i, v in enumerate(stroeme) if v is None]
    if not vals:
        raise ValueError("Mindestens 1 Strom eingeben")
    total = sum(vals)
    result = {"summe_bekannt": total, "n_unbekannt": len(unknown)}
    if len(unknown) == 1:
        missing = -total
        result["I_unbekannt"] = missing
        result["index"]       = unknown[0]
        result["richtung"]    = "zufliessend" if missing > 0 else "abfliessend"
        result["kcl_ok"]      = True
    elif len(unknown) == 0:
        result["kcl_ok"] = abs(total) < 1e-12
        result["fehler"] = total if not result["kcl_ok"] else 0.0
    else:
        raise ValueError(f"Zu viele Unbekannte ({len(unknown)}), max. 1 leer lassen")
    return result


def kirchhoff_masche(spannungen: list) -> dict:
    """
    1.0b Maschenregel (KVL): Summe aller Spannungen = 0
    spannungen: Liste mit Werten oder None (max. 1x None = Unbekannte)
    Vorzeichen: Quelle in Umlaufrichtung positiv, Abfall negativ.
    """
    vals    = [v for v in spannungen if v is not None]
    unknown = [i for i, v in enumerate(spannungen) if v is None]
    if not vals:
        raise ValueError("Mindestens 1 Spannung eingeben")
    total = sum(vals)
    result = {"summe_bekannt": total, "n_unbekannt": len(unknown)}
    if len(unknown) == 1:
        missing = -total
        result["U_unbekannt"] = missing
        result["index"]       = unknown[0]
        result["kvl_ok"]      = True
    elif len(unknown) == 0:
        result["kvl_ok"] = abs(total) < 1e-9
        result["fehler"] = total if not result["kvl_ok"] else 0.0
    else:
        raise ValueError(f"Zu viele Unbekannte ({len(unknown)}), max. 1 leer lassen")
    return result


def ohm(U=None, R=None, I=None) -> dict:
    """
    1.1 Ohmsches Gesetz: U = R · I
    Ein Feld None lassen → wird berechnet. Alle 3 Werte werden zurückgegeben.
    """
    n, miss = check_inputs({"U": U, "R": R, "I": I})
    if n == 0:
        raise ValueError("Ein Feld leer lassen!")
    if n > 1:
        raise ValueError("Nur ein Feld leer lassen!")
    m = miss[0]
    if m == "U":
        U = R * I
    elif m == "R":
        if I == 0: raise ZeroDivisionError("I darf nicht 0 sein")
        R = U / I
    else:
        if R == 0: raise ZeroDivisionError("R darf nicht 0 sein")
        I = U / R
    return {"U": U, "R": R, "I": I, "berechnet": m}


def leistung(P=None, U=None, I=None, R=None) -> dict:
    """
    1.2 Elektrische Leistung: P = U·I = I²·R = U²/R
    Genau 2 Felder eingeben → alle 4 Grössen werden zurückgegeben.
    """
    formel = ""
    if P is None and U is not None and I is not None:
        P = U * I;                         formel = "P=U·I"
    elif U is None and P is not None and I is not None:
        if I == 0: raise ZeroDivisionError("I darf nicht 0 sein")
        U = P / I;                         formel = "U=P/I"
    elif I is None and P is not None and U is not None:
        if U == 0: raise ZeroDivisionError("U darf nicht 0 sein")
        I = P / U;                         formel = "I=P/U"
    elif P is None and I is not None and R is not None:
        P = I**2 * R;                      formel = "P=I²·R"
    elif R is None and P is not None and I is not None:
        if I == 0: raise ZeroDivisionError("I darf nicht 0 sein")
        R = P / I**2;                      formel = "R=P/I²"
    elif I is None and P is not None and R is not None:
        if R <= 0: raise ZeroDivisionError("R muss > 0 sein")
        I = math.sqrt(P / R);              formel = "I=sqrt(P/R)"
    elif P is None and U is not None and R is not None:
        if R == 0: raise ZeroDivisionError("R darf nicht 0 sein")
        P = U**2 / R;                      formel = "P=U2/R"
    elif R is None and P is not None and U is not None:
        if P == 0: raise ZeroDivisionError("P darf nicht 0 sein")
        R = U**2 / P;                      formel = "R=U2/P"
    elif U is None and P is not None and R is not None:
        if R <= 0: raise ZeroDivisionError("R muss > 0 sein")
        U = math.sqrt(P * R);              formel = "U=sqrt(P*R)"
    else:
        raise ValueError("Genau 2 Werte eingeben (z.B. U+I, I+R, U+R)")
    if R is None and I is not None and I != 0:
        R = P / I**2
    if R is None and U is not None and P is not None and P != 0:
        R = U**2 / P
    if I is None and U is not None and R is not None and R != 0:
        I = U / R
    if U is None and P is not None and I is not None and I != 0:
        U = P / I
    return {"P": P, "U": U, "I": I, "R": R, "formel": formel}


def reihenschaltung(widerstaende: list, U_ges=None) -> dict:
    """
    1.3 Reihenschaltung: R_ges = R1 + R2 + ...
    widerstaende: Liste von Werten (None-Eintraege werden ignoriert)
    """
    rs = [r for r in widerstaende if r is not None]
    if not rs:
        raise ValueError("Mindestens 1 Widerstand eingeben")
    R_ges = sum(rs)
    result = {"R_ges": R_ges, "U_ges": U_ges}
    if U_ges is not None and R_ges > 0:
        result["I"] = U_ges / R_ges
        result["U_teile"] = [U_ges / R_ges * r for r in rs]
    return result


def parallelschaltung(widerstaende: list, U_ges=None) -> dict:
    """
    1.4 Parallelschaltung: 1/R_ges = 1/R1 + 1/R2 + ...
    """
    rs = [r for r in widerstaende if r is not None]
    if not rs:
        raise ValueError("Mindestens 1 Widerstand eingeben")
    if any(r == 0 for r in rs):
        raise ZeroDivisionError("Widerstand darf nicht 0 sein")
    R_ges = 1 / sum(1 / r for r in rs)
    result = {"R_ges": R_ges, "U_ges": U_ges}
    if U_ges is not None:
        result["I_ges"] = U_ges / R_ges
        result["I_teile"] = [U_ges / r for r in rs]
    return result


def temperaturkoeffizient(R20=None, alpha=None, T=None, RT=None) -> dict:
    """
    1.5 Temperaturabhaengigkeit: R_T = R20 * [1 + alpha * (T - 20)]
    """
    n, miss = check_inputs({"R20": R20, "alpha": alpha, "T": T, "RT": RT})
    if n != 1:
        raise ValueError("Genau ein Feld leer lassen!")
    m = miss[0]
    if m == "RT":
        RT = R20 * (1 + alpha * (T - 20))
    elif m == "R20":
        denom = 1 + alpha * (T - 20)
        if denom == 0: raise ZeroDivisionError("1 + a*(T-20) = 0")
        R20 = RT / denom
    elif m == "T":
        if alpha == 0: raise ZeroDivisionError("alpha darf nicht 0 sein")
        T = ((RT / R20) - 1) / alpha + 20
    elif m == "alpha":
        if T == 20: raise ZeroDivisionError("T darf nicht 20 Grad C sein")
        alpha = ((RT / R20) - 1) / (T - 20)
    return {"R20": R20, "alpha": alpha, "T": T, "RT": RT, "berechnet": m}


def leitungswiderstand(R=None, rho=None, l=None, A=None) -> dict:
    """
    1.6 Leitungswiderstand: R = rho * l / A
    rho in Ohm*mm2/m, l in m, A in mm2
    """
    n, miss = check_inputs({"R": R, "rho": rho, "l": l, "A": A})
    if n != 1:
        raise ValueError("Genau ein Feld leer lassen!")
    m = miss[0]
    if m == "R":
        if A == 0: raise ZeroDivisionError("A darf nicht 0 sein")
        R = rho * l / A
    elif m == "rho":
        if l == 0: raise ZeroDivisionError("l darf nicht 0 sein")
        rho = R * A / l
    elif m == "l":
        if rho == 0: raise ZeroDivisionError("rho darf nicht 0 sein")
        l = R * A / rho
    elif m == "A":
        if R == 0: raise ZeroDivisionError("R darf nicht 0 sein")
        A = rho * l / R
    return {"R": R, "rho": rho, "l": l, "A": A, "berechnet": m}


def spannungsteiler(U_ges=None, R1=None, R2=None, U2=None) -> dict:
    """
    1.8 Spannungsteiler (unbelastet): U2 = U_ges * R2 / (R1 + R2)
    """
    n, miss = check_inputs({"U_ges": U_ges, "R1": R1, "R2": R2, "U2": U2})
    if n != 1:
        raise ValueError("Genau ein Feld leer lassen!")
    m = miss[0]
    if m == "U2":
        U2 = U_ges * R2 / (R1 + R2)
    elif m == "U_ges":
        if R2 == 0: raise ZeroDivisionError("R2 darf nicht 0 sein")
        U_ges = U2 * (R1 + R2) / R2
    elif m == "R1":
        if U2 == 0: raise ZeroDivisionError("U2 darf nicht 0 sein")
        R1 = R2 * (U_ges - U2) / U2
    elif m == "R2":
        denom = U_ges - U2
        if denom == 0: raise ZeroDivisionError("U_ges = U2, kein Teiler moeglich")
        R2 = R1 * U2 / denom
    U1 = U_ges - U2
    I  = U_ges / (R1 + R2) if (R1 + R2) != 0 else None
    return {"U_ges": U_ges, "R1": R1, "R2": R2, "U2": U2,
            "U1": U1, "I": I, "berechnet": m}


def spannungsteiler_belastet(U_ges, R1, R2, RL=None) -> dict:
    """
    1.12 Belasteter Spannungsteiler.
    RL = None → nur unbelasteter Fall.
    Gibt beide Fälle zurück (unbelastet immer, belastet wenn RL vorhanden).
    """
    if R1 + R2 == 0: raise ZeroDivisionError("R1 + R2 darf nicht 0 sein")
    # Unbelastet
    U2_unb = U_ges * R2 / (R1 + R2)
    I_unb  = U_ges / (R1 + R2)
    result = {
        "U_ges": U_ges, "R1": R1, "R2": R2,
        "U2_unbelastet": U2_unb,
        "I_unbelastet":  I_unb,
    }
    if RL is not None:
        if RL <= 0: raise ValueError("R_L muss > 0 sein")
        R2L   = R2 * RL / (R2 + RL)
        U2_b  = U_ges * R2L / (R1 + R2L)
        I_ges = U_ges / (R1 + R2L)
        I_R2  = U2_b / R2
        I_RL  = U2_b / RL
        abw   = (U2_unb - U2_b) / U2_unb * 100 if U2_unb != 0 else 0
        result.update({
            "RL": RL, "R2_parallel_RL": R2L,
            "U2_belastet":    U2_b,
            "I_ges_belastet": I_ges,
            "I_R2":           I_R2,
            "I_RL":           I_RL,
            "abweichung_pct": abw,
            "stabil":         RL >= 10 * R2,
        })
    return result


def leitwert(R=None, G=None) -> dict:
    """1.9 Leitwert: G = 1/R"""
    if R is not None and G is None:
        if R == 0: raise ZeroDivisionError("R darf nicht 0 sein")
        G = 1 / R
    elif G is not None and R is None:
        if G == 0: raise ZeroDivisionError("G darf nicht 0 sein")
        R = 1 / G
    else:
        raise ValueError("Genau ein Feld (R oder G) leer lassen!")
    return {"R": R, "G": G}


def stromdichte(I=None, A=None, J=None) -> dict:
    """1.10 Stromdichte: J = I / A"""
    n, miss = check_inputs({"I": I, "A": A, "J": J})
    if n != 1:
        raise ValueError("Genau ein Feld leer lassen!")
    m = miss[0]
    if m == "J":
        if A == 0: raise ZeroDivisionError("A darf nicht 0 sein")
        J = I / A
    elif m == "A":
        if J == 0: raise ZeroDivisionError("J darf nicht 0 sein")
        A = I / J
    else:
        I = J * A
    return {"I": I, "A": A, "J": J, "berechnet": m}


def thevenin_aus_ull_ik(Ull, Ik, R_last=None) -> dict:
    """
    1.11 Thevenin/Norton aus Leerlaufspannung + Kurzschlussstrom.
    """
    if Ik == 0: raise ZeroDivisionError("I_k darf nicht 0 sein")
    Uth   = Ull
    Rth   = Ull / Ik
    IN    = Ik
    P_max = Uth**2 / (4 * Rth)
    result = {"Ull": Ull, "Ik": Ik, "Uth": Uth, "Rth": Rth, "IN": IN, "P_max": P_max}
    if R_last is not None:
        U_last = Uth * R_last / (Rth + R_last)
        I_last = Uth / (Rth + R_last)
        result.update({"R_last": R_last, "U_last": U_last,
                        "I_last": I_last, "P_last": U_last * I_last})
    return result


def thevenin_aus_spannungsteiler(U_ges, R1, R2, R_last=None) -> dict:
    """1.11 Thevenin aus Spannungsteiler-Schaltung."""
    if R1 + R2 == 0: raise ZeroDivisionError("R1 + R2 = 0")
    Uth = U_ges * R2 / (R1 + R2)
    Rth = R1 * R2 / (R1 + R2)
    IN  = Uth / Rth if Rth > 0 else 0
    P_max = Uth**2 / (4 * Rth) if Rth > 0 else 0
    result = {"U_ges": U_ges, "R1": R1, "R2": R2,
              "Uth": Uth, "Rth": Rth, "IN": IN, "P_max": P_max}
    if R_last is not None:
        U_last = Uth * R_last / (Rth + R_last)
        I_last = Uth / (Rth + R_last)
        result.update({"R_last": R_last, "U_last": U_last, "I_last": I_last})
    return result


# ============================================================
# KAPITEL 2: Kondensatoren
# ============================================================

def kondensator_qcu(Q=None, C=None, U=None) -> dict:
    """2.1 Kondensator Grundgroessen: Q = C * U"""
    n, miss = check_inputs({"Q": Q, "C": C, "U": U})
    if n != 1:
        raise ValueError("Genau ein Feld leer lassen!")
    m = miss[0]
    if m == "Q":
        Q = C * U
    elif m == "C":
        if U == 0: raise ZeroDivisionError("U darf nicht 0 sein")
        C = Q / U
    else:
        if C == 0: raise ZeroDivisionError("C darf nicht 0 sein")
        U = Q / C
    W = 0.5 * C * U**2
    return {"Q": Q, "C": C, "U": U, "W": W, "berechnet": m}


def plattenkondensator(C=None, A=None, d=None, er=None) -> dict:
    """2.2 Plattenkondensator: C = eps0 * er * A / d"""
    n, miss = check_inputs({"C": C, "A": A, "d": d, "er": er})
    if n != 1:
        raise ValueError("Genau ein Feld leer lassen!")
    m = miss[0]
    if m == "C":
        if d == 0: raise ZeroDivisionError("d darf nicht 0 sein")
        C = EPS0 * er * A / d
    elif m == "A":
        if d == 0 or er == 0: raise ZeroDivisionError
        A = C * d / (EPS0 * er)
    elif m == "d":
        if C == 0: raise ZeroDivisionError("C darf nicht 0 sein")
        d = EPS0 * er * A / C
    elif m == "er":
        if A == 0: raise ZeroDivisionError("A darf nicht 0 sein")
        er = C * d / (EPS0 * A)
    return {"C": C, "A": A, "d": d, "er": er, "berechnet": m}


def kondensator_schaltung(kapazitaeten: list, parallel: bool, U=None) -> dict:
    """2.3 Kondensatoren in Reihe oder Parallel."""
    cs = [c for c in kapazitaeten if c is not None]
    if not cs:
        raise ValueError("Mindestens 1 Kondensator eingeben")
    if parallel:
        C_ges = sum(cs)
        result = {"C_ges": C_ges, "schaltung": "parallel", "U": U}
        if U:
            result["Q_ges"] = C_ges * U
            result["Q_teile"] = [c * U for c in cs]
    else:
        if any(c == 0 for c in cs): raise ZeroDivisionError
        C_ges = 1 / sum(1 / c for c in cs)
        result = {"C_ges": C_ges, "schaltung": "reihe", "U": U}
        if U:
            Q = C_ges * U
            result["Q"] = Q
            result["U_teile"] = [Q / c for c in cs]
    return result


def rc_zeitkonstante(R=None, C=None, tau=None) -> dict:
    """2.4a RC-Zeitkonstante: tau = R * C"""
    n, miss = check_inputs({"R": R, "C": C, "tau": tau})
    if n != 1:
        raise ValueError("Genau ein Feld leer lassen!")
    m = miss[0]
    if m == "tau":
        tau = R * C
    elif m == "R":
        if C == 0: raise ZeroDivisionError
        R = tau / C
    else:
        if R == 0: raise ZeroDivisionError
        C = tau / R
    return {"R": R, "C": C, "tau": tau, "berechnet": m,
            "ladetabelle": {n: (1 - math.exp(-n)) * 100 for n in range(1, 6)}}


def rc_zeitverlauf(R, C, U0, t, laden=True) -> dict:
    """2.4b RC-Spannung zu Zeitpunkt t."""
    if R <= 0 or C <= 0: raise ValueError("R und C muessen > 0 sein")
    tau = R * C
    if laden:
        Uc = U0 * (1 - math.exp(-t / tau))
        I  = (U0 / R) * math.exp(-t / tau)
    else:
        Uc = U0 * math.exp(-t / tau)
        I  = (U0 / R) * math.exp(-t / tau)
    return {"R": R, "C": C, "U0": U0, "t": t, "laden": laden,
            "tau": tau, "Uc": Uc, "Ur": U0 - Uc, "I": I, "t_tau": t / tau}


def kapazitiver_widerstand(Xc=None, f=None, C=None) -> dict:
    """2.5 Kapazitiver Widerstand: X_C = 1 / (2*pi*f*C)"""
    n, miss = check_inputs({"Xc": Xc, "f": f, "C": C})
    if n != 1:
        raise ValueError("Genau ein Feld leer lassen!")
    m = miss[0]
    if m == "Xc":
        if f == 0 or C == 0: raise ZeroDivisionError
        Xc = 1 / (2 * math.pi * f * C)
    elif m == "f":
        if Xc == 0 or C == 0: raise ZeroDivisionError
        f = 1 / (2 * math.pi * Xc * C)
    else:
        if Xc == 0 or f == 0: raise ZeroDivisionError
        C = 1 / (2 * math.pi * f * Xc)
    return {"Xc": Xc, "f": f, "C": C, "omega": 2 * math.pi * f, "berechnet": m}


def rc_impedanz(R, f, C, U=None) -> dict:
    """2.6 RC-Reihenschaltung Impedanz: Z = sqrt(R^2 + Xc^2)"""
    if f == 0 or C == 0: raise ZeroDivisionError
    Xc  = 1 / (2 * math.pi * f * C)
    Z   = math.sqrt(R**2 + Xc**2)
    phi = -math.degrees(math.atan(Xc / R)) if R != 0 else -90.0
    result = {"R": R, "f": f, "C": C, "Xc": Xc, "Z": Z, "phi_grad": phi}
    if U:
        I = U / Z
        result.update({"U": U, "I": I, "U_R": I * R, "U_C": I * Xc})
    return result


def elektrisches_feld(E=None, U=None, d=None, er=None) -> dict:
    """2.7 Elektrisches Feld: E = U / d"""
    n, miss = check_inputs({"E": E, "U": U, "d": d})
    if n != 1:
        raise ValueError("Genau ein Feld leer lassen!")
    m = miss[0]
    if m == "E":
        if d == 0: raise ZeroDivisionError
        E = U / d
    elif m == "U":
        U = E * d
    else:
        if E == 0: raise ZeroDivisionError
        d = U / E
    result = {"E": E, "U": U, "d": d, "berechnet": m,
              "durchschlag_warnung": E > 3e6}
    if er:
        result["D"] = EPS0 * er * E
        result["er"] = er
    return result


# ============================================================
# KAPITEL 3: Spulen
# ============================================================

def selbstinduktion(UL=None, L=None, dI=None, dt=None) -> dict:
    """3.1 Selbstinduktionsspannung: U_L = L * dI/dt"""
    n, miss = check_inputs({"UL": UL, "L": L, "dI": dI, "dt": dt})
    if n != 1:
        raise ValueError("Genau ein Feld leer lassen!")
    m = miss[0]
    if m == "UL":
        if dt == 0: raise ZeroDivisionError
        UL = L * dI / dt
    elif m == "L":
        if dI == 0: raise ZeroDivisionError
        L = UL * dt / dI
    elif m == "dI":
        if L == 0: raise ZeroDivisionError
        dI = UL * dt / L
    else:
        if UL == 0: raise ZeroDivisionError
        dt = L * dI / UL
    W = 0.5 * L * dI**2
    return {"UL": UL, "L": L, "dI": dI, "dt": dt, "W": W, "berechnet": m}


def induktivitaet_spule(L=None, mur=None, N=None, A=None, l=None) -> dict:
    """3.2 Induktivitaet Zylinderspule: L = mu0*mur*N^2*A/l"""
    n, miss = check_inputs({"L": L, "mur": mur, "N": N, "A": A, "l": l})
    if n != 1:
        raise ValueError("Genau ein Feld leer lassen!")
    m = miss[0]
    if m == "L":
        if l == 0: raise ZeroDivisionError
        L = MU0 * mur * N**2 * A / l
    elif m == "mur":
        if N == 0 or A == 0: raise ZeroDivisionError
        mur = L * l / (MU0 * N**2 * A)
    elif m == "N":
        denom = MU0 * mur * A
        if denom == 0: raise ZeroDivisionError
        N = math.sqrt(L * l / denom)
    elif m == "A":
        denom = MU0 * mur * N**2
        if denom == 0: raise ZeroDivisionError
        A = L * l / denom
    elif m == "l":
        if L == 0: raise ZeroDivisionError
        l = MU0 * mur * N**2 * A / L
    return {"L": L, "mur": mur, "N": N, "A": A, "l": l, "berechnet": m}


def spulen_schaltung(induktivitaeten: list, reihe: bool) -> dict:
    """3.3 Spulen in Reihe oder Parallel."""
    ls = [l for l in induktivitaeten if l is not None]
    if not ls:
        raise ValueError("Mindestens 1 Spule eingeben")
    if reihe:
        return {"L_ges": sum(ls), "schaltung": "reihe"}
    if any(l == 0 for l in ls): raise ZeroDivisionError
    return {"L_ges": 1 / sum(1 / l for l in ls), "schaltung": "parallel"}


def rl_zeitkonstante(L=None, R=None, tau=None) -> dict:
    """3.4a RL-Zeitkonstante: tau = L/R"""
    n, miss = check_inputs({"L": L, "R": R, "tau": tau})
    if n != 1:
        raise ValueError("Genau ein Feld leer lassen!")
    m = miss[0]
    if m == "tau":
        if R == 0: raise ZeroDivisionError
        tau = L / R
    elif m == "L":
        L = tau * R
    else:
        if tau == 0: raise ZeroDivisionError
        R = L / tau
    return {"L": L, "R": R, "tau": tau, "berechnet": m,
            "stromtabelle": {n: (1 - math.exp(-n)) * 100 for n in range(1, 6)}}


def rl_zeitverlauf(L, R, U0, t, einschalten=True) -> dict:
    """3.4b RL-Strom/Spannung zu Zeitpunkt t."""
    if R == 0 or L == 0: raise ZeroDivisionError
    tau   = L / R
    I_max = U0 / R
    if einschalten:
        I  = I_max * (1 - math.exp(-t / tau))
        UL = U0 * math.exp(-t / tau)
    else:
        I  = I_max * math.exp(-t / tau)
        UL = -U0 * math.exp(-t / tau)
    return {"L": L, "R": R, "U0": U0, "t": t, "einschalten": einschalten,
            "tau": tau, "I_max": I_max, "I": I, "UL": UL, "UR": I * R, "t_tau": t / tau}


def induktiver_widerstand(XL=None, f=None, L=None) -> dict:
    """3.5 Induktiver Widerstand: X_L = 2*pi*f*L"""
    n, miss = check_inputs({"XL": XL, "f": f, "L": L})
    if n != 1:
        raise ValueError("Genau ein Feld leer lassen!")
    m = miss[0]
    if m == "XL":
        XL = 2 * math.pi * f * L
    elif m == "f":
        if L == 0: raise ZeroDivisionError
        f = XL / (2 * math.pi * L)
    else:
        if f == 0: raise ZeroDivisionError
        L = XL / (2 * math.pi * f)
    return {"XL": XL, "f": f, "L": L, "omega": 2 * math.pi * f, "berechnet": m}


def rl_impedanz(R, f, L, U=None) -> dict:
    """3.6 RL-Reihenschaltung Impedanz: Z = sqrt(R^2 + XL^2)"""
    XL  = 2 * math.pi * f * L
    Z   = math.sqrt(R**2 + XL**2)
    phi = math.degrees(math.atan(XL / R)) if R != 0 else 90.0
    result = {"R": R, "f": f, "L": L, "XL": XL, "Z": Z, "phi_grad": phi}
    if U:
        I = U / Z
        result.update({"U": U, "I": I, "U_R": I * R, "U_L": I * XL})
    return result


def magnetisches_feld(N, I, l, mur=None, A=None) -> dict:
    """3.7 Magnetisches Feld: H = N*I/l, B = mu0*mur*H"""
    if l == 0: raise ZeroDivisionError
    Theta = N * I
    H     = Theta / l
    result = {"N": N, "I": I, "l": l, "Theta": Theta, "H": H}
    if mur:
        B = MU0 * mur * H
        result.update({"mur": mur, "B": B, "saettigung_warnung": mur > 1 and B > 1.5})
        if A:
            result.update({"A": A, "Phi": B * A})
    return result


# ============================================================
# KAPITEL 4: Wechselstrom - Leistung
# ============================================================

def effektivwert(signal: str, Up=None, Ue=None, D=None, U_dc=None) -> dict:
    """
    4.0 Effektiv-/Spitzenwert für verschiedene Signalformen.

    signal: 'sinus' | 'rechteck' | 'dreieck' | 'sinus_dc'
    Up     – Spitzenwert (Amplitude)
    Ue     – Effektivwert  (einer der beiden leer lassen)
    D      – Tastverhältnis 0…1 (nur 'rechteck')
    U_dc   – DC-Offset in V   (nur 'sinus_dc')

    Rückgabe: dict mit Up, Ue, Gleichrichtwert, Scheitelfaktor, Formfaktor
    """
    result = {"signal": signal}

    if signal == "sinus":
        if Up is not None:
            Ue = Up / math.sqrt(2)
        elif Ue is not None:
            Up = Ue * math.sqrt(2)
        else:
            raise ValueError("Up oder Ue eingeben")
        Ub = 2 * Up / math.pi
        result.update({
            "Up": Up, "Ue": Ue, "Ub": Ub,
            "k_s": math.sqrt(2),
            "k_f": math.pi / (2 * math.sqrt(2)),
        })

    elif signal == "rechteck":
        if D is None or not (0 < D <= 1):
            raise ValueError("Tastverhältnis D (0 < D ≤ 1) eingeben")
        if Up is not None:
            Ue = Up * math.sqrt(D)
        elif Ue is not None:
            Up = Ue / math.sqrt(D)
        else:
            raise ValueError("Up oder Ue eingeben")
        result.update({
            "Up": Up, "Ue": Ue, "D": D,
            "k_s": 1 / math.sqrt(D),
        })

    elif signal == "dreieck":
        if Up is not None:
            Ue = Up / math.sqrt(3)
        elif Ue is not None:
            Up = Ue * math.sqrt(3)
        else:
            raise ValueError("Up oder Ue eingeben")
        result.update({
            "Up": Up, "Ue": Ue,
            "k_s": math.sqrt(3),
            "k_f": 2 / math.sqrt(3),
        })

    elif signal == "sinus_dc":
        if U_dc is None:
            raise ValueError("U_DC eingeben")
        if Up is not None:
            Uac_eff = Up / math.sqrt(2)
        elif Ue is not None:
            Uac_eff = Ue
            Up = Ue * math.sqrt(2)
        else:
            raise ValueError("Up oder Ue (AC-Anteil) eingeben")
        Ue_ges = math.sqrt(U_dc**2 + Uac_eff**2)
        result.update({
            "Up": Up, "Uac_eff": Uac_eff,
            "U_dc": U_dc, "Ue_gesamt": Ue_ges,
        })
    else:
        raise ValueError("signal muss 'sinus', 'rechteck', 'dreieck' oder 'sinus_dc' sein")

    return result


def ac_leistung(U=None, I=None, phi_grad=None, cos_phi=None,
                S=None, P=None, Q=None) -> dict:
    """
    4.1 Wechselstrom-Leistung: S, P, Q, cos phi
    Mindestens 2 unabhaengige Groessen eingeben.
    """
    if phi_grad is not None and cos_phi is None:
        cos_phi = math.cos(math.radians(phi_grad))
    elif cos_phi is not None and phi_grad is None:
        phi_grad = math.degrees(math.acos(max(-1, min(1, cos_phi))))
    if S is None and U is not None and I is not None:
        S = U * I
    if S is not None and cos_phi is not None:
        if P is None: P = S * cos_phi
        if Q is None: Q = S * math.sqrt(max(0, 1 - cos_phi**2))
    if S is None and P is not None and Q is not None:
        S = math.sqrt(P**2 + Q**2)
    if cos_phi is None and P is not None and S is not None and S > 0:
        cos_phi = P / S
        phi_grad = math.degrees(math.acos(max(-1, min(1, cos_phi))))
    if U is None and S is not None and I is not None and I > 0:
        U = S / I
    if I is None and S is not None and U is not None and U > 0:
        I = S / U
    if S is None:
        raise ValueError("Mindestens U+I, S, oder P+Q eingeben")
    return {"S": S, "P": P, "Q": Q, "cos_phi": cos_phi,
            "phi_grad": phi_grad, "U": U, "I": I}


def blindstromkompensation(P, U, f, cos1, cos2) -> dict:
    """4.2 Kompensationskondensator berechnen."""
    if not (0 < cos1 <= 1 and 0 < cos2 <= 1):
        raise ValueError("cos phi muss zwischen 0 und 1 liegen")
    if U == 0 or f == 0: raise ZeroDivisionError
    omega  = 2 * math.pi * f
    phi1   = math.acos(cos1)
    phi2   = math.acos(cos2)
    Q1     = P * math.tan(phi1)
    Q2     = P * math.tan(phi2)
    Q_komp = Q1 - Q2
    C      = Q_komp / (omega * U**2)
    S1, S2 = P / cos1, P / cos2
    I1, I2 = S1 / U, S2 / U
    return {"P": P, "U": U, "f": f, "cos1": cos1, "cos2": cos2,
            "C": C, "Q_komp": Q_komp, "Q1": Q1, "Q2": Q2,
            "S1": S1, "S2": S2, "I1": I1, "I2": I2,
            "strom_reduktion_pct": (I1 - I2) / I1 * 100}


# ============================================================
# KAPITEL 5: RLC-Schwingkreise
# ============================================================

def resonanzfrequenz(f0=None, L=None, C=None) -> dict:
    """5.1 Resonanzfrequenz: f0 = 1 / (2*pi*sqrt(L*C))"""
    n, miss = check_inputs({"f0": f0, "L": L, "C": C})
    if n != 1:
        raise ValueError("Genau ein Feld leer lassen!")
    m = miss[0]
    if m == "f0":
        if L <= 0 or C <= 0: raise ValueError("L und C muessen > 0 sein")
        f0 = 1 / (2 * math.pi * math.sqrt(L * C))
    elif m == "L":
        if f0 == 0 or C == 0: raise ZeroDivisionError
        L = 1 / (4 * math.pi**2 * f0**2 * C)
    else:
        if f0 == 0 or L == 0: raise ZeroDivisionError
        C = 1 / (4 * math.pi**2 * f0**2 * L)
    omega0 = 2 * math.pi * f0
    XL_res = omega0 * L if L else None
    return {"f0": f0, "L": L, "C": C, "omega0": omega0,
            "XL_res": XL_res, "berechnet": m}


def reihenschwingkreis(R, L, C, U=None, f_ein=None) -> dict:
    """5.2 Reihenschwingkreis: f0, Q, Df, Z bei beliebiger Frequenz."""
    if L <= 0 or C <= 0: raise ValueError("L und C muessen > 0 sein")
    f0     = 1 / (2 * math.pi * math.sqrt(L * C))
    omega0 = 2 * math.pi * f0
    Q      = (1 / R) * math.sqrt(L / C)
    df     = f0 / Q
    f      = f_ein if f_ein else f0
    omega  = 2 * math.pi * f
    XL     = omega * L
    XC     = 1 / (omega * C)
    Z      = math.sqrt(R**2 + (XL - XC)**2)
    result = {"R": R, "L": L, "C": C,
              "f0": f0, "Q": Q, "df": df,
              "f_u": f0 - df/2, "f_o": f0 + df/2,
              "XL": XL, "XC": XC, "Z": Z,
              "charakter": "induktiv" if XL > XC else ("kapazitiv" if XL < XC else "resonanz")}
    if U:
        I  = U / Z
        result.update({"U": U, "I": I, "U_R": I*R, "U_L": I*XL, "U_C": I*XC})
        if f_ein is None:
            result["U_L_resonanz"] = Q * U
    return result


def parallelschwingkreis(R, L, C, U=None) -> dict:
    """5.3 Parallelschwingkreis."""
    if L <= 0 or C <= 0: raise ValueError("L und C muessen > 0 sein")
    omega0_ideal = 1 / math.sqrt(L * C)
    radicand = 1 / (L * C) - (R / L)**2
    if radicand <= 0:
        raise ValueError("R zu gross - kein Schwingen moeglich")
    omega0 = math.sqrt(radicand)
    f0     = omega0 / (2 * math.pi)
    XL     = omega0_ideal * L
    Q      = XL / R
    Rp     = Q**2 * R
    df     = f0 / Q
    result = {"R": R, "L": L, "C": C,
              "f0": f0, "Q": Q, "Rp": Rp, "df": df,
              "f_u": f0 - df/2, "f_o": f0 + df/2,
              "warnung_niedrige_guete": Q < 10}
    if U:
        I_ges = U / Rp
        result.update({"U": U, "I_ges": I_ges, "I_kreis": Q * I_ges})
    return result


def guete_bandbreite(f0=None, Q=None, df=None) -> dict:
    """5.4 Guete und Bandbreite: Q = f0 / Df"""
    n, miss = check_inputs({"f0": f0, "Q": Q, "df": df})
    if n != 1:
        raise ValueError("Genau ein Feld leer lassen!")
    m = miss[0]
    if m == "df":
        if Q == 0: raise ZeroDivisionError
        df = f0 / Q
    elif m == "Q":
        if df == 0: raise ZeroDivisionError
        Q = f0 / df
    else:
        f0 = Q * df
    return {"f0": f0, "Q": Q, "df": df,
            "f_u": f0 - df/2, "f_o": f0 + df/2, "berechnet": m}


# ============================================================
# KAPITEL 6: Dezibel
# ============================================================

def dezibel(x1=None, x2=None, dB=None, leistung_db=False) -> dict:
    """
    6.1 Dezibel-Rechner.
    leistung_db=True -> Faktor 10, sonst Faktor 20 (Spannung/Strom)
    """
    factor = 10 if leistung_db else 20
    if x1 is not None and x2 is not None:
        if x1 <= 0 or x2 <= 0: raise ValueError("x1 und x2 muessen > 0 sein")
        dB = factor * math.log10(x2 / x1)
    elif x1 is not None and dB is not None:
        if x1 <= 0: raise ValueError
        x2 = x1 * 10**(dB / factor)
    elif x2 is not None and dB is not None:
        if x2 <= 0: raise ValueError
        x1 = x2 / 10**(dB / factor)
    else:
        raise ValueError("Zwei Felder eingeben (x1+x2, x1+dB, oder x2+dB)")
    return {"x1": x1, "x2": x2, "dB": dB, "leistung_db": leistung_db}


def kettendaempfung(stufen_db: list, U_ein=None) -> dict:
    """6.3 Kettendaempfung: Summe der dB-Werte."""
    stufen = [d for d in stufen_db if d is not None]
    if not stufen:
        raise ValueError("Mindestens eine Stufe eingeben")
    total    = sum(stufen)
    ratio_U  = 10**(total / 20)
    ratio_P  = 10**(total / 10)
    result   = {"total_db": total, "ratio_U": ratio_U, "ratio_P": ratio_P, "U_ein": U_ein}
    if U_ein is not None:
        result["U_aus"] = U_ein * ratio_U
    return result


# ============================================================
# KAPITEL 7: Filter
# ============================================================

def rc_tiefpass(R, C, f=None, U0=None) -> dict:
    """7.1 Passiver RC-Tiefpass: fg = 1/(2*pi*R*C)"""
    if R == 0 or C == 0: raise ZeroDivisionError
    fg  = 1 / (2 * math.pi * R * C)
    tau = R * C
    result = {"R": R, "C": C, "fg": fg, "tau": tau}
    if f is not None:
        H     = 1 / math.sqrt(1 + (f / fg)**2)
        phi   = -math.degrees(math.atan(f / fg))
        dB_v  = 20 * math.log10(H)
        result.update({"f": f, "H": H, "dB": dB_v, "phi_grad": phi})
        if U0:
            result.update({"U0": U0, "U_aus": H * U0})
        result["bereich"] = "durchlass" if f < fg else ("grenzfrequenz" if f == fg else "sperr")
    return result


def rc_hochpass(R, C, f=None, U0=None) -> dict:
    """7.2 Passiver RC-Hochpass: fg = 1/(2*pi*R*C)"""
    if R == 0 or C == 0: raise ZeroDivisionError
    fg  = 1 / (2 * math.pi * R * C)
    result = {"R": R, "C": C, "fg": fg, "tau": R * C}
    if f is not None:
        if f == 0: raise ZeroDivisionError("f darf nicht 0 sein")
        ratio  = f / fg
        H      = ratio / math.sqrt(1 + ratio**2)
        phi    = math.degrees(math.atan(fg / f))
        dB_v   = 20 * math.log10(H)
        result.update({"f": f, "H": H, "dB": dB_v, "phi_grad": phi})
        if U0:
            result.update({"U0": U0, "U_aus": H * U0})
    return result


def rl_filter(R, L, f=None, tiefpass=True, U0=None) -> dict:
    """7.3 Passiver RL-Filter."""
    if L == 0: raise ZeroDivisionError
    fg     = R / (2 * math.pi * L)
    result = {"R": R, "L": L, "fg": fg, "tiefpass": tiefpass}
    if f is not None:
        ratio = f / fg
        if tiefpass:
            H   = 1 / math.sqrt(1 + ratio**2)
            phi = -math.degrees(math.atan(ratio))
        else:
            if f == 0: raise ZeroDivisionError
            H   = ratio / math.sqrt(1 + ratio**2)
            phi = math.degrees(math.atan(fg / f))
        dB_v = 20 * math.log10(H)
        result.update({"f": f, "H": H, "dB": dB_v, "phi_grad": phi})
        if U0:
            result.update({"U0": U0, "U_aus": H * U0})
    return result


def aktiver_tiefpass(R, C, Rf=None, R1=None, f=None, U0=None) -> dict:
    """7.4 Aktiver OPV-Tiefpass 1. Ordnung."""
    if R == 0 or C == 0: raise ZeroDivisionError
    fg = 1 / (2 * math.pi * R * C)
    if Rf is not None and R1 is not None:
        if R1 == 0: raise ZeroDivisionError
        A0 = 1 + Rf / R1
    elif Rf is None and R1 is None:
        A0 = 1.0
    else:
        raise ValueError("Entweder beide (Rf und R1) oder keinen eingeben")
    result = {"R": R, "C": C, "Rf": Rf, "R1": R1,
              "fg": fg, "A0": A0, "A0_dB": 20 * math.log10(A0) if A0 > 0 else 0}
    if f is not None:
        H     = A0 / math.sqrt(1 + (f / fg)**2)
        dB_v  = 20 * math.log10(H) if H > 0 else -999
        result.update({"f": f, "H": H, "dB": dB_v})
        if U0:
            result.update({"U0": U0, "U_aus": H * U0})
    return result


def aktiver_hochpass(R, C, Rf=None, R1=None, f=None, U0=None) -> dict:
    """7.5 Aktiver OPV-Hochpass 1. Ordnung."""
    if R == 0 or C == 0: raise ZeroDivisionError
    fg = 1 / (2 * math.pi * R * C)
    A0 = (1 + Rf / R1) if (Rf is not None and R1 is not None) else 1.0
    result = {"R": R, "C": C, "Rf": Rf, "R1": R1, "fg": fg, "A0": A0}
    if f is not None:
        if f == 0: raise ZeroDivisionError
        ratio  = f / fg
        H      = A0 * ratio / math.sqrt(1 + ratio**2)
        dB_v   = 20 * math.log10(H) if H > 0 else -999
        result.update({"f": f, "H": H, "dB": dB_v})
        if U0:
            result.update({"U0": U0, "U_aus": H * U0})
    return result


def sallen_key(R, C, Q, f=None, U0=None) -> dict:
    """7.7 Sallen-Key Tiefpass 2. Ordnung."""
    if R == 0 or C == 0: raise ZeroDivisionError
    fg   = 1 / (2 * math.pi * R * C)
    if Q == 0: raise ZeroDivisionError
    A0   = 3 - 1 / Q
    Rf_R1 = A0 - 1
    result = {"R": R, "C": C, "Q": Q,
              "fg": fg, "A0": A0, "Rf_R1": Rf_R1, "instabil": A0 >= 3 or Q > 50}
    if A0 >= 3:
        return result
    if f is not None:
        norm  = f / fg
        denom = math.sqrt((1 - norm**2)**2 + (norm / Q)**2)
        H     = A0 / denom if denom > 0 else 0
        dB_v  = 20 * math.log10(H) if H > 0 else -999
        result.update({"f": f, "H": H, "dB": dB_v})
        if U0:
            result.update({"U0": U0, "U_aus": H * U0})
    return result


def notch_filter(R, C, Q=None, f=None, U0=None) -> dict:
    """7.8 Notch-Filter (Twin-T)."""
    if R == 0 or C == 0: raise ZeroDivisionError
    f0 = 1 / (2 * math.pi * R * C)
    Qv = Q if Q else 0.25
    df = f0 / Qv
    result = {"R": R, "C": C, "Q": Qv, "f0": f0, "df": df}
    if f is not None:
        norm  = f / f0
        num   = abs(1 - norm**2)
        denom = math.sqrt((1 - norm**2)**2 + (norm / Qv)**2)
        H     = num / denom if denom > 0 else 0
        dB_v  = 20 * math.log10(H) if H > 1e-10 else -100
        result.update({"f": f, "H": H, "dB": dB_v})
        if U0:
            result.update({"U0": U0, "U_aus": H * U0})
    return result


# ============================================================
# KAPITEL 8: Transformator
# ============================================================

def uebersetzungsverhaeltnis(N1=None, N2=None, U1=None, U2=None,
                              I1=None, I2=None) -> dict:
    """8.1 Uebersetzungsverhaeltnis: ue = N1/N2 = U1/U2 = I2/I1"""
    ue = None
    result = {}
    if N1 and N2:
        ue = N1 / N2
        result["ue_N"] = ue
    if U1 and U2:
        ue_u = U1 / U2
        result["ue_U"] = ue_u
        if ue and abs(ue - ue_u) > 0.001:
            result["widerspruch"] = True
        ue = ue_u
    if I1 and I2:
        ue_i = I2 / I1
        result["ue_I"] = ue_i
        ue = ue_i
    if ue is None:
        raise ValueError("Mindestens ein Paar (N1+N2, U1+U2 oder I1+I2) eingeben")
    result["ue"] = ue
    result["typ"] = "abwaerts" if ue > 1 else ("aufwaerts" if ue < 1 else "1:1")
    result.update({"N1": N1, "N2": N2, "U1": U1, "U2": U2, "I1": I1, "I2": I2})
    if U1 and not U2: result["U2"] = U1 / ue
    if U2 and not U1: result["U1"] = U2 * ue
    if I1 and not I2: result["I2"] = I1 * ue
    if I2 and not I1: result["I1"] = I2 / ue
    if N1 and not N2: result["N2"] = N1 / ue
    if N2 and not N1: result["N1"] = N2 * ue
    return result


def trafo_wirkungsgrad(P1=None, P2=None, eta_pct=None) -> dict:
    """8.2 Transformator-Wirkungsgrad: eta = P2/P1"""
    eta = eta_pct / 100 if eta_pct is not None else None
    n, miss = check_inputs({"P1": P1, "P2": P2, "eta": eta})
    if n != 1:
        raise ValueError("Genau ein Feld leer lassen!")
    m = miss[0]
    if m == "eta":
        if P1 == 0: raise ZeroDivisionError
        eta = P2 / P1
    elif m == "P1":
        if eta == 0: raise ZeroDivisionError
        P1 = P2 / eta
    else:
        P2 = P1 * eta
    return {"P1": P1, "P2": P2, "eta_pct": eta * 100, "P_verl": P1 - P2, "berechnet": m}


def widerstandstransformation(ue, R1=None, R2=None) -> dict:
    """8.3 Widerstandstransformation: R1' = ue^2 * R2"""
    if ue == 0: raise ZeroDivisionError
    result = {"ue": ue, "R1": R1, "R2": R2}
    if R2 is not None:
        result["R1_prim"] = ue**2 * R2
    if R1 is not None:
        result["R2_sek"] = R1 / ue**2
    if "R1_prim" not in result and "R2_sek" not in result:
        raise ValueError("R1 oder R2 eingeben")
    return result


def trafo_lastspannung(U2ll, Rcu2, I2=None, R_last=None) -> dict:
    """8.4 Spannungsabfall unter Last."""
    if I2 is None and R_last is not None:
        I2 = U2ll / (Rcu2 + R_last)
    elif I2 is None:
        raise ValueError("I2 oder R_last eingeben")
    dU   = I2 * Rcu2
    U2l  = U2ll - dU
    return {"U2ll": U2ll, "Rcu2": Rcu2, "I2": I2, "R_last": R_last,
            "dU": dU, "U2_last": U2l,
            "P2": U2l * I2, "P_cu": I2**2 * Rcu2,
            "abfall_pct": dU / U2ll * 100}

def spartrafo(U1=None, U2=None, N_ges=None, N2=None, I2=None) -> dict:
    """
    8.5 Spartrafo-Berechnung.
    ü = N_ges/N2 = U1/U2
    Liefert Ströme, Differenzstrom im gemeinsamen Abschnitt und Kupfereinsparung.
    Mindestens ein Spannungs- oder Windungspaar eingeben.
    """
    ue = None
    result = {}

    if N_ges is not None and N2 is not None:
        if N2 == 0: raise ZeroDivisionError("N2 darf nicht 0 sein")
        ue = N_ges / N2
        result["ue_N"] = ue
    if U1 is not None and U2 is not None:
        if U2 == 0: raise ZeroDivisionError("U2 darf nicht 0 sein")
        ue_u = U1 / U2
        result["ue_U"] = ue_u
        if ue is not None and abs(ue - ue_u) > 0.01:
            result["widerspruch"] = True
        ue = ue_u

    if ue is None:
        raise ValueError("N_ges+N2 oder U1+U2 eingeben")

    # Fehlende Spannung ergänzen
    if U1 is None and U2 is not None:
        U1 = U2 * ue
    if U2 is None and U1 is not None:
        U2 = U1 / ue

    result.update({
        "ue": ue, "U1": U1, "U2": U2,
        "typ": "abwaerts" if ue > 1 else ("aufwaerts" if ue < 1 else "1:1"),
    })

    if I2 is not None:
        I1      = I2 / ue
        I_diff  = abs(I2 - I1)
        S       = U2 * I2 if U2 else None
        # Kupfereinsparung: nur der induktiv übertragene Anteil braucht Wicklung
        # Durchgeleitete Leistung = min(U1,U2)*I2 → Einsparung vs. normaler Trafo
        if S and S > 0:
            S_induktiv = abs(U1 - U2) * I2 if ue > 1 else abs(U2 - U1) * I1
            einspar    = (1 - S_induktiv / S) * 100
        else:
            einspar = None
        result.update({
            "I2": I2, "I1": I1,
            "I_diff_gemeinsam": I_diff,
            "S": S,
            "kupfer_einsparung_pct": einspar,
        })

    return result


# ============================================================
# KAPITEL 9: Gleichrichter
# ============================================================

def spitzenwert_effektivwert(Up=None, Ue=None) -> dict:
    """9.1 Up = Ueff * sqrt(2)"""
    if Up is None and Ue is not None:
        Up = Ue * math.sqrt(2)
    elif Ue is None and Up is not None:
        Ue = Up / math.sqrt(2)
    else:
        raise ValueError("Genau ein Feld leer lassen!")
    return {"Up": Up, "Ue": Ue}


def einweggleichrichter(Ueff=None, Up=None, UF=0.7) -> dict:
    """9.2 Einweggleichrichter M1."""
    if Up is None and Ueff is None:
        raise ValueError("U_eff oder Up eingeben")
    if Up is None:   Up   = Ueff * math.sqrt(2)
    if Ueff is None: Ueff = Up / math.sqrt(2)
    U_avg      = Up / math.pi
    U_avg_real = U_avg - UF
    return {"Up": Up, "Ueff": Ueff, "UF": UF,
            "U_avg_ideal": U_avg, "U_avg_real": U_avg_real,
            "f_brumm_hz": 50, "warnung": U_avg_real < 0}


def brueckengleichrichter(Ueff=None, Up=None, UF=0.7) -> dict:
    """9.3 Brueckengleichrichter B2 (Graetz)."""
    if Up is None and Ueff is None:
        raise ValueError("U_eff oder Up eingeben")
    if Up is None:   Up   = Ueff * math.sqrt(2)
    if Ueff is None: Ueff = Up / math.sqrt(2)
    U_avg      = 2 * Up / math.pi
    U_avg_real = U_avg - 2 * UF
    return {"Up": Up, "Ueff": Ueff, "UF": UF,
            "U_avg_ideal": U_avg, "U_avg_real": U_avg_real,
            "UF_gesamt": 2 * UF, "U_sperr": Up,
            "f_brumm_hz": 100, "warnung": U_avg_real < 0}


def siebkondensator(C=None, I=None, U_br=None, f_brumm=100, Up=None) -> dict:
    """9.4 Siebkondensator: U_Br = I / (f*C)"""
    if C is not None and I is not None:
        U_br_calc = I / (f_brumm * C)
        result = {"C": C, "I": I, "f_brumm": f_brumm,
                  "U_br": U_br_calc, "berechnet": "U_br"}
        if Up:
            UDC = Up - U_br_calc / 2
            result.update({"Up": Up, "U_DC": UDC,
                            "welligkeit_pct": U_br_calc / UDC * 100 if UDC > 0 else 0})
        return result
    if U_br is not None and I is not None:
        if f_brumm == 0 or U_br == 0: raise ZeroDivisionError
        return {"C": I / (f_brumm * U_br), "I": I, "U_br": U_br,
                "f_brumm": f_brumm, "berechnet": "C"}
    if C is not None and U_br is not None:
        return {"C": C, "U_br": U_br, "f_brumm": f_brumm,
                "I_max": U_br * f_brumm * C, "berechnet": "I_max"}
    raise ValueError("C + I_Last, U_Br + I_Last, oder C + U_Br eingeben")


def netzteil_dimensionierung(U_DC, I_last, welligkeit_pct=1.0, UF=0.7) -> dict:
    """9.5 Komplettes Netzteil (B2)."""
    if I_last <= 0 or U_DC <= 0: raise ValueError
    f_brumm = 100
    w_fakt  = welligkeit_pct / 100
    U_br    = w_fakt * U_DC
    Up_min  = U_DC + U_br / 2 + 2 * UF
    U2_eff  = Up_min / math.sqrt(2)
    C_min   = I_last / (f_brumm * U_br)
    return {"U_DC": U_DC, "I_last": I_last, "welligkeit_pct": welligkeit_pct, "UF": UF,
            "U_br": U_br, "Up_min": Up_min, "U2_eff": U2_eff,
            "C_min": C_min, "U_festigkeit": Up_min * 1.5,
            "S_trafo": U2_eff * I_last * 1.5}

def gleichrichter_vergleich(Ueff, UF=0.7, I_last=None, C=None) -> dict:
    """
    9.6 Direktvergleich Einweggleichrichter M1 vs. Brückengleichrichter B2.

    Ueff   – Effektivwert der AC-Eingangsspannung [V]
    UF     – Flussspannung je Diode [V] (default 0.7)
    I_last – Laststrom [A] (optional, für Siebung)
    C      – Siebkondensator [F] (optional, für Brummspannung)

    Rückgabe: dict mit m1{} und b2{} Unterdict sowie Vergleichsfeldern
    """
    if Ueff <= 0: raise ValueError("Ueff muss > 0 sein")
    Up = Ueff * math.sqrt(2)

    # M1
    U_avg_m1  = Up / math.pi                   # ideal
    U_dc_m1   = U_avg_m1 - UF
    fBr_m1    = 50

    # B2
    U_avg_b2  = 2 * Up / math.pi               # ideal
    U_dc_b2   = U_avg_b2 - 2 * UF
    fBr_b2    = 100

    m1 = {"U_avg_ideal": U_avg_m1, "U_dc": U_dc_m1,
          "UF_gesamt": UF,  "f_brumm": fBr_m1, "n_dioden": 1}
    b2 = {"U_avg_ideal": U_avg_b2, "U_dc": U_dc_b2,
          "UF_gesamt": 2*UF, "f_brumm": fBr_b2, "n_dioden": 4}

    if I_last is not None:
        # C für 1 V Brumm als Referenzvergleich
        m1["C_fuer_1V_brumm"] = I_last / (fBr_m1 * 1)
        b2["C_fuer_1V_brumm"] = I_last / (fBr_b2 * 1)
        if C is not None:
            for d, f in ((m1, fBr_m1), (b2, fBr_b2)):
                U_br = I_last / (f * C)
                UDC  = d["U_dc"]
                d["U_brumm"] = U_br
                d["welligkeit_pct"] = U_br / UDC * 100 if UDC > 0 else float("inf")

    return {
        "Ueff": Ueff, "Up": Up, "UF": UF,
        "m1": m1, "b2": b2,
        "C": C, "I_last": I_last,
        "empfehlung": "B2",
        "grund": "Doppelte Brummfrequenz → halb so grosser Siebkondensator",
    }

    """10.3 Betriebstemperatur: T_betr = T_amb + I^2*R*R_th"""
    PV     = I**2 * R20
    dT     = PV * Rth
    T_betr = Tamb + dT
    result = {"R20": R20, "I": I, "Rth": Rth, "Tamb": Tamb,
              "PV": PV, "dT": dT, "T_betr": T_betr}
    if alpha:
        R_betr = R20 * (1 + alpha * (T_betr - 20))
        result.update({"alpha": alpha, "R_betr": R_betr,
                        "PV_iteration1": I**2 * R_betr})
    if Tmax:
        reserve = Tmax - T_betr
        result.update({"Tmax": Tmax, "reserve_K": reserve, "warnung": reserve < 0})
    return result


# ============================================================
# KAPITEL 10: Thermik
# ============================================================

def waermewiderstand(PV=None, Rth=None, dT=None) -> dict:
    """10.1 Waermewiderstand: dT = P_V * R_th"""
    n, miss = check_inputs({"PV": PV, "Rth": Rth, "dT": dT})
    if n != 1:
        raise ValueError("Genau ein Feld leer lassen!")
    m = miss[0]
    if m == "dT":
        dT = PV * Rth
    elif m == "Rth":
        if PV == 0: raise ZeroDivisionError
        Rth = dT / PV
    else:
        if Rth == 0: raise ZeroDivisionError
        PV = dT / Rth
    return {"PV": PV, "Rth": Rth, "dT": dT, "berechnet": m}


def kuehlkoerper_dimensionierung(Tj, Tamb, PV, Rjc, Rcs=0.2) -> dict:
    """10.2 Kuehlkoerper: R_th,sa <= (Tj-Tamb)/PV - Rjc - Rcs"""
    if PV == 0: raise ZeroDivisionError
    Rth_ges_max = (Tj - Tamb) / PV
    Rsa_max     = Rth_ges_max - Rjc - Rcs
    empfehlung  = ("unmöglich" if Rsa_max < 0 else
                   "grosser Kuehlkoerper" if Rsa_max < 1 else
                   "mittlerer Kuehlkoerper" if Rsa_max < 5 else
                   "kleiner Kuehlkoerper" if Rsa_max < 20 else
                   "kein Kühlkörper nötig")
    return {"Tj": Tj, "Tamb": Tamb, "PV": PV, "Rjc": Rjc, "Rcs": Rcs,
            "Rth_ges_max": Rth_ges_max, "Rsa_max": Rsa_max, "empfehlung": empfehlung}

# ============================================================
# KAPITEL E1: Dioden & Gleichrichter (Elektronik)
# ============================================================

def diode_kennlinie(UF=None, IS=1e-12, n=1.0, T_celsius=27.0, ID=None) -> dict:
    """
    E1.1 Diodenkennlinie (Shockley): ID = IS*(exp(UF/(n*VT))-1)
    Ein Feld (UF oder ID) leer lassen → wird berechnet.
    """
    from utils import vt
    VT = vt(T_celsius)
    if UF is None and ID is None:
        raise ValueError("UF oder ID eingeben")
    if UF is not None:
        ID_calc = IS * (math.exp(UF / (n * VT)) - 1)
        return {"UF": UF, "ID": ID_calc, "VT": VT, "IS": IS, "n": n, "T": T_celsius, "berechnet": "ID"}
    else:
        # ID gegeben → UF berechnen
        if ID <= -IS: raise ValueError("ID muss > -IS sein")
        UF_calc = n * VT * math.log(ID / IS + 1)
        return {"UF": UF_calc, "ID": ID, "VT": VT, "IS": IS, "n": n, "T": T_celsius, "berechnet": "UF"}


def zener_vorwiderstand(Uin=None, UZ=None, IZ=None, ILast=0.0, RV=None) -> dict:
    """
    E1.2 Zener-Vorwiderstand: RV = (Uin - UZ) / (IZ + ILast)
    Genau ein Feld leer lassen.
    """
    n, miss = check_inputs({"Uin": Uin, "UZ": UZ, "IZ": IZ, "RV": RV})
    if n != 1:
        raise ValueError("Genau ein Feld leer lassen!")
    m = miss[0]
    if m == "RV":
        denom = IZ + ILast
        if denom == 0: raise ZeroDivisionError("IZ + ILast darf nicht 0 sein")
        RV = (Uin - UZ) / denom
    elif m == "Uin":
        Uin = UZ + RV * (IZ + ILast)
    elif m == "UZ":
        UZ = Uin - RV * (IZ + ILast)
    elif m == "IZ":
        if RV == 0: raise ZeroDivisionError("RV darf nicht 0 sein")
        IZ = (Uin - UZ) / RV - ILast
    PV = (Uin - UZ) * (IZ + ILast) if all(x is not None for x in [Uin, UZ, IZ]) else None
    return {"Uin": Uin, "UZ": UZ, "IZ": IZ, "ILast": ILast, "RV": RV,
            "PV_RV": PV, "berechnet": m}


def lm317(R1=None, R2=None, Uout=None, Iadj=50e-6) -> dict:
    """
    E1.3 LM317 Ausgangsspannung: Uout = 1.25*(1 + R2/R1) + Iadj*R2
    R1 typisch 240 Ohm. Genau ein Feld leer lassen.
    """
    n, miss = check_inputs({"R1": R1, "R2": R2, "Uout": Uout})
    if n != 1:
        raise ValueError("Genau ein Feld leer lassen!")
    m = miss[0]
    if m == "Uout":
        if R1 == 0: raise ZeroDivisionError
        Uout = 1.25 * (1 + R2 / R1) + Iadj * R2
    elif m == "R2":
        # Uout = 1.25 + 1.25*R2/R1 + Iadj*R2 → R2*(1.25/R1 + Iadj) = Uout - 1.25
        denom = 1.25 / R1 + Iadj
        if denom == 0: raise ZeroDivisionError
        R2 = (Uout - 1.25) / denom
    elif m == "R1":
        # Uout - 1.25 - Iadj*R2 = 1.25*R2/R1 → R1 = 1.25*R2/(Uout - 1.25 - Iadj*R2)
        denom = Uout - 1.25 - Iadj * R2
        if denom == 0: raise ZeroDivisionError
        R1 = 1.25 * R2 / denom
    PD_min = 1.25 / R1 if R1 and R1 > 0 else None  # Ruhestrom durch R1
    return {"R1": R1, "R2": R2, "Uout": Uout, "Iadj": Iadj,
            "Uref": 1.25, "I_R1": PD_min, "berechnet": m,
            "warnung_Uin_min": (Uout + 3.0) if Uout else None}


# ============================================================
# KAPITEL E2: Transistoren (BJT & MOSFET)
# ============================================================

def bjt_basis(IC=None, IB=None, IE=None, beta=None, UCE=None) -> dict:
    """
    E2.1 BJT-Grundgleichungen: IC = beta*IB, IE = IC + IB
    Mindestens 2 Werte eingeben.
    """
    solved = True
    if IC is not None and IB is not None:
        if beta is None: beta = IC / IB
        if IE is None: IE = IC + IB
    elif IC is not None and beta is not None:
        if IB is None: IB = IC / beta
        if IE is None: IE = IC + IB
    elif IB is not None and beta is not None:
        if IC is None: IC = beta * IB
        if IE is None: IE = IC + IB
    elif IE is not None and beta is not None:
        # IE = IC + IB = beta*IB + IB = IB*(beta+1)
        IB = IE / (beta + 1)
        IC = beta * IB
    else:
        raise ValueError("Mindestens 2 Grössen eingeben (IC, IB, beta, oder IE)")
    PV = UCE * IC if (UCE is not None and IC is not None) else None
    UBE = 0.7
    arbeitspunkt = None
    if UCE is not None:
        arbeitspunkt = "sättigung" if UCE < 0.3 else ("aktiv" if UCE > 0.3 else "grenzfall")
    return {"IC": IC, "IB": IB, "IE": IE, "beta": beta,
            "UCE": UCE, "UBE": UBE, "PV": PV,
            "arbeitspunkt": arbeitspunkt}


def bjt_basiswiderstand(Uin, UBE=0.7, IC_soll=None, beta=100, k_ueberst=5.0,
                         RB=None) -> dict:
    """
    E2.1 Basisvorwiderstand für BJT-Schalter.
    RB = (Uin - UBE) / (IC_soll/beta * k)
    """
    if RB is None:
        if IC_soll is None: raise ValueError("IC_soll oder RB eingeben")
        IB_min = IC_soll / beta
        IB_soll = IB_min * k_ueberst
        if IB_soll == 0: raise ZeroDivisionError
        RB = (Uin - UBE) / IB_soll
    else:
        IB_soll = (Uin - UBE) / RB if RB > 0 else None
        IB_min = IC_soll / beta if IC_soll and beta else None
        k_ueberst = IB_soll / IB_min if (IB_soll and IB_min and IB_min > 0) else None
    return {"Uin": Uin, "UBE": UBE, "IC_soll": IC_soll, "beta": beta,
            "k_ueberst": k_ueberst, "RB": RB,
            "P_RB": (Uin - UBE)**2 / RB if RB and RB > 0 else None}


def mosfet_ids(UGS=None, Uth=2.5, K=0.1, region="sättigung",
               UDS=None) -> dict:
    """
    E2.2 MOSFET Drainstrom.
    Sättigung:  IDS = K/2*(UGS-Uth)^2
    Ohmscher B.: IDS = K*(UGS-Uth)*UDS - K/2*UDS^2
    """
    if UGS is None: raise ValueError("UGS eingeben")
    Uov = UGS - Uth  # overdrive
    if Uov <= 0:
        return {"UGS": UGS, "Uth": Uth, "K": K, "IDS": 0.0,
                "region": "sperrung", "Uov": Uov}
    if region == "sättigung" or (UDS is not None and UDS >= Uov):
        IDS = K / 2 * Uov**2
        reg = "sättigung"
    elif region == "ohmscher" or (UDS is not None and UDS < Uov):
        if UDS is None: raise ValueError("UDS für ohmschen Bereich eingeben")
        IDS = K * (Uov * UDS - 0.5 * UDS**2)
        reg = "ohmscher Bereich"
    else:
        IDS = K / 2 * Uov**2
        reg = "sättigung"
    RDS_on = UDS / IDS if (UDS and IDS and IDS > 0) else None
    PV = IDS * UDS if UDS is not None else None
    return {"UGS": UGS, "Uth": Uth, "K": K, "UDS": UDS,
            "IDS": IDS, "Uov": Uov, "region": reg,
            "RDS_on": RDS_on, "PV": PV}


def leistungshalbleiter(UCE=None, IC=None, PV=None, RDS_on=None,
                         Tj_max=150, Tamb=25, Rjc=None, Rcs=0.2) -> dict:
    """
    E2.3 Verlustleistung & Thermik Leistungshalbleiter.
    BJT:   PV = UCE * IC
    MOSFET: PV = RDS_on * IC^2
    """
    if PV is None:
        if UCE is not None and IC is not None:
            PV = UCE * IC
            modus = "BJT"
        elif RDS_on is not None and IC is not None:
            PV = RDS_on * IC**2
            modus = "MOSFET"
        else:
            raise ValueError("PV, oder (UCE+IC), oder (RDS_on+IC) eingeben")
    else:
        modus = "direkt"
    result = {"PV": PV, "UCE": UCE, "IC": IC, "RDS_on": RDS_on, "modus": modus}
    if Rjc is not None and PV > 0:
        Rth_ges = (Tj_max - Tamb) / PV
        Rsa_max = Rth_ges - Rjc - Rcs
        Tj = Tamb + PV * (Rjc + Rcs + max(0, Rsa_max))
        result.update({
            "Tj_max": Tj_max, "Tamb": Tamb, "Rjc": Rjc, "Rcs": Rcs,
            "Rth_ges_max": Rth_ges,
            "Rsa_max": Rsa_max,
            "kuehlkoerper": "nötig" if Rsa_max < 50 else "nicht nötig",
            "warnung": Rsa_max < 0,
        })
    return result


# ============================================================
# KAPITEL E3: Operationsverstärker
# ============================================================

def opv_invertierend(Uin=None, Rf=None, Rin=None, Uout=None, v=None) -> dict:
    """
    E3.1a Invertierender Verstärker: v = -Rf/Rin, Uout = v*Uin
    Mindestens 2 der 4 Grössen eingeben (Rf, Rin, Uin, Uout).
    """
    if Rf is not None and Rin is not None:
        if Rin == 0: raise ZeroDivisionError
        v = -Rf / Rin
    if v is not None and Uin is not None and Uout is None:
        Uout = v * Uin
    elif v is not None and Uout is not None and Uin is None:
        if v == 0: raise ZeroDivisionError
        Uin = Uout / v
    elif Uin is not None and Uout is not None and v is None:
        if Uin == 0: raise ZeroDivisionError
        v = Uout / Uin
        Rf = -v * Rin if Rin else None
    if v is None:
        raise ValueError("Mindestens Rf+Rin, oder v+Uin, oder Uin+Uout eingeben")
    Rkomp = None
    if Rf is not None and Rin is not None and Rf > 0 and Rin > 0:
        Rkomp = Rf * Rin / (Rf + Rin)
    return {"v": v, "v_dB": 20*math.log10(abs(v)) if v and v != 0 else None,
            "Rf": Rf, "Rin": Rin, "Uin": Uin, "Uout": Uout, "Rkomp": Rkomp}


def opv_nicht_invertierend(Uin=None, Rf=None, R2=None, Uout=None, v=None) -> dict:
    """
    E3.1b Nicht-invertierender Verstärker: v = 1 + Rf/R2
    """
    if Rf is not None and R2 is not None:
        if R2 == 0: raise ZeroDivisionError
        v = 1 + Rf / R2
    if v is not None and Uin is not None and Uout is None:
        Uout = v * Uin
    elif v is not None and Uout is not None and Uin is None:
        if v == 0: raise ZeroDivisionError
        Uin = Uout / v
    elif Uin is not None and Uout is not None and v is None:
        if Uin == 0: raise ZeroDivisionError
        v = Uout / Uin
        if R2 is not None: Rf = (v - 1) * R2
    if v is None:
        raise ValueError("Rf+R2, oder v+Uin/Uout, oder Uin+Uout eingeben")
    return {"v": v, "v_dB": 20*math.log10(abs(v)) if v and v > 0 else None,
            "Rf": Rf, "R2": R2, "Uin": Uin, "Uout": Uout,
            "impedanzwandler": (Rf == 0 or v == 1)}


def opv_gbp(GBP, v_gewuenscht) -> dict:
    """
    E3.2 Gain-Bandwidth-Product: GBP = v * f_-3dB = const
    """
    if v_gewuenscht == 0: raise ZeroDivisionError
    f3dB = GBP / abs(v_gewuenscht)
    return {"GBP": GBP, "v": v_gewuenscht,
            "f_3dB": f3dB,
            "hinweis": f"Bei v={v_gewuenscht} beträgt die Bandbreite {f3dB:.4g} Hz"}


def opv_slew_rate(SR, Uout_max, f=None, f_max=None) -> dict:
    """
    E3.2 Slew Rate Analyse.
    SR [V/µs]: maximale Aussteuerungsfrequenz f_max = SR/(2*pi*Uout_max)
    """
    SR_si = SR * 1e6  # V/µs → V/s
    if Uout_max <= 0: raise ValueError("Uout_max muss > 0 sein")
    f_max_calc = SR_si / (2 * math.pi * Uout_max)
    result = {"SR_Vus": SR, "SR_Vs": SR_si, "Uout_max": Uout_max, "f_max": f_max_calc}
    if f is not None:
        Umax_bei_f = SR_si / (2 * math.pi * f)
        result["f"] = f
        result["Uout_max_bei_f"] = Umax_bei_f
        result["ok"] = Uout_max <= Umax_bei_f
    return result


def schmitt_trigger_inv(Rf=None, R1=None, Usat_pos=13.5, Usat_neg=-13.5,
                         Uotp=None, Uutp=None) -> dict:
    """
    E3.3 Invertierender Schmitt-Trigger.
    Uotp =  Usat_pos * R1/(R1+Rf)  (obere Schaltschwelle)
    Uutp =  Usat_neg * R1/(R1+Rf)  (untere Schaltschwelle)
    """
    if Rf is not None and R1 is not None:
        denom = R1 + Rf
        if denom == 0: raise ZeroDivisionError
        Uotp = Usat_pos * R1 / denom
        Uutp = Usat_neg * R1 / denom
    elif Uotp is not None and Usat_pos != 0:
        # R1/(R1+Rf) = Uotp/Usat_pos → k = Uotp/Usat_pos
        k = Uotp / Usat_pos
        if R1 is not None and k < 1:
            Rf = R1 * (1 - k) / k
        elif Rf is not None and k < 1:
            R1 = Rf * k / (1 - k)
    if Uotp is None or Uutp is None:
        raise ValueError("Rf+R1 oder Uotp (mit R1 oder Rf) eingeben")
    hysterese = Uotp - Uutp
    return {"Rf": Rf, "R1": R1,
            "Uotp": Uotp, "Uutp": Uutp,
            "hysterese": hysterese,
            "Usat_pos": Usat_pos, "Usat_neg": Usat_neg}


def opv_integrator(R=None, C=None, Uin=None, t=None, Uout=None) -> dict:
    """
    E3.3 OPV-Integrator: Uout = -1/(R*C) * Uin * t (für DC-Eingang)
    f_int = 1/(2*pi*R*C) = Integrationsfrequenz
    """
    n, miss = check_inputs({"R": R, "C": C})
    if n > 0:
        raise ValueError("R und C müssen eingegeben werden")
    if R == 0 or C == 0: raise ZeroDivisionError
    tau = R * C
    f_int = 1 / (2 * math.pi * tau)
    result = {"R": R, "C": C, "tau": tau, "f_int": f_int}
    if Uin is not None and t is not None:
        Uout_calc = -(1 / tau) * Uin * t
        result.update({"Uin": Uin, "t": t, "Uout": Uout_calc})
    return result


# ============================================================
# KAPITEL E4: Aktive Filter & Oszillatoren
# ============================================================

def wien_oszillator(R=None, C=None, f0=None) -> dict:
    """
    E4.2 Wien-Brücken-Oszillator: f0 = 1/(2*pi*R*C), v=3, k=1/3
    """
    n, miss = check_inputs({"R": R, "C": C, "f0": f0})
    if n != 1:
        raise ValueError("Genau ein Feld leer lassen!")
    m = miss[0]
    if m == "f0":
        if R == 0 or C == 0: raise ZeroDivisionError
        f0 = 1 / (2 * math.pi * R * C)
    elif m == "R":
        if f0 == 0 or C == 0: raise ZeroDivisionError
        R = 1 / (2 * math.pi * f0 * C)
    else:
        if f0 == 0 or R == 0: raise ZeroDivisionError
        C = 1 / (2 * math.pi * f0 * R)
    return {"R": R, "C": C, "f0": f0,
            "v_min": 3.0, "k": 1/3,
            "Rf_R1": 2.0,  # Rf = 2*R1 für v=3
            "berechnet": m}


def rc_phasenschieber_osz(R=None, C=None, f0=None) -> dict:
    """
    E4.2 RC-Phasenschieber-Oszillator: f0 = 1/(2*pi*R*C*sqrt(6)), v=29
    """
    n, miss = check_inputs({"R": R, "C": C, "f0": f0})
    if n != 1:
        raise ValueError("Genau ein Feld leer lassen!")
    m = miss[0]
    factor = 2 * math.pi * math.sqrt(6)
    if m == "f0":
        if R == 0 or C == 0: raise ZeroDivisionError
        f0 = 1 / (factor * R * C)
    elif m == "R":
        if f0 == 0 or C == 0: raise ZeroDivisionError
        R = 1 / (factor * f0 * C)
    else:
        if f0 == 0 or R == 0: raise ZeroDivisionError
        C = 1 / (factor * f0 * R)
    return {"R": R, "C": C, "f0": f0,
            "v_min": 29.0, "phase_je_glied": 60.0,
            "berechnet": m}


def timer_555_astabil(RA=None, RB=None, C=None, f=None, D=None) -> dict:
    """
    E4.3 555 Timer astabil.
    f = 1.44 / ((RA + 2*RB) * C)
    D = (RA+RB) / (RA+2*RB)
    """
    n, miss = check_inputs({"RA": RA, "RB": RB, "C": C})
    if n == 0:
        # Alle gegeben → berechne f und D
        denom = (RA + 2 * RB) * C
        if denom == 0: raise ZeroDivisionError
        f = 1.44 / denom
        D = (RA + RB) / (RA + 2 * RB)
        t_high = 0.693 * (RA + RB) * C
        t_low  = 0.693 * RB * C
        return {"RA": RA, "RB": RB, "C": C, "f": f, "D": D,
                "t_high": t_high, "t_low": t_low,
                "T": 1/f, "berechnet": "f,D"}
    elif n == 1 and miss[0] == "C":
        if f is None and D is None:
            raise ValueError("f oder D eingeben wenn C unbekannt")
        if f is not None:
            C = 1.44 / ((RA + 2 * RB) * f)
        D_calc = (RA + RB) / (RA + 2 * RB) if (RA and RB) else None
        return {"RA": RA, "RB": RB, "C": C, "f": f, "D": D_calc, "berechnet": "C"}
    else:
        raise ValueError("RA, RB, und C eingeben – f und D werden berechnet")


def timer_555_monostabil(R=None, C=None, tp=None) -> dict:
    """
    E4.3 555 Timer monostabil: tp = 1.1 * R * C
    """
    n, miss = check_inputs({"R": R, "C": C, "tp": tp})
    if n != 1:
        raise ValueError("Genau ein Feld leer lassen!")
    m = miss[0]
    if m == "tp":
        tp = 1.1 * R * C
    elif m == "R":
        if C == 0: raise ZeroDivisionError
        R = tp / (1.1 * C)
    else:
        if R == 0: raise ZeroDivisionError
        C = tp / (1.1 * R)
    return {"R": R, "C": C, "tp": tp, "berechnet": m}


# ============================================================
# KAPITEL E5: Regelungstechnik
# ============================================================

def pt1_sprungantwort(KS=None, T=None, t=None, w=1.0) -> dict:
    """
    E5.2 PT1-Glied Sprungantwort: x(t) = KS * w * (1 - exp(-t/T))
    """
    n, miss = check_inputs({"KS": KS, "T": T, "t": t})
    if n > 0:
        raise ValueError("KS, T und t müssen eingegeben werden")
    if T == 0: raise ZeroDivisionError("T darf nicht 0 sein")
    x_end = KS * w
    x_t   = x_end * (1 - math.exp(-t / T))
    pct   = x_t / x_end * 100 if x_end != 0 else 0
    return {"KS": KS, "T": T, "t": t, "w": w,
            "x_end": x_end, "x_t": x_t, "pct_von_endwert": pct,
            "t_63pct": T, "t_99pct": 5 * T}


def pid_ausgabe(e, e_prev, e_sum, dt, KP=1.0, TI=None, TD=None) -> dict:
    """
    E5.1 PID-Regler Ausgabe (diskret, ein Zeitschritt).
    e     – aktuelle Regelabweichung
    e_prev– vorherige Regelabweichung
    e_sum – aufgelaufene Summe (Integral)
    dt    – Zeitschritt [s]
    """
    P_anteil = KP * e
    e_sum_neu = e_sum + e * dt
    I_anteil  = KP / TI * e_sum_neu if TI and TI > 0 else 0.0
    D_anteil  = KP * TD * (e - e_prev) / dt if (TD and dt > 0) else 0.0
    y = P_anteil + I_anteil + D_anteil
    return {"y": y, "P": P_anteil, "I": I_anteil, "D": D_anteil,
            "e": e, "e_sum": e_sum_neu, "KP": KP, "TI": TI, "TD": TD}


# ============================================================
# KAPITEL E6: FFT & Signalverarbeitung
# ============================================================

def adc_kennwerte(N_bit, Uref=3.3, Uin=None) -> dict:
    """
    E6.3 ADC Kennwerte: LSB = Uref/2^N, SNR = 6.02*N + 1.76 dB
    """
    if N_bit <= 0: raise ValueError("N_bit muss > 0 sein")
    LSB    = Uref / (2**N_bit)
    SNR_dB = 6.02 * N_bit + 1.76
    codes  = 2**N_bit
    result = {"N_bit": N_bit, "Uref": Uref, "LSB": LSB,
              "SNR_dB": SNR_dB, "codes": codes,
              "LSB_mV": LSB * 1000}
    if Uin is not None:
        if Uin < 0 or Uin > Uref:
            result["warnung"] = f"Uin={Uin} V ausserhalb 0…{Uref} V"
        code = min(int(Uin / LSB), codes - 1)
        result.update({"Uin": Uin, "code_decimal": code,
                       "code_hex": hex(code), "quantisierungs_fehler": Uin - code * LSB})
    return result


def fft_parameter(fs, N) -> dict:
    """
    E6.1 FFT-Kenngrößen: Δf, f_Nyquist, T_ges
    """
    if N <= 0 or fs <= 0: raise ValueError("fs und N müssen > 0 sein")
    df      = fs / N
    f_ny    = fs / 2
    T_ges   = N / fs
    return {"fs": fs, "N": N,
            "delta_f": df,
            "f_nyquist": f_ny,
            "T_gesamt": T_ges,
            "warnung_n_pot2": N & (N - 1) != 0}