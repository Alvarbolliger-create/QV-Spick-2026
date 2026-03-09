# ============================================================
# TestNoteBook.py – pytest Tests für Elektrotechnik-Rechner
# ============================================================
# Ordnerstruktur:
#   ./
#   ├── TestNoteBook.py
#   ├── venv/
#   ├── utils.py
#   ├── calc.py     ← Single Source of Truth für Logik
#   └── notebook/
#       ├── SoftHardware.ipynb
#       ├── Elektronik.ipynb
#       └── Elektrotechnik.ipynb
#
# Ausführen:
#   pytest TestNoteBook.py -v
#   pytest TestNoteBook.py -v -k "ohm"
#   pytest TestNoteBook.py -v --tb=short
# ============================================================

import sys, math
import pytest

sys.path.insert(0, "./notebook")
from utils import p, fmt, check_inputs, EPS0, MU0
from calc  import (
    ohm, leistung, reihenschaltung, parallelschaltung,
    temperaturkoeffizient, leitungswiderstand, spannungsteiler,
    leitwert, stromdichte, thevenin_aus_ull_ik, thevenin_aus_spannungsteiler,
    kondensator_qcu, plattenkondensator, kondensator_schaltung,
    rc_zeitkonstante, rc_zeitverlauf, kapazitiver_widerstand,
    rc_impedanz, elektrisches_feld,
    selbstinduktion, induktivitaet_spule, spulen_schaltung,
    rl_zeitkonstante, rl_zeitverlauf, induktiver_widerstand,
    rl_impedanz, magnetisches_feld,
    ac_leistung, blindstromkompensation,
    resonanzfrequenz, reihenschwingkreis, parallelschwingkreis, guete_bandbreite,
    dezibel, kettendaempfung,
    rc_tiefpass, rc_hochpass, rl_filter, aktiver_tiefpass,
    aktiver_hochpass, sallen_key, notch_filter,
    uebersetzungsverhaeltnis, trafo_wirkungsgrad,
    widerstandstransformation, trafo_lastspannung,
    spitzenwert_effektivwert, einweggleichrichter,
    brueckengleichrichter, siebkondensator, netzteil_dimensionierung,
    waermewiderstand, kuehlkoerper_dimensionierung, thermische_stabilitaet,
)

A = pytest.approx


# ============================================================
# utils.py – p(), fmt(), check_inputs(), Konstanten
# ============================================================

class TestUtils:
    def test_p_none(self):          assert p(None) is None
    def test_p_leer(self):          assert p("") is None
    def test_p_leerzeichen(self):   assert p("  ") is None
    def test_p_int(self):           assert p("100") == A(100.0)
    def test_p_float(self):         assert p("4.7") == A(4.7)
    def test_p_kilo(self):          assert p("10k") == A(10_000.0)
    def test_p_mega(self):          assert p("2M") == A(2_000_000.0)
    def test_p_giga(self):          assert p("1G") == A(1e9)
    def test_p_milli(self):         assert p("100m") == A(0.1)
    def test_p_mikro_u(self):       assert p("4.7u") == A(4.7e-6)
    def test_p_mikro_mu(self):      assert p("4.7µ") == A(4.7e-6)
    def test_p_nano(self):          assert p("100n") == A(1e-7)
    def test_p_piko(self):          assert p("22p") == A(22e-12)
    def test_p_negativ(self):       assert p("-5") == A(-5.0)
    def test_p_text_wirft(self):
        with pytest.raises(ValueError): p("abc")
    def test_p_einheit_wirft(self):
        with pytest.raises(ValueError): p("10V")

    def test_check_alle_voll(self):
        n, miss = check_inputs({"R": 100, "U": 5, "I": 0.05})
        assert n == 0 and miss == []
    def test_check_eines_leer(self):
        n, miss = check_inputs({"R": 100, "U": None, "I": 0.05})
        assert n == 1 and miss == ["U"]
    def test_check_alle_leer(self):
        n, _ = check_inputs({"R": None, "U": None, "I": None})
        assert n == 3

    def test_fmt_null(self):    assert fmt(0, "V")       == "0 V"
    def test_fmt_kilo(self):    assert fmt(10_000, "Hz") == "10 kHz"
    def test_fmt_mikro(self):   assert fmt(4.7e-6, "F")  == "4.7 µF"
    def test_fmt_nano(self):    assert fmt(100e-9, "F")  == "100 nF"
    def test_fmt_milli(self):   assert fmt(0.001, "A")   == "1 mA"

    def test_eps0(self): assert EPS0 == A(8.854187817e-12, rel=1e-9)
    def test_mu0(self):  assert MU0  == A(4 * math.pi * 1e-7, rel=1e-9)


# ============================================================
# Allgemeine Edge-Cases
# ============================================================

class TestEdgeCases:
    def test_alle_felder_voll_wirft(self):
        with pytest.raises(ValueError): ohm(U=5, R=100, I=0.05)
    def test_alle_felder_leer_wirft(self):
        with pytest.raises(ValueError): ohm()
    def test_division_durch_null_wirft(self):
        with pytest.raises((ZeroDivisionError, ValueError)): ohm(U=5, R=0)
    def test_ergebnis_ist_dict(self):
        assert isinstance(ohm(R=100, I=0.05), dict)
    def test_berechnet_feld_vorhanden(self):
        assert "berechnet" in ohm(R=100, I=0.05)
    def test_grosse_werte_kein_overflow(self):
        assert math.isfinite(ohm(R=p("1G"), I=p("1m"))["U"])
    def test_kleine_werte_kein_underflow(self):
        assert rc_zeitkonstante(R=1, C=p("1p"))["tau"] > 0
    def test_si_praefixe_konsistent(self):
        assert ohm(U=p("12"), R=p("10k"))["I"] == A(1.2e-3)


# ============================================================
# Kapitel 1 – Widerstand
# ============================================================

class TestOhm:
    """1.1 U = R · I"""
    def test_u(self):   assert ohm(R=100, I=0.05)["U"]  == A(5.0)
    def test_r(self):   assert ohm(U=12,  I=0.1)["R"]   == A(120.0)
    def test_i(self):   assert ohm(U=230, R=1000)["I"]  == A(0.23)
    def test_berechnet_u(self): assert ohm(R=100, I=0.05)["berechnet"] == "U"
    def test_berechnet_r(self): assert ohm(U=12,  I=0.1)["berechnet"]  == "R"
    def test_berechnet_i(self): assert ohm(U=230, R=1000)["berechnet"] == "I"
    def test_r_null_wirft(self):
        with pytest.raises((ZeroDivisionError, ValueError)): ohm(U=5, R=0)


class TestLeistung:
    """1.2 P = U·I = I²·R = U²/R"""
    def test_p_ui(self):  assert leistung(U=230, I=10)["P"]     == A(2300.0)
    def test_u_pi(self):  assert leistung(P=1000, I=4.348)["U"] == A(230.0, rel=1e-3)
    def test_i_pu(self):  assert leistung(P=2300, U=230)["I"]   == A(10.0)
    def test_p_ir(self):  assert leistung(I=2, R=100)["P"]      == A(400.0)
    def test_p_ur(self):  assert leistung(U=10, R=50)["P"]      == A(2.0)
    def test_r_pu(self):  assert leistung(P=2, U=10)["I"]       == A(0.2)
    def test_i_pr(self):  assert leistung(P=400, R=100)["I"]    == A(2.0)
    def test_u_pr(self):  assert leistung(P=2, R=50)["U"]       == A(10.0)
    def test_ungueltig_wirft(self):
        with pytest.raises(ValueError): leistung(P=100)


class TestReihenschaltung:
    """1.3 R_ges = R1 + R2 + ..."""
    def test_zwei(self):         assert reihenschaltung([100, 200])["R_ges"]            == A(300.0)
    def test_fuenf(self):        assert reihenschaltung([100,200,300,400,500])["R_ges"] == A(1500.0)
    def test_none_ignoriert(self): assert reihenschaltung([100, None, 200])["R_ges"]    == A(300.0)
    def test_mit_spannung(self):
        r = reihenschaltung([100, 400], U_ges=100)
        assert r["R_ges"] == A(500.0) and r["I"] == A(0.2)
    def test_leer_wirft(self):
        with pytest.raises(ValueError): reihenschaltung([])


class TestParallelschaltung:
    """1.4 1/R_ges = Σ(1/Rn)"""
    def test_zwei_gleich(self):     assert parallelschaltung([100, 100])["R_ges"] == A(50.0)
    def test_kleiner_als_kleinstes(self):
        assert parallelschaltung([100, 200, 300])["R_ges"] < 100
    def test_mit_spannung(self):
        r = parallelschaltung([200, 300], U_ges=120)
        assert r["I_ges"] == A(1.0)
        assert r["I_teile"][0] == A(0.6)
        assert r["I_teile"][1] == A(0.4)
    def test_null_wirft(self):
        with pytest.raises(ZeroDivisionError): parallelschaltung([100, 0])


class TestTemperaturkoeffizient:
    """1.5 R_T = R20 · [1 + α·(T−20)]"""
    def test_rt(self):
        assert temperaturkoeffizient(R20=100, alpha=0.00393, T=100)["RT"] == A(100*(1+0.00393*80))
    def test_r20(self):
        RT = 100*(1+0.00393*80)
        assert temperaturkoeffizient(alpha=0.00393, T=100, RT=RT)["R20"] == A(100.0, rel=1e-4)
    def test_t(self):
        RT = 100*(1+0.00393*80)
        assert temperaturkoeffizient(R20=100, alpha=0.00393, RT=RT)["T"] == A(100.0, rel=1e-3)
    def test_alpha(self):
        RT = 100*(1+0.00393*80)
        assert temperaturkoeffizient(R20=100, T=100, RT=RT)["alpha"] == A(0.00393, rel=1e-3)
    def test_t_gleich_20_kein_effekt(self):
        assert temperaturkoeffizient(R20=100, alpha=0.00393, T=20)["RT"] == A(100.0)
    def test_t_gleich_20_alpha_wirft(self):
        with pytest.raises(ZeroDivisionError):
            temperaturkoeffizient(R20=100, T=20, RT=100)


class TestLeitungswiderstand:
    """1.6 R = ρ·l/A"""
    def test_r(self):
        assert leitungswiderstand(rho=0.0178, l=10, A=1.5)["R"] == A(0.0178*10/1.5)
    def test_l(self):   assert leitungswiderstand(R=1, rho=0.0178, A=1.5)["l"]  == A(1.5/0.0178)
    def test_a(self):   assert leitungswiderstand(R=0.5, rho=0.0178, l=10)["A"] == A(0.0178*10/0.5)
    def test_rho(self): assert leitungswiderstand(R=1, l=10, A=1.5)["rho"]      == A(1*1.5/10)


class TestSpannungsteiler:
    """1.8 U2 = U_ges · R2/(R1+R2)"""
    def test_u2(self):   assert spannungsteiler(U_ges=12, R1=300, R2=100)["U2"]  == A(3.0)
    def test_uges(self): assert spannungsteiler(R1=300, R2=100, U2=3)["U_ges"]   == A(12.0)
    def test_r1(self):   assert spannungsteiler(U_ges=12, R2=100, U2=3)["R1"]    == A(300.0)
    def test_r2(self):   assert spannungsteiler(U_ges=12, R1=300, U2=3)["R2"]    == A(100.0)
    def test_gleiche_r_halbiert(self):
        assert spannungsteiler(U_ges=10, R1=1000, R2=1000)["U2"] == A(5.0)
    def test_r1_null_volle_spannung(self):
        assert spannungsteiler(U_ges=5, R1=0, R2=100)["U2"] == A(5.0)


