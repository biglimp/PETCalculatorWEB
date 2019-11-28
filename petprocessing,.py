import numpy as np
import Solweig_v2015_metdata_noload as metload
import clearnessindex_2013b as ci
#import diffusefraction as df
import Solweig1D_2019a_calc as so
import PET_calculations as p
import UTCI_calculations as utci

def petcalc(Ta, RH, Ws, radG, year, month, day, hour, minu):
    sh = 1.  # 0 if shadowed by building
    vegsh = 1.  # 0 if shadowed by tree
    svfveg = 1.
    svfaveg = 1.
    trans = 1.
    elvis = 0

    # Location and time settings. Should be moved out later on
    UTC = 1
    lat = 57.7
    lon = 12.0

    if lon > 180.:
        lon = lon - 180.

    # Human parameter data. Should maybe be move out later on
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

    cyl = 1
    ani = 1

    # Environmental data. Should maybe bo moved out later on.
    albedo_b = 0.2
    albedo_g = 0.15
    ewall = 0.9
    eground = 0.95
    svf = 0.6

    # Meteorological data, Should maybe be move out later on.
    sensorheight = 10.0
    onlyglobal = 1

    #metfileexist = 0
    #PathMet = None
    metdata = np.zeros((1, 24)) - 999.

    #date = self.calendarWidget.selectedDate()
    #year = date.year()
    #month = date.month()
    #day = date.day()
    #time = self.spinBoxTimeEdit.time()
    #hour = time.hour()
    #minu = time.minute()
    doy = day_of_year(year, month, day)

    #Ta = self.doubleSpinBoxTa.value()
    #RH = self.doubleSpinBoxRH.value()
    #radG = self.doubleSpinBoxradG.value()
    radD = -999.
    radI = -999.
    #Ws = self.doubleSpinBoxWs.value()

    metdata[0, 0] = year
    metdata[0, 1] = doy
    metdata[0, 2] = hour
    metdata[0, 3] = minu
    metdata[0, 11] = Ta
    metdata[0, 10] = RH
    metdata[0, 14] = radG
    metdata[0, 21] = radD
    metdata[0, 22] = radI
    metdata[0, 9] = Ws

    location = {'longitude': lon, 'latitude': lat, 'altitude': 3.}
    YYYY, altitude, azimuth, zen, jday, leafon, dectime, altmax = metload.Solweig_2015a_metdata_noload(metdata, location, UTC)

    svfalfa = np.arcsin(np.exp((np.log((1.-svf))/2.)))

    # %Creating vectors from meteorological input
    DOY = metdata[:, 1]
    hours = metdata[:, 2]
    minu = metdata[:, 3]
    Ta = metdata[:, 11]
    RH = metdata[:, 10]
    radG = metdata[:, 14]
    radD = metdata[:, 21]
    radI = metdata[:, 22]
    P = metdata[:, 12]
    Ws = metdata[:, 9]

    TgK = 0.37
    Tstart = -3.41
    TmaxLST = 15
    TgK_wall = 0.58
    Tstart_wall = -3.41
    TmaxLST_wall = 15

    # If metfile starts at night
    CI = 1.

    if ani == 1:
        skyvaultalt = np.atleast_2d([])
        skyvaultazi = np.atleast_2d([])
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
    poi_save = np.zeros((1, 34))

    # main loop
    for i in np.arange(0, Ta.__len__()):
        # Daily water body temperature
        if (dectime[i] - np.floor(dectime[i])) == 0 or (i == 0):
            Twater = np.mean(Ta[jday[0] == np.floor(dectime[i])])

        # Nocturnal cloudfraction from Offerle et al. 2003
        if (dectime[i] - np.floor(dectime[i])) == 0:
            daylines = np.where(np.floor(dectime) == dectime[i])
            alt = altitude[0][daylines]
            alt2 = np.where(alt > 1)
            rise = alt2[0][0]
            [_, CI, _, _, _] = ci.clearnessindex_2013b(zen[0, i + rise + 1], jday[0, i + rise + 1],
                                                    Ta[i + rise + 1],
                                                    RH[i + rise + 1] / 100., radG[i + rise + 1], location,
                                                    P[i + rise + 1])
            if (CI > 1) or (CI == np.inf):
                CI = 1

        Tmrt, Kdown, Kup, Ldown, Lup, Tg, ea, esky, I0, CI, Keast, Ksouth, Kwest, Knorth, Least, Lsouth, Lwest, \
        Lnorth, KsideI, radIo, radDo, shadow = so.Solweig1D_2019a_calc(svf, svfveg, svfaveg, sh, vegsh,  albedo_b, absK, absL, ewall,
                                                            Fside, Fup, Fcyl,
                                                            altitude[0][i], azimuth[0][i], zen[0][i], jday[0][i],
                                                            onlyglobal, location, dectime[i], altmax[0][i], cyl, elvis,
                                                            Ta[i], RH[i], radG[i], radD[i], radI[i], P[i],
                                                            Twater, TgK, Tstart, albedo_g, eground, TgK_wall, Tstart_wall,
                                                            TmaxLST, TmaxLST_wall, svfalfa, CI, ani, diffsh, trans)

        # Write to array
        poi_save[0, 0] = YYYY[0][i]
        poi_save[0, 1] = jday[0][i]
        poi_save[0, 2] = hours[i]
        poi_save[0, 3] = minu[i]
        poi_save[0, 4] = dectime[i]
        poi_save[0, 5] = altitude[0][i]
        poi_save[0, 6] = azimuth[0][i]
        poi_save[0, 7] = radIo
        poi_save[0, 8] = radDo
        poi_save[0, 9] = radG[i]
        poi_save[0, 10] = Kdown
        poi_save[0, 11] = Kup
        poi_save[0, 12] = Keast
        poi_save[0, 13] = Ksouth
        poi_save[0, 14] = Kwest
        poi_save[0, 15] = Knorth
        poi_save[0, 16] = Ldown
        poi_save[0, 17] = Lup
        poi_save[0, 18] = Least
        poi_save[0, 19] = Lsouth
        poi_save[0, 20] = Lwest
        poi_save[0, 21] = Lnorth
        poi_save[0, 22] = Ta[i]
        poi_save[0, 23] = Tg + Ta[i]
        poi_save[0, 24] = RH[i]
        poi_save[0, 25] = esky
        poi_save[0, 26] = Tmrt
        poi_save[0, 27] = I0
        poi_save[0, 28] = CI
        poi_save[0, 29] = shadow
        poi_save[0, 30] = svf
        poi_save[0, 31] = KsideI


        # Recalculating wind speed based on pwerlaw
        WsPET = (1.1 / sensorheight) ** 0.2 * Ws[i]
        WsUTCI = (10. / sensorheight) ** 0.2 * Ws[i]
        resultPET = p._PET(Ta[i], RH[i], Tmrt[0][i], WsPET, mbody, age, ht, activity, clo, sex)
        poi_save[0, 32] = resultPET
        resultUTCI = utci.utci_calculator(Ta[i], RH[i], Tmrt[0][i], WsUTCI)
        poi_save[0, 33] = resultUTCI

    return Tmrt[0][0], resultPET, resultUTCI

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
