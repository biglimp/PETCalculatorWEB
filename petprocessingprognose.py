import numpy as np
import Solweig_v2015_metdata_noload as metload
import clearnessindex_2013b as ci
#import diffusefraction as df
import Solweig1D_2020a_calc as so
import PET_calculations as p
import UTCI_calculations as utci
#import matplotlib.pylab as plt

def petcalcprognose(Ta, RH, Ws, radG, radD, radI, year, month, day, hour, minu, lat, lon, UTC, elev=3.):

    elvis = 0
    cyl = 1
    anisdiff = 1
    L_ani = 0

    # Location and time settings
    # UTC = 0
    # lat = 57.7
    # lon = 12.0

    if lon > 180.:
        lon = lon - 180.

    # Human parameter data
    absK = 0.70
    absL = 0.95
    pos = 0
    mbody = 75.
    ht = 180 / 100.
    clo = 0.9
    age = 35
    activity = 80.
    sex = 1

    if pos == 0:
        Fside = 0.22
        Fup = 0.06
        height = 1.1
        Fcyl = 0.28
    else:
        Fside = 0.166666
        Fup = 0.166666
        height = 0.75
        Fcyl = 0.2


    # ani = 1

    # Environmental data
    albedo_b = 0.2
    albedo_g = 0.15
    ewall = 0.9
    eground = 0.95
    svf = 0.6
    svfalfa = np.arcsin(np.exp((np.log((1.-svf))/2.)))
    sh = 1.  # 0 if shadowed by building
    vegsh = 1.  # 0 if shadowed by tree
    svfveg = 1.
    svfaveg = 1.
    trans = 1.
    svfbuveg = (svf - (1. - svfveg) * (1. - trans))

    # Meteorological data
    sensorheight = 10.0
    onlyglobal = 0

    metdata = np.zeros((Ta.__len__(), 24)) - 999.

    # doy = day_of_year(year, month, day)

    metdata[:, 0] = year
    for i in range(0,  Ta.__len__()):
        metdata[i, 1] = day_of_year(year[i], month[i], day[i])
    metdata[:, 2] = hour
    metdata[:, 3] = minu
    # metdata[0, 11] = Ta
    # metdata[0, 10] = RH
    # metdata[0, 14] = radG
    # metdata[0, 21] = radD
    # metdata[0, 22] = radI
    # metdata[0, 9] = Ws

    location = {'longitude': lon, 'latitude': lat, 'altitude': elev}
    YYYY, altitude, azimuth, zen, jday, leafon, dectime, altmax = metload.Solweig_2015a_metdata_noload(metdata, location, UTC)

    radI = (radG - radD)/(np.sin(altitude[0][:]*(np.pi/180)))
    with np.errstate(invalid='ignore'):
      radI[radI < 0] = 0.
    for i in range(0,  Ta.__len__()):
        if altitude[0][i] < 0.:
           radG[i] = 0.
        if altitude[0][i] < 1 and radI[i] > radG[i]:
            radI[i]=radG[i]
        if radD[i] > radG[i]:
            radD[i] = radG[i]

    # %Creating vectors from meteorological input
    # DOY = metdata[:, 1]
    # hour = metdata[:, 2]
    # minu = metdata[:, 3]
    # Ta = metdata[:, 11]
    # RH = metdata[:, 10]
    # radG = metdata[:, 14]
    # radD = metdata[:, 21]
    # radI = metdata[:, 22]
    P = metdata[:, 12]
    # Ws = metdata[:, 9]
    Twater = []

    TgK = 0.37
    Tstart = -3.41
    TmaxLST = 15
    TgK_wall = 0.58
    Tstart_wall = -3.41
    TmaxLST_wall = 15

    # If metfile starts at night
    CI = 1.

    if anisdiff == 1:
        skyvaultalt = np.atleast_2d([])
        # skyvaultazi = np.atleast_2d([])
        skyvaultaltint = [6, 18, 30, 42, 54, 66, 78]
        skyvaultaziint = [12, 12, 15, 15, 20, 30, 60]
        for j in range(7):
            for k in range(1, int(360/skyvaultaziint[j]) + 1):
                skyvaultalt = np.append(skyvaultalt, skyvaultaltint[j])

        skyvaultalt = np.append(skyvaultalt, 90)

        diffsh = np.zeros((145))
        svfalfadeg = svfalfa / (np.pi / 180.)
        for k in range(0, 145):
            if skyvaultalt[k] > svfalfadeg:
                diffsh[k] = 1
    else:
        diffsh = []

    #numformat = '%3d %2d %3d %2d %6.5f ' + '%6.2f ' * 29
    poi_save = np.zeros((Ta.__len__(), 34))


    # main loop
    for i in np.arange(1, Ta.__len__()): # starting from 1 as rad[0] is nan
        # print(i)
        # Daily water body temperature
        if (dectime[i] - np.floor(dectime[i])) == 0 or (i == 0):
            Twater = np.mean(Ta[jday[0] == np.floor(dectime[i])])

        # Nocturnal cloudfraction from Offerle et al. 2003
        # Last CI from previous day is used until midnight
        # after which we swap to first CI of following day. 
        if (dectime[i] - np.floor(dectime[i])) == 0:
            daylines = np.where(np.floor(dectime) == dectime[i])
            alt = altitude[0][daylines]
            alt2 = np.where(alt > 1)
            try:
              rise = alt2[0][0]
              [_, CI, _, _, _] = ci.clearnessindex_2013b(zen[0, i + rise + 1], 
                jday[0, i + rise + 1], Ta[i + rise + 1],
                RH[i + rise + 1] / 100., radG[i + rise + 1], location,
                P[i + rise + 1])
            except IndexError as error:
              # there was no hour after sunrise for following day. 
              # Just keep the last CI
              pass
            if (CI > 1) or (CI == np.inf):
                CI = 1

        Tmrt, Kdown, Kup, Ldown, Lup, Tg, ea, esky, I0, CI, Keast, Ksouth, Kwest, Knorth, Least, Lsouth, Lwest, \
        Lnorth, KsideI, radIo, radDo, shadow = so.Solweig1D_2020a_calc(svf, svfveg, svfaveg, sh, vegsh,  albedo_b, absK, absL, ewall,
                                                            Fside, Fup, Fcyl,
                                                            altitude[0][i], azimuth[0][i], zen[0][i], jday[0][i],
                                                            onlyglobal, location, dectime[i], altmax[0][i], cyl, elvis,
                                                            Ta[i], RH[i], radG[i], radD[i], radI[i], P[i],
                                                            Twater, TgK, Tstart, albedo_g, eground, TgK_wall, Tstart_wall,
                                                            TmaxLST, TmaxLST_wall, svfalfa, svfbuveg, CI, anisdiff, diffsh, trans, L_ani)


        # Write to array
        poi_save[i, 0] = YYYY[0][i]
        poi_save[i, 1] = jday[0][i]
        poi_save[i, 2] = hour[i]
        poi_save[i, 3] = minu[i]
        poi_save[i, 4] = dectime[i]
        poi_save[i, 5] = altitude[0][i]
        poi_save[i, 6] = azimuth[0][i]
        poi_save[i, 7] = radIo
        poi_save[i, 8] = radDo
        poi_save[i, 9] = radG[i]
        poi_save[i, 10] = Kdown
        poi_save[i, 11] = Kup
        poi_save[i, 12] = Keast
        poi_save[i, 13] = Ksouth
        poi_save[i, 14] = Kwest
        poi_save[i, 15] = Knorth
        poi_save[i, 16] = Ldown
        poi_save[i, 17] = Lup
        poi_save[i, 18] = Least
        poi_save[i, 19] = Lsouth
        poi_save[i, 20] = Lwest
        poi_save[i, 21] = Lnorth
        poi_save[i, 22] = Ta[i]
        poi_save[i, 23] = Tg + Ta[i]
        poi_save[i, 24] = RH[i]
        poi_save[i, 25] = esky
        poi_save[i, 26] = Tmrt
        poi_save[i, 27] = I0
        poi_save[i, 28] = CI
        poi_save[i, 29] = shadow
        poi_save[i, 30] = svf
        poi_save[i, 31] = KsideI


        # Recalculating wind speed based on pwerlaw
        WsPET = (1.1 / sensorheight) ** 0.2 * Ws[i]
        WsUTCI = (10. / sensorheight) ** 0.2 * Ws[i]
        resultPET = p._PET(Ta[i], RH[i], Tmrt, WsPET, mbody, age, ht, activity, clo, sex)
        poi_save[i, 32] = resultPET
        resultUTCI = utci.utci_calculator(Ta[i], RH[i], Tmrt, WsUTCI)
        poi_save[i, 33] = resultUTCI

    return poi_save

def day_of_year(yyyy, month, day):
        if (yyyy % 4) == 0:
            if (yyyy % 100) == 0:
                if (yyyy % 400) == 0:
                    leapyear = 1
                else:
                    leapyear = 0
            else:
                leapyear = 1
        else:
            leapyear = 0

        if leapyear == 1:
            dayspermonth = [31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
        else:
            dayspermonth = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

        doy = np.sum(dayspermonth[0:month - 1]) + day

        return doy