class TestLeitwert:
    """1.9 G = 1/R"""
    def test_g(self):  assert leitwert(R=100)["G"]   == A(0.01)
    def test_r(self):  assert leitwert(G=0.002)["R"] == A(500.0)
    def test_r_null_wirft(self):
        with pytest.raises(ZeroDivisionError): leitwert(R=0)


class TestStromdichte:
    """1.10 J = I/A"""
    def test_j(self): assert stromdichte(I=10, A=2.5)["J"] == A(4.0)
    def test_a(self): assert stromdichte(I=6,  J=4)["A"]   == A(1.5)
    def test_i(self): assert stromdichte(A=1.5, J=4)["I"]  == A(6.0)


class TestTheveninNorton:
    """1.11 Thevenin/Norton-Äquivalent"""
    def test_uth(self):  assert thevenin_aus_ull_ik(Ull=12, Ik=0.1)["Uth"] == A(12.0)
    def test_rth(self):  assert thevenin_aus_ull_ik(Ull=12, Ik=0.1)["Rth"] == A(120.0)
    def test_in(self):   assert thevenin_aus_ull_ik(Ull=12, Ik=0.1)["IN"]  == A(0.1)
    def test_p_max(self):
        r = thevenin_aus_ull_ik(Ull=20, Ik=1)
        assert r["P_max"] == A(20**2 / (4*20))
    def test_r_last_spannung(self):
        r = thevenin_aus_ull_ik(Ull=12, Ik=0.1, R_last=120)
        assert r["U_last"] == A(6.0) and r["I_last"] == A(0.05)
    def test_spannungsteiler_methode(self):
        r = thevenin_aus_spannungsteiler(U_ges=12, R1=300, R2=100)
        assert r["Uth"] == A(3.0) and r["Rth"] == A(75.0)
    def test_rth_gleich_uth_durch_in(self):
        r = thevenin_aus_ull_ik(Ull=9, Ik=0.3)
        assert r["Rth"] == A(r["Uth"] / r["IN"])
    def test_ik_null_wirft(self):
        with pytest.raises(ZeroDivisionError): thevenin_aus_ull_ik(Ull=12, Ik=0)


# ============================================================
# Kapitel 2 – Kondensatoren
# ============================================================

class TestKondensatorQCU:
    """2.1 Q = C·U"""
    def test_q(self): assert kondensator_qcu(C=100e-6, U=12)["Q"]  == A(1.2e-3)
    def test_c(self): assert kondensator_qcu(Q=1.2e-3, U=12)["C"]  == A(100e-6)
    def test_u(self): assert kondensator_qcu(Q=1e-3, C=100e-6)["U"] == A(10.0)
    def test_energie(self):
        assert kondensator_qcu(C=100e-6, U=12)["W"] == A(0.5*100e-6*144)


class TestPlattenkondensator:
    """2.2 C = ε0·εr·A/d"""
    def test_c(self):
        assert plattenkondensator(A=0.01, d=0.001, er=1)["C"] == A(EPS0*0.01/0.001)
    def test_er(self):
        C0 = EPS0*0.01/0.001
        assert plattenkondensator(C=C0*4.5, A=0.01, d=0.001)["er"] == A(4.5, rel=1e-4)
    def test_d(self):
        C = EPS0*0.01/0.001
        assert plattenkondensator(C=C, A=0.01, er=1)["d"] == A(0.001)
    def test_a(self):
        C = EPS0*0.01/0.001
        assert plattenkondensator(C=C, d=0.001, er=1)["A"] == A(0.01)


class TestKondensatorSchaltung:
    """2.3 Reihe/Parallel"""
    def test_parallel_summe(self):
        assert kondensator_schaltung([100e-9,220e-9,470e-9], parallel=True)["C_ges"] == A(790e-9)
    def test_parallel_groesser_als_groesstes(self):
        assert kondensator_schaltung([100e-9, 200e-9], parallel=True)["C_ges"] > 200e-9
    def test_reihe_halbierung(self):
        assert kondensator_schaltung([100e-9, 100e-9], parallel=False)["C_ges"] == A(50e-9)
    def test_reihe_kleiner_als_kleinstes(self):
        assert kondensator_schaltung([100e-9,220e-9,470e-9], parallel=False)["C_ges"] < 100e-9


class TestRCZeitkonstante:
    """2.4a τ = R·C"""
    def test_tau(self): assert rc_zeitkonstante(R=10_000, C=100e-9)["tau"] == A(1e-3)
    def test_r(self):   assert rc_zeitkonstante(C=100e-9, tau=1e-3)["R"]   == A(10_000.0)
    def test_c(self):   assert rc_zeitkonstante(R=10_000, tau=1e-3)["C"]   == A(100e-9)
    def test_1tau_63pct(self):
        assert rc_zeitkonstante(R=1000, C=1e-6)["ladetabelle"][1] == A(63.2, rel=1e-3)
    def test_5tau_ueber_99pct(self):
        assert rc_zeitkonstante(R=1000, C=1e-6)["ladetabelle"][5] > 99.0


class TestRCZeitverlauf:
    """2.4b U_C(t)"""
    def test_laden_1tau(self):
        r = rc_zeitverlauf(R=10_000, C=100e-9, U0=10, t=1e-3, laden=True)
        assert r["Uc"] == A(10*(1-math.exp(-1)))
    def test_entladen_1tau(self):
        r = rc_zeitverlauf(R=10_000, C=100e-9, U0=10, t=1e-3, laden=False)
        assert r["Uc"] == A(10*math.exp(-1))
    def test_laden_t0_ist_null(self):
        assert rc_zeitverlauf(R=1000, C=1e-6, U0=5, t=0, laden=True)["Uc"] == A(0.0, abs=1e-15)
    def test_entladen_t0_gleich_u0(self):
        assert rc_zeitverlauf(R=1000, C=1e-6, U0=5, t=0, laden=False)["Uc"] == A(5.0)


