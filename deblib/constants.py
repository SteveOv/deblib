""" Common constants from IAU 2015 recommendations. """
# pylint: disable=no-name-in-module, no-member, invalid-name
from astropy import constants as consts
from astropy.constants import iau2015
from uncertainties import ufloat

G = ufloat(consts.G.value, consts.G.uncertainty)

M_sun = ufloat(iau2015.M_sun.si.value, iau2015.M_sun.si.uncertainty)

R_sun = ufloat(iau2015.R_sun.si.value, iau2015.R_sun.si.uncertainty)

# For these astropy have zero uncertainty value
c = consts.c.si.value

h = consts.h.si.value

k_B = consts.k_B.si.value
