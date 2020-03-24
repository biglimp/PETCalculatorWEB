import numpy as np
from copy import deepcopy

# This function combines the patches from Tregenza (1987)/Robinson & Stone (2004) and the approach by Unsworth & Monteith
# to calculate emissivities of the different parts of the sky vault.

def Lcyl(esky,L_lv, Ta):

    SBC = 5.67051e-8                    # Stefan-Boltzmann's Constant

    deg2rad = np.pi / 180               # Degrees to radians

    skyalt, skyalt_c = np.unique(L_lv[0][:, 0], return_counts=True)   # Unique altitudes in lv, i.e. unique altitude for the patches
    skyzen = 90-skyalt                  # Unique zeniths for the patches

    cosskyzen = np.cos(skyzen * deg2rad)# Cosine of the zenith angles
    sinskyzen = np.sin(skyzen * deg2rad)  # Cosine of the zenith angles

    a_c = 0.67                          # Constant??
    b_c = 0.094                         # Constant??

    ln_u_prec = esky/b_c-a_c/b_c-0.5    # Natural log of the reduced depth of precipitable water
    u_prec = np.exp(ln_u_prec)          # Reduced depth of precipitable water

    owp = u_prec/cosskyzen              # Optical water depth

    log_owp = np.log(owp)               # Natural log of optical water depth

    esky_p = a_c+b_c*log_owp            # Emissivity of each zenith angle, i.e. the zenith angle of each patch

    lsky_p = esky_p * SBC * ((Ta + 273.15) ** 4)    # Longwave radiation of the sky at different altitudes

    p_alt = L_lv[0][:,0]                # Altitudes of the Robinson & Stone patches

    # Calculation of steradian for each patch
    sr = np.zeros((p_alt.shape[0]))
    for i in range(p_alt.shape[0]):
        if skyalt_c[skyalt == p_alt[i]] > 1:
            sr[i] = ((360 / skyalt_c[skyalt == p_alt[i]]) * deg2rad) * (np.sin((p_alt[i] + p_alt[0]) * deg2rad) \
            - np.sin((p_alt[i] - p_alt[0]) * deg2rad))  # Solid angle / Steradian
        else:
            sr[i] = ((360 / skyalt_c[skyalt == p_alt[i]]) * deg2rad) * (np.sin((p_alt[i]) * deg2rad) \
                - np.sin((p_alt[i-1] + p_alt[0]) * deg2rad))  # Solid angle / Steradian

    sr_h = sr * np.cos((90 - p_alt) * deg2rad)  # Horizontal
    sr_v = sr * np.sin((90 - p_alt) * deg2rad)  # Vertical

    sr_h_w = sr_h / np.sum(sr_h)                # Horizontal weight
    sr_v_w = sr_v / np.sum(sr_v)                # Vertical weight

    sr_w = sr / np.sum(sr)

    Lside = np.zeros((p_alt.shape[0]))
    Ldown = np.zeros((p_alt.shape[0]))
    Lsky_t = np.zeros((p_alt.shape[0]))

    # Estimating longwave radiation for each patch to a horizontal or vertical surface
    for idx in skyalt:
        Ltemp = lsky_p[skyalt == idx]
        Lsky_t[p_alt == idx] = (Ltemp / skyalt_c[skyalt == idx])
        Ldown[p_alt == idx] = Ltemp * sr_h_w[p_alt == idx]          # Longwave radiation from each patch on a horizontal surface
        Lside[p_alt == idx] = Ltemp * sr_v_w[p_alt == idx]          # Longwave radiation from each patch on a vertical surface

    Lsky = deepcopy(L_lv)
    Lsky[0][:,2] = Ldown

    test = 0

    return Ldown, Lside, Lsky