class TestKapazitiverWiderstand:
    """2.5 X_C = 1/(2π·f·C)"""
    def test_xc(self):
        assert kapazitiver_widerstand(f=50, C=100e-6)["Xc"] == A(1/(2*math.pi*50*100e-6))
    def test_f(self):
        Xc = 1/(2*math.pi*1000*100e-9)
        assert kapazitiver_widerstand(Xc=Xc, C=100e-9)["f"] == A(1000.0)
    def test_c(self):
        Xc = 1/(2*math.pi*50*100e-6)
        assert kapazitiver_widerstand(Xc=Xc, f=50)["C"] == A(100e-6)
    def test_xc_sinkt_mit_f(self):
        assert (kapazitiver_widerstand(f=50,  C=1e-6)["Xc"] >
                kapazitiver_widerstand(f=500, C=1e-6)["Xc"])


class TestRCImpedanz:
    """2.6 Z = √(R²+Xc²)"""
    def test_z_groesser_r(self):
        assert rc_impedanz(R=100, f=50, C=100e-6)["Z"] > 100
    def test_phi_negativ(self):
        assert rc_impedanz(R=100, f=1000, C=1e-6)["phi_grad"] < 0
    def test_pythagorisch(self):
        r = rc_impedanz(R=100, f=1000, C=1.59e-6, U=10)
        assert math.sqrt(r["U_R"]**2 + r["U_C"]**2) == A(10.0, rel=1e-3)


class TestElektrischesFeld:
    """2.7 E = U/d"""
    def test_e(self): assert elektrisches_feld(U=1000, d=0.001)["E"] == A(1e6)
    def test_u(self): assert elektrisches_feld(E=1e6,  d=0.001)["U"] == A(1000.0)
    def test_d(self): assert elektrisches_feld(E=1e6,  U=1000)["d"]  == A(0.001)
    def test_durchschlag_warnung(self):
        assert elektrisches_feld(U=5000, d=0.001)["durchschlag_warnung"] is True
    def test_keine_warnung_normal(self):
        assert elektrisches_feld(U=100, d=0.001)["durchschlag_warnung"] is False


# ============================================================
# Kapitel 3 – Spulen
# ============================================================

class TestSelbstinduktion:
    """3.1 U_L = L·ΔI/Δt"""
    def test_ul(self): assert selbstinduktion(L=10e-3, dI=5, dt=1e-3)["UL"]  == A(50.0)
    def test_l(self):  assert selbstinduktion(UL=50, dI=5, dt=1e-3)["L"]     == A(10e-3)
    def test_di(self): assert selbstinduktion(UL=50, L=10e-3, dt=1e-3)["dI"] == A(5.0)
    def test_dt(self): assert selbstinduktion(UL=50, L=10e-3, dI=5)["dt"]    == A(1e-3)
    def test_energie(self):
        assert selbstinduktion(L=10e-3, dI=5, dt=1e-3)["W"] == A(0.5*10e-3*25)


class TestInduktivitaetSpule:
    """3.2 L = µ0·µr·N²·A/l"""
    def test_l(self):
        assert induktivitaet_spule(mur=1, N=100, A=1e-4, l=0.1)["L"] == A(MU0*100**2*1e-4/0.1)
    def test_n(self):
        L = MU0*100**2*1e-4/0.1
        assert induktivitaet_spule(L=L, mur=1, A=1e-4, l=0.1)["N"] == A(100.0)
    def test_mur(self):
        L = MU0*500*100**2*1e-4/0.1
        assert induktivitaet_spule(L=L, N=100, A=1e-4, l=0.1)["mur"] == A(500.0, rel=1e-4)


class TestSpulenSchaltung:
    """3.3 Reihe/Parallel"""
    def test_reihe(self):
        assert spulen_schaltung([100e-6,200e-6,300e-6], reihe=True)["L_ges"] == A(600e-6)
    def test_parallel(self):
        assert spulen_schaltung([100e-6, 100e-6], reihe=False)["L_ges"] == A(50e-6)
    def test_reihe_groesser(self):
        assert spulen_schaltung([100e-6, 200e-6], reihe=True)["L_ges"] > 200e-6


class TestRLZeitkonstante:
    """3.4a τ = L/R"""
    def test_tau(self): assert rl_zeitkonstante(L=10e-3, R=100)["tau"]    == A(100e-6)
    def test_l(self):   assert rl_zeitkonstante(R=100, tau=100e-6)["L"]   == A(10e-3)
    def test_r(self):   assert rl_zeitkonstante(L=10e-3, tau=100e-6)["R"] == A(100.0)
    def test_1tau_63pct(self):
        assert rl_zeitkonstante(L=10e-3, R=100)["stromtabelle"][1] == A(63.2, rel=1e-3)


class TestRLZeitverlauf:
    """3.4b I(t)"""
    def test_i_bei_1tau(self):
        r = rl_zeitverlauf(L=10e-3, R=100, U0=10, t=100e-6, einschalten=True)
        assert r["I"] == A(0.1*(1-math.exp(-1)))
    def test_ul_bei_t0(self):
        assert rl_zeitverlauf(L=10e-3, R=100, U0=10, t=0, einschalten=True)["UL"] == A(10.0)
    def test_i_bei_t0_null(self):
        assert rl_zeitverlauf(L=10e-3, R=100, U0=10, t=0, einschalten=True)["I"] == A(0.0, abs=1e-15)


class TestInduktiverWiderstand:
    """3.5 X_L = 2π·f·L"""
    def test_xl(self):
        assert induktiver_widerstand(f=50, L=0.1)["XL"] == A(2*math.pi*50*0.1)
    def test_f(self):
        XL = 2*math.pi*1000*10e-3
        assert induktiver_widerstand(XL=XL, L=10e-3)["f"] == A(1000.0)
    def test_l(self):
        XL = 2*math.pi*50*0.1
        assert induktiver_widerstand(XL=XL, f=50)["L"] == A(0.1)
    def test_xl_steigt_mit_f(self):
        assert (induktiver_widerstand(f=500, L=0.1)["XL"] >
                induktiver_widerstand(f=50,  L=0.1)["XL"])


