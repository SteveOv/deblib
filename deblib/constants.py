""" Common constants from IAU 2015 recommendations. """
# pylint: disable=no-name-in-module, no-member, invalid-name
from astropy import constants as consts
from astropy.constants import iau2015
from uncertainties import ufloat

G = ufloat(consts.G.value, consts.G.uncertainty)

M_sun = ufloat(iau2015.M_sun.si.value, iau2015.M_sun.si.uncertainty)

R_sun = ufloat(iau2015.R_sun.si.value, iau2015.R_sun.si.uncertainty)

c = ufloat(consts.c.si.value, consts.c.si.uncertainty)

h = ufloat(consts.h.si.value, consts.h.si.uncertainty)

k_B = ufloat(consts.k_B.si.value, consts.k_B.si.uncertainty)
