from typing import Optional, Tuple

def woz_belasting(woz_waarde):
    return woz_waarde * 0.1e-2


def eigenwoning_forfait(woz_waarde: float):
    return 5e-3 * woz_waarde


def hypotheek_aftrek(jaarlijkse_rente: float, woz_waarde: float) -> float:
    """Berekent aftrekbaar bedrag

    Args:
        jaarlijkse_rente (float): Jaarlijkse rente van annuitaire of lineaire hypotheek, in geld eenheden
        woz_waarde (float): WOZ waarde in geld_eenheden

    Returns:
        float: Aftrekbaar bedrag, in geld eenheden
    """
    forfait = eigenwoning_forfait(woz_waarde)
    return max(jaarlijkse_rente - forfait, 0)


class Persoon:
    def __init__(self, bruto_jaarloon: float):
        self.bruto_jaarloon = bruto_jaarloon
        self.aftrek = 0

    @property
    def belastbaar_jaarloon(self) -> float:
        return self.bruto_jaarloon - self.aftrek

    @property
    def netto_loon(self) -> float:
        return self.bruto_jaarloon - self.belasting_afdracht

    @property
    def belasting_afdracht(self) -> float:
        return self.loonheffing - self.arbeidskorting - self.algemene_heffingskorting

    @property
    def loonheffing(self) -> float:
        schijf_1 = min(self.belastbaar_jaarloon, 68508) * 37.10e-2
        schijf_2 = max(self.belastbaar_jaarloon - 68508, 0) * 49.50e-2
        return schijf_1 + schijf_2

    @property
    def arbeidskorting(self) -> float:
        if self.belastbaar_jaarloon < 10108:
            return 4.581 * self.belastbaar_jaarloon
        elif self.belastbaar_jaarloon < 21835:
            return 463 + 28.771e-2 * (self.belastbaar_jaarloon - 10108)
        elif self.belastbaar_jaarloon < 35652:
            return 3837 + 2.663e-2 * (self.belastbaar_jaarloon - 21835)
        elif self.belastbaar_jaarloon < 105736:
            return 4205 - 6e-2 * (self.belastbaar_jaarloon - 35652)
        else:
            return 0

    @property
    def algemene_heffingskorting(self) -> float:
        if self.belastbaar_jaarloon < 21043:
            return 2837
        elif self.belastbaar_jaarloon < 68507:
            return 2837 - 5.977e-2 * (self.belastbaar_jaarloon - 21043)
        else:
            return 0

    @property
    def premie_volksverzekeringen(self) -> float:
        """Alleen voor de werkgever"""
        grondslag = min(self.belastbaar_jaarloon, 34712)
        premie_aow = 17.9e-2 * grondslag
        premie_anw = 0.1e-2 * grondslag
        premie_wlz = 9.65e-2 * grondslag
        return premie_aow + premie_anw + premie_wlz


def maandlasten(
    totaal_hypotheek_bedrag: float,
    rente: float = 1.5e-2,
    aflossings_vrij_gedeelte: float = 0.5,
    onderhoud: float = 1e-2,
    persoon: Optional[Persoon] = None,
) -> Tuple[float, float]:
    """Berekent maandlasten van huis, inclusief eventuele hypotheek-rente aftrek.

    Args:
        totaal_hypotheek_bedrag (float): Total hypotheek op huis
        rente (float, optional): Jaarlijks rente percentage. Defaults to 1.5e-2.
        aflossings_vrij_gedeelte (float, optional): Fractie van hypotheek die aflossingvrij is. Tussen 0 en 1. Defaults to 0.5.
        onderhoud (float, optional): Schatting voor jaarlijks percentage die aan onderhouds kosten moeten worden uitgegeven. Defaults to 1e-2.
        persoon (Persoon, optional): Persoon bij wie huis op naam staat voor hypotheek-rente aftrek. Defaults to None.

    Returns:
        Tuple[float, float]: De totale maandelijkse kosten inclusief aflossing, de maandelijkse kosten zonder aflossing.
    """
    aflossing = totaal_hypotheek_bedrag / 360 * (1 - aflossings_vrij_gedeelte)
    kosten_rente = totaal_hypotheek_bedrag * rente / 12
    kosten_onderhoud = onderhoud * totaal_hypotheek_bedrag / 12

    if persoon is not None:
        aftrek = hypotheek_aftrek(totaal_hypotheek_bedrag * rente * (1 - aflossings_vrij_gedeelte), totaal_hypotheek_bedrag)
        persoon_met_aftrek = Persoon(persoon.bruto_jaarloon)
        persoon_met_aftrek.aftrek = aftrek

        teruggave = (persoon_met_aftrek.netto_loon - persoon.netto_loon) / 12

    else:
        teruggave = 0

    return aflossing + kosten_rente + kosten_onderhoud - teruggave