class TestRLImpedanz:
    """3.6 Z = √(R²+XL²)"""
    def test_z(self):
        r = rl_impedanz(R=100, f=1000, L=15.9e-3)
        assert r["Z"] == A(math.sqrt(100**2 + r["XL"]**2))
    def test_phi_positiv(self):
        assert rl_impedanz(R=100, f=1000, L=10e-3)["phi_grad"] > 0
    def test_pythagorisch(self):
        r = rl_impedanz(R=100, f=1000, L=15.9e-3, U=10)
        assert math.sqrt(r["U_R"]**2 + r["U_L"]**2) == A(10.0, rel=1e-3)


class TestMagnetischesFeld:
    """3.7 H = N·I/l, B = µ0·µr·H"""
    def test_theta(self): assert magnetisches_feld(N=100, I=2, l=0.1)["Theta"] == A(200.0)
    def test_h(self):     assert magnetisches_feld(N=100, I=2, l=0.1)["H"]     == A(2000.0)
    def test_b(self):
        assert magnetisches_feld(N=100, I=2, l=0.1, mur=1000)["B"] == A(MU0*1000*2000)
    def test_phi(self):
        r = magnetisches_feld(N=100, I=2, l=0.1, mur=1000, A=1e-4)
        assert r["Phi"] == A(r["B"]*1e-4)
    def test_saettigungs_warnung(self):
        assert magnetisches_feld(N=1000, I=10, l=0.01, mur=5000)["saettigung_warnung"] is True


# ============================================================
# Kapitel 4 – Wechselstrom Leistung
# ============================================================

class TestACLeistung:
    """4.1 S, P, Q, cos φ"""
    def test_s_aus_ui(self):
        assert ac_leistung(U=230, I=10)["S"] == A(2300.0)
    def test_p_aus_s_cosphi(self):
        assert ac_leistung(S=1000, cos_phi=0.8)["P"] == A(800.0)
    def test_q_aus_s_cosphi(self):
        assert ac_leistung(S=1000, cos_phi=0.8)["Q"] == A(600.0)
    def test_leistungsdreieck(self):
        assert ac_leistung(P=800, Q=600)["S"] == A(1000.0)
    def test_rein_ohmsch(self):
        r = ac_leistung(S=500, cos_phi=1.0)
        assert r["P"] == A(500.0) and r["Q"] == A(0.0, abs=1e-9)
    def test_phi_aus_cosphi(self):
        assert ac_leistung(S=1000, cos_phi=0.866)["phi_grad"] == A(30.0, rel=1e-2)
    def test_phi_grad_eingabe(self):
        assert ac_leistung(S=1000, phi_grad=60)["cos_phi"] == A(0.5, rel=1e-4)
    def test_s_groesser_gleich_p(self):
        r = ac_leistung(U=230, I=5, cos_phi=0.7)
        assert r["S"] >= r["P"]


class TestBlindstromkompensation:
    """4.2 Kompensationskondensator"""
    def test_c_positiv(self):
        assert blindstromkompensation(P=1000, U=230, f=50, cos1=0.7, cos2=0.95)["C"] > 0
    def test_gleicher_cosphi_c_null(self):
        r = blindstromkompensation(P=1000, U=230, f=50, cos1=0.95, cos2=0.95)
        assert r["C"] == A(0.0, abs=1e-15)
    def test_strom_reduziert(self):
        r = blindstromkompensation(P=1000, U=230, f=50, cos1=0.7, cos2=0.95)
        assert r["I2"] < r["I1"]
    def test_q_differenz(self):
        r = blindstromkompensation(P=1000, U=230, f=50, cos1=0.7, cos2=0.95)
        assert r["Q_komp"] == A(r["Q1"] - r["Q2"])
    def test_ungueltig_cosphi_wirft(self):
        with pytest.raises(ValueError):
            blindstromkompensation(P=1000, U=230, f=50, cos1=1.5, cos2=0.95)


# ============================================================
# Kapitel 5 – RLC-Schwingkreise
# ============================================================

class TestResonanzfrequenz:
    """5.1 f0 = 1/(2π·√(L·C))"""
    def test_f0(self):
        r = resonanzfrequenz(L=100e-3, C=10e-6)
        assert r["f0"] == A(1/(2*math.pi*math.sqrt(100e-3*10e-6)))
    def test_l(self):
        f0 = 1/(2*math.pi*math.sqrt(100e-3*10e-6))
        assert resonanzfrequenz(f0=f0, C=10e-6)["L"] == A(100e-3)
    def test_c(self):
        f0 = 1/(2*math.pi*math.sqrt(100e-3*10e-6))
        assert resonanzfrequenz(f0=f0, L=100e-3)["C"] == A(10e-6)
    def test_xl_gleich_xc(self):
        r = resonanzfrequenz(L=100e-3, C=10e-6)
        XC_res = 1/(2*math.pi*r["f0"]*10e-6)
        assert r["XL_res"] == A(XC_res, rel=1e-4)


class TestReihenschwingkreis:
    """5.2"""
    def test_z_gleich_r_bei_resonanz(self):
        assert reihenschwingkreis(R=10, L=100e-3, C=10e-6)["Z"] == A(10.0)
    def test_q(self):
        r = reihenschwingkreis(R=10, L=100e-3, C=10e-6)
        assert r["Q"] == A((1/10)*math.sqrt(100e-3/10e-6))
    def test_df_gleich_f0_durch_q(self):
        r = reihenschwingkreis(R=10, L=100e-3, C=10e-6)
        assert r["df"] == A(r["f0"]/r["Q"])
    def test_hohe_guete_schmalband(self):
        rH = reihenschwingkreis(R=10,  L=100e-3, C=10e-6)
        rN = reihenschwingkreis(R=100, L=100e-3, C=10e-6)
        assert rH["Q"] > rN["Q"] and rH["df"] < rN["df"]
    def test_charakter_bei_resonanz(self):
        assert reihenschwingkreis(R=10, L=100e-3, C=10e-6)["charakter"] == "resonanz"


class TestParallelschwingkreis:
    """5.3"""
    def test_f0(self):
        r = parallelschwingkreis(R=10, L=100e-3, C=10e-6)
        assert r["f0"] == A(1/(2*math.pi*math.sqrt(100e-3*10e-6)), rel=1e-2)
    def test_r_zu_gross_wirft(self):
        with pytest.raises(ValueError):
            parallelschwingkreis(R=1e9, L=100e-3, C=10e-6)


class TestGueteBandbreite:
    """5.4 Q = f0/Δf"""
    def test_df(self):  assert guete_bandbreite(f0=10_000, Q=50)["df"]  == A(200.0)
    def test_q(self):   assert guete_bandbreite(f0=10_000, df=200)["Q"] == A(50.0)
    def test_f0(self):  assert guete_bandbreite(Q=50, df=200)["f0"]     == A(10_000.0)
    def test_grenzen(self):
        r = guete_bandbreite(f0=10_000, Q=50)
        assert r["f_u"] == A(9900.0) and r["f_o"] == A(10_100.0)


# ============================================================
# Kapitel 6 – Dezibel
# ============================================================

class TestDezibel:
    """6.1 dB = 20·lg(x2/x1)"""
    def test_6db_verdoppelung(self):
        assert dezibel(x1=1, x2=2)["dB"] == A(6.02, rel=1e-3)
    def test_minus6db_halbierung(self):
        assert dezibel(x1=2, x2=1)["dB"] == A(-6.02, rel=1e-3)
    def test_0db_gleich(self):
        assert dezibel(x1=5, x2=5)["dB"] == A(0.0, abs=1e-10)
    def test_x2_aus_x1_db(self):
        assert dezibel(x1=1, dB=20)["x2"] == A(10.0)
    def test_x1_aus_x2_db(self):
        assert dezibel(x2=10, dB=20)["x1"] == A(1.0)
    def test_leistung_3db(self):
        assert dezibel(x1=2, x2=1, leistung_db=True)["dB"] == A(-3.01, rel=1e-2)
    def test_leistung_10db_faktor10(self):
        assert dezibel(x1=1, x2=10, leistung_db=True)["dB"] == A(10.0)
    def test_negativ_wirft(self):
        with pytest.raises(ValueError): dezibel(x1=-1, x2=2)


class TestKettendaempfung:
    """6.3"""
    def test_summe(self):
        assert kettendaempfung([20, -6])["total_db"] == A(14.0)
    def test_alle_null(self):
        r = kettendaempfung([0, 0, 0])
        assert r["total_db"] == A(0.0) and r["ratio_U"] == A(1.0)
    def test_ausgangsspannung(self):
        assert kettendaempfung([20, 20], U_ein=1)["U_aus"] == A(100.0)
    def test_none_ignoriert(self):
        assert kettendaempfung([20, None, -6])["total_db"] == A(14.0)
    def test_leer_wirft(self):
        with pytest.raises(ValueError): kettendaempfung([])


# ============================================================
# Kapitel 7 – Filter
# ============================================================

class TestRCTiefpass:
    """7.1 fg = 1/(2π·R·C)"""
    def test_fg(self):
        assert rc_tiefpass(R=10_000, C=100e-9)["fg"] == A(159.15, rel=1e-3)
    def test_bei_fg_minus3db(self):
        assert rc_tiefpass(R=10_000, C=100e-9, f=159.15)["dB"] == A(-3.01, rel=1e-2)
    def test_h_bei_fg(self):
        assert rc_tiefpass(R=10_000, C=100e-9, f=159.15)["H"] == A(1/math.sqrt(2), rel=1e-3)
    def test_durchlass_nahe_1(self):
        assert rc_tiefpass(R=10_000, C=100e-9, f=1)["H"] > 0.99
    def test_sperr_nahe_0(self):
        assert rc_tiefpass(R=10_000, C=100e-9, f=1e6)["H"] < 0.001
    def test_bereich_label(self):
        assert rc_tiefpass(R=10_000, C=100e-9, f=1)["bereich"] == "durchlass"


class TestRCHochpass:
    """7.2"""
    def test_fg(self):
        assert rc_hochpass(R=10_000, C=100e-9)["fg"] == A(159.15, rel=1e-3)
    def test_bei_fg_minus3db(self):
        assert rc_hochpass(R=10_000, C=100e-9, f=159.15)["dB"] == A(-3.01, rel=1e-2)
    def test_sperr_nahe_0(self):
        fg = rc_hochpass(R=10_000, C=100e-9)["fg"]
        assert rc_hochpass(R=10_000, C=100e-9, f=fg/1000)["H"] < 0.002
    def test_durchlass_nahe_1(self):
        fg = rc_hochpass(R=10_000, C=100e-9)["fg"]
        assert rc_hochpass(R=10_000, C=100e-9, f=fg*1000)["H"] > 0.999


class TestRLFilter:
    """7.3"""
    def test_fg(self):
        assert rl_filter(R=100, L=10e-3)["fg"] == A(100/(2*math.pi*10e-3))
    def test_tiefpass_bei_fg(self):
        fg = rl_filter(R=100, L=10e-3)["fg"]
        assert rl_filter(R=100, L=10e-3, f=fg, tiefpass=True)["dB"] == A(-3.01, rel=1e-2)
    def test_hochpass_bei_fg(self):
        fg = rl_filter(R=100, L=10e-3)["fg"]
        assert rl_filter(R=100, L=10e-3, f=fg, tiefpass=False)["dB"] == A(-3.01, rel=1e-2)


class TestAktiverTiefpass:
    """7.4"""
    def test_fg(self):
        assert aktiver_tiefpass(R=10_000, C=100e-9)["fg"] == A(159.15, rel=1e-3)
    def test_a0_mit_verstaerkung(self):
        assert aktiver_tiefpass(R=10_000, C=100e-9, Rf=9000, R1=1000)["A0"] == A(10.0)
    def test_a0_ohne_ist_1(self):
        assert aktiver_tiefpass(R=10_000, C=100e-9)["A0"] == A(1.0)
    def test_db_plus_verstaerkung(self):
        r = aktiver_tiefpass(R=10_000, C=100e-9, Rf=9000, R1=1000, f=159.15)
        assert r["dB"] == A(20*math.log10(10)-3.01, rel=1e-2)
    def test_nur_rf_wirft(self):
        with pytest.raises(ValueError):
            aktiver_tiefpass(R=10_000, C=100e-9, Rf=9000)


class TestAktiverHochpass:
    """7.5"""
    def test_fg(self):
        assert aktiver_hochpass(R=10_000, C=100e-9)["fg"] == A(159.15, rel=1e-3)
    def test_a0(self):
        assert aktiver_hochpass(R=10_000, C=100e-9, Rf=9000, R1=1000)["A0"] == A(10.0)


class TestSallenKey:
    """7.7"""
    def test_fg(self):
        assert sallen_key(R=10_000, C=100e-9, Q=1/math.sqrt(2))["fg"] == A(159.15, rel=1e-3)
    def test_butterworth_a0(self):
        assert sallen_key(R=10_000, C=100e-9, Q=1/math.sqrt(2))["A0"] == A(3-math.sqrt(2), rel=1e-4)
    def test_instabil(self):
        assert sallen_key(R=10_000, C=100e-9, Q=100)["instabil"] is True
    def test_stabil(self):
        assert sallen_key(R=10_000, C=100e-9, Q=1/math.sqrt(2))["instabil"] is False


class TestNotchFilter:
    """7.8"""
    def test_f0(self):
        assert notch_filter(R=10_000, C=100e-9)["f0"] == A(159.15, rel=1e-3)
    def test_kerbe_bei_f0(self):
        assert notch_filter(R=10_000, C=100e-9, f=159.15)["H"] < 0.01
    def test_weit_weg_nahe_1(self):
        assert notch_filter(R=10_000, C=100e-9, f=159.15*100)["H"] > 0.9


# ============================================================
# Kapitel 8 – Transformator
# ============================================================

class TestUebersetzungsverhaeltnis:
    """8.1 ü = N1/N2"""
    def test_ue(self):     assert uebersetzungsverhaeltnis(N1=100, N2=20)["ue"]       == A(5.0)
    def test_u2(self):     assert uebersetzungsverhaeltnis(N1=100, N2=20, U1=230)["U2"] == A(46.0)
    def test_i2(self):     assert uebersetzungsverhaeltnis(N1=100, N2=20, I1=1)["I2"]  == A(5.0)
    def test_abwaerts(self): assert uebersetzungsverhaeltnis(N1=230, N2=12)["typ"]      == "abwaerts"
    def test_aufwaerts(self): assert uebersetzungsverhaeltnis(N1=12, N2=230)["typ"]     == "aufwaerts"
    def test_1zu1(self):   assert uebersetzungsverhaeltnis(N1=100, N2=100)["typ"]      == "1:1"
    def test_kein_input_wirft(self):
        with pytest.raises(ValueError): uebersetzungsverhaeltnis()


class TestTrafoWirkungsgrad:
    """8.2 η = P2/P1"""
    def test_p2(self):  assert trafo_wirkungsgrad(P1=1000, eta_pct=95)["P2"]    == A(950.0)
    def test_eta(self): assert trafo_wirkungsgrad(P1=1000, P2=950)["eta_pct"]   == A(95.0)
    def test_p1(self):  assert trafo_wirkungsgrad(P2=950, eta_pct=95)["P1"]     == A(1000.0, rel=1e-4)
    def test_verlust(self):
        assert trafo_wirkungsgrad(P1=1000, eta_pct=95)["P_verl"] == A(50.0)


class TestWiderstandstransformation:
    """8.3 R1' = ü²·R2"""
    def test_r2_auf_primaer(self):
        assert widerstandstransformation(ue=5, R2=8)["R1_prim"] == A(200.0)
    def test_r1_auf_sekundaer(self):
        assert widerstandstransformation(ue=5, R1=200)["R2_sek"] == A(8.0)
    def test_lautsprecher_anpassung(self):
        ue = math.sqrt(600/4)
        assert widerstandstransformation(ue=ue, R2=4)["R1_prim"] == A(600.0, rel=1e-4)
    def test_ue_null_wirft(self):
        with pytest.raises(ZeroDivisionError): widerstandstransformation(ue=0, R2=8)


class TestTrafoLastspannung:
    """8.4"""
    def test_du(self):
        r = trafo_lastspannung(U2ll=12, Rcu2=0.5, I2=2)
        assert r["dU"] == A(1.0) and r["U2_last"] == A(11.0)
    def test_i_aus_r_last(self):
        assert trafo_lastspannung(U2ll=12, Rcu2=0.5, R_last=5.5)["I2"] == A(2.0)
    def test_abfall_prozent(self):
        r = trafo_lastspannung(U2ll=12, Rcu2=0.5, I2=2)
        assert r["abfall_pct"] == A(1/12*100, rel=1e-4)


# ============================================================
# Kapitel 9 – Gleichrichter
# ============================================================

class TestSpitzenwertEffektivwert:
    """9.1 Û = Ueff·√2"""
    def test_up(self):   assert spitzenwert_effektivwert(Ue=230)["Up"] == A(230*math.sqrt(2))
    def test_ue(self):   assert spitzenwert_effektivwert(Up=325)["Ue"] == A(325/math.sqrt(2))
    def test_230v(self): assert spitzenwert_effektivwert(Ue=230)["Up"] == A(325.3, rel=1e-3)
    def test_beide_leer_wirft(self):
        with pytest.raises(ValueError): spitzenwert_effektivwert()


class TestEinweggleichrichter:
    """9.2 M1"""
    def test_u_avg(self):
        r = einweggleichrichter(Ueff=12)
        assert r["U_avg_ideal"] == A(r["Up"]/math.pi)
    def test_real_kleiner_ideal(self):
        r = einweggleichrichter(Ueff=12)
        assert r["U_avg_real"] < r["U_avg_ideal"]
    def test_f_brumm_50hz(self):
        assert einweggleichrichter(Ueff=12)["f_brumm_hz"] == 50
    def test_warnung_kleine_spannung(self):
        assert einweggleichrichter(Ueff=0.3)["warnung"] is True
    def test_keine_warnung_normal(self):
        assert einweggleichrichter(Ueff=12)["warnung"] is False


class TestBrueckengleichrichter:
    """9.3 B2"""
    def test_zwei_diodenfaelle(self):
        assert brueckengleichrichter(Ueff=12, UF=0.7)["UF_gesamt"] == A(1.4)
    def test_f_brumm_100hz(self):
        assert brueckengleichrichter(Ueff=12)["f_brumm_hz"] == 100
    def test_real_kleiner_ideal(self):
        r = brueckengleichrichter(Ueff=12)
        assert r["U_avg_real"] < r["U_avg_ideal"]
    def test_u_avg_doppelt_wie_m1(self):
        Up = 12*math.sqrt(2)
        assert brueckengleichrichter(Ueff=12)["U_avg_ideal"] == A(2*Up/math.pi)


class TestSiebkondensator:
    """9.4 U_Br = I/(f·C)"""
    def test_ubr(self):
        assert siebkondensator(C=1000e-6, I=0.5, f_brumm=100)["U_br"] == A(5.0)
    def test_c(self):
        assert siebkondensator(I=0.5, U_br=1.0, f_brumm=100)["C"] == A(5000e-6)
    def test_i_max(self):
        assert siebkondensator(C=1000e-6, U_br=5.0, f_brumm=100)["I_max"] == A(0.5)
    def test_groesseres_c_weniger_brummen(self):
        r1 = siebkondensator(C=1000e-6,  I=0.5)
        r2 = siebkondensator(C=10000e-6, I=0.5)
        assert r2["U_br"] < r1["U_br"]


class TestNetzteilDimensionierung:
    """9.5"""
    def test_c_min_positiv(self):
        assert netzteil_dimensionierung(U_DC=12, I_last=0.5)["C_min"] > 0
    def test_u2_eff(self):
        r = netzteil_dimensionierung(U_DC=12, I_last=0.5)
        assert r["U2_eff"] == A(r["Up_min"]/math.sqrt(2))
    def test_mehr_welligkeit_weniger_c(self):
        r1 = netzteil_dimensionierung(U_DC=12, I_last=0.5, welligkeit_pct=1)
        r2 = netzteil_dimensionierung(U_DC=12, I_last=0.5, welligkeit_pct=5)
        assert r2["C_min"] < r1["C_min"]


# ============================================================
# Kapitel 10 – Thermik
# ============================================================

class TestWaermewiderstand:
    """10.1 ΔT = P_V·R_th"""
    def test_dt(self):  assert waermewiderstand(PV=10, Rth=5)["dT"]  == A(50.0)
    def test_rth(self): assert waermewiderstand(PV=10, dT=50)["Rth"] == A(5.0)
    def test_pv(self):  assert waermewiderstand(Rth=5, dT=50)["PV"]  == A(10.0)
    def test_pv_null_wirft(self):
        with pytest.raises(ZeroDivisionError): waermewiderstand(dT=5, PV=0)


class TestKuehlkoerper:
    """10.2"""
    def test_rth_ges(self):
        r = kuehlkoerper_dimensionierung(Tj=150, Tamb=25, PV=10, Rjc=5)
        assert r["Rth_ges_max"] == A(12.5)
    def test_rsa(self):
        r = kuehlkoerper_dimensionierung(Tj=150, Tamb=25, PV=10, Rjc=5, Rcs=0.2)
        assert r["Rsa_max"] == A(7.3)
    def test_unmoeglich(self):
        r = kuehlkoerper_dimensionierung(Tj=150, Tamb=25, PV=100, Rjc=5)
        assert r["Rsa_max"] < 0 and r["empfehlung"] == "unmöglich"
    def test_kein_kuehlkoerper_noetig(self):
        r = kuehlkoerper_dimensionierung(Tj=150, Tamb=25, PV=0.1, Rjc=5)
        assert r["empfehlung"] == "kein Kühlkörper nötig"


class TestThermischeStabilitaet:
    """10.3 T_betr = T_amb + I²·R·R_th"""
    def test_t_betr(self):
        assert thermische_stabilitaet(R20=100, I=1, Rth=2, Tamb=25)["T_betr"] == A(225.0)
    def test_pv(self):
        assert thermische_stabilitaet(R20=100, I=2, Rth=1, Tamb=25)["PV"] == A(400.0)
    def test_kein_strom_kein_dt(self):
        assert thermische_stabilitaet(R20=100, I=0, Rth=5, Tamb=25)["dT"] == A(0.0)
    def test_warnung_bei_ueberschreitung(self):
        r = thermische_stabilitaet(R20=100, I=5, Rth=10, Tamb=25, Tmax=100)
        assert r["warnung"] is True
    def test_keine_warnung_wenn_ok(self):
        r = thermische_stabilitaet(R20=1, I=1, Rth=1, Tamb=25, Tmax=200)
        assert r["warnung"] is False