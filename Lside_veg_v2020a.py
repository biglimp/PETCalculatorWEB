import numpy as np
from Lvikt_veg import Lvikt_veg

def Lside_veg_v2020a(svfS,svfW,svfN,svfE,svfEveg,svfSveg,svfWveg,svfNveg,svfEaveg,svfSaveg,svfWaveg,svfNaveg,azimuth,altitude,Ta,Tw,SBC,ewall,Ldown,esky,t,F_sh,CI,LupE,LupS,LupW,LupN,L_ani,Ldown_i):

    # This m-file is the current one that estimates L from the four cardinal points 20100414
    
    #Building height angle from svf
    svfalfaE=np.arcsin(np.exp((np.log(1-svfE))/2))
    svfalfaS=np.arcsin(np.exp((np.log(1-svfS))/2))
    svfalfaW=np.arcsin(np.exp((np.log(1-svfW))/2))
    svfalfaN=np.arcsin(np.exp((np.log(1-svfN))/2))
    
    vikttot=4.4897
    aziW=azimuth+t
    aziN=azimuth-90+t
    aziE=azimuth-180+t
    aziS=azimuth-270+t
    
    F_sh = 2*F_sh-1  #(cylindric_wedge scaled 0-1)
    
    c=1-CI
    Lsky_allsky = esky*SBC*((Ta+273.15)**4)*(1-c)+c*SBC*((Ta+273.15)**4)
    
    ## Least
    [viktveg, viktwall, viktsky, viktrefl] = Lvikt_veg(svfE, svfEveg, svfEaveg, vikttot)

    if altitude > 0:  # daytime
        alfaB=np.arctan(svfalfaE)
        betaB=np.arctan(np.tan((svfalfaE)*F_sh))
        betasun=((alfaB-betaB)/2)+betaB
        # betasun = np.arctan(0.5*np.tan(svfalfaE)*(1+F_sh)) #TODO This should be considered in future versions
        if (azimuth > (180-t))  and  (azimuth <= (360-t)):
            Lwallsun=SBC*ewall*((Ta+273.15+Tw*np.sin(aziE*(np.pi/180)))**4)*\
                viktwall*(1-F_sh)*np.cos(betasun)*0.5
            Lwallsh=SBC*ewall*((Ta+273.15)**4)*viktwall*F_sh*0.5
        else:
            Lwallsun=0
            Lwallsh=SBC*ewall*((Ta+273.15)**4)*viktwall*0.5
    else: #nighttime
        Lwallsun=0
        Lwallsh=SBC*ewall*((Ta+273.15)**4)*viktwall*0.5

    if L_ani == 1:
        #Lsky = Ldown * 0.5
        Lveg=SBC*ewall*((Ta+273.15)**4)*viktveg*0.5
        Lground=LupE*0.5
        Lrefl=(Ldown_i+LupE)*(viktrefl)*(1-ewall)*0.5
        Least=Lwallsun+Lwallsh+Lveg+Lground+Lrefl
        #Least = Lsky + Lwallsun + Lwallsh + Lveg + Lground + Lrefl
    else:
        Lsky = ((svfE + svfEveg - 1) * Lsky_allsky) * viktsky * 0.5
        Lveg = SBC * ewall * ((Ta + 273.15) ** 4) * viktveg * 0.5
        Lground = LupE * 0.5
        Lrefl = (Ldown + LupE) * (viktrefl) * (1 - ewall) * 0.5
        Least = Lsky + Lwallsun + Lwallsh + Lveg + Lground + Lrefl

    # print('East',Lveg[0,59], Lground[0,59], Lrefl[0,59], Least[0,59])

    Lsky = ((svfE + svfEveg - 1) * Lsky_allsky) * viktsky * 0.5
    Lveg = SBC * ewall * ((Ta + 273.15) ** 4) * viktveg * 0.5
    Lground = LupE * 0.5
    Lrefl = (Ldown_i + LupE) * (viktrefl) * (1 - ewall) * 0.5
    Least_i = Lsky + Lwallsun + Lwallsh + Lveg + Lground + Lrefl

    # print(Lsky[0,59],Lveg[0, 59], Lground[0, 59], Lrefl[0, 59], Least_i[0, 59])

    Lsky_t = Lsky

    # clear alfaB betaB betasun Lsky Lwallsh Lwallsun Lveg Lground Lrefl viktveg viktwall viktsky
    
    ## Lsouth
    [viktveg,viktwall,viktsky,viktrefl]=Lvikt_veg(svfS,svfSveg,svfSaveg,vikttot)
    
    if altitude>0: # daytime
        alfaB=np.arctan(svfalfaS)
        betaB=np.arctan(np.tan((svfalfaS)*F_sh))
        betasun=((alfaB-betaB)/2)+betaB
        # betasun = np.arctan(0.5*np.tan(svfalfaS)*(1+F_sh))
        if (azimuth <= (90-t))  or  (azimuth > (270-t)):
            Lwallsun=SBC*ewall*((Ta+273.15+Tw*np.sin(aziS*(np.pi/180)))**4)*\
                viktwall*(1-F_sh)*np.cos(betasun)*0.5
            Lwallsh=SBC*ewall*((Ta+273.15)**4)*viktwall*F_sh*0.5
        else:
            Lwallsun=0
            Lwallsh=SBC*ewall*((Ta+273.15)**4)*viktwall*0.5
    else: #nighttime
        Lwallsun=0
        Lwallsh=SBC*ewall*((Ta+273.15)**4)*viktwall*0.5

    if L_ani == 1:
        #Lsky = Ldown * 0.5
        Lveg=SBC*ewall*((Ta+273.15)**4)*viktveg*0.5
        Lground=LupS*0.5
        Lrefl=(Ldown_i+LupS)*(viktrefl)*(1-ewall)*0.5
        Lsouth=Lwallsun+Lwallsh+Lveg+Lground+Lrefl
        #Lsouth = Lsky + Lwallsun + Lwallsh + Lveg + Lground + Lrefl
    else:
        Lsky = ((svfS + svfSveg - 1) * Lsky_allsky) * viktsky * 0.5
        Lveg = SBC * ewall * ((Ta + 273.15) ** 4) * viktveg * 0.5
        Lground = LupS * 0.5
        Lrefl = (Ldown + LupS) * (viktrefl) * (1 - ewall) * 0.5
        Lsouth = Lsky + Lwallsun + Lwallsh + Lveg + Lground + Lrefl

    # print('South',Lveg[0, 59], Lground[0, 59], Lrefl[0, 59], Lsouth[0, 59])

    Lsky = ((svfS + svfSveg - 1) * Lsky_allsky) * viktsky * 0.5
    Lveg = SBC * ewall * ((Ta + 273.15) ** 4) * viktveg * 0.5
    Lground = LupS * 0.5
    Lrefl = (Ldown_i + LupS) * (viktrefl) * (1 - ewall) * 0.5
    Lsouth_i = Lsky + Lwallsun + Lwallsh + Lveg + Lground + Lrefl

    # print(Lsky[0,59],Lveg[0, 59], Lground[0, 59], Lrefl[0, 59], Lsouth_i[0, 59])

    Lsky_t = Lsky_t + Lsky

    # clear alfaB betaB betasun Lsky Lwallsh Lwallsun Lveg Lground Lrefl viktveg viktwall viktsky
    
    ## Lwest
    [viktveg,viktwall,viktsky,viktrefl]=Lvikt_veg(svfW,svfWveg,svfWaveg,vikttot)
    
    if altitude>0: # daytime
        alfaB=np.arctan(svfalfaW)
        betaB=np.arctan(np.tan((svfalfaW)*F_sh))
        betasun=((alfaB-betaB)/2)+betaB
        # betasun = np.arctan(0.5*np.tan(svfalfaW)*(1+F_sh))
        if (azimuth > (360-t))  or  (azimuth <= (180-t)):
            Lwallsun=SBC*ewall*((Ta+273.15+Tw*np.sin(aziW*(np.pi/180)))**4)*\
                viktwall*(1-F_sh)*np.cos(betasun)*0.5
            Lwallsh=SBC*ewall*((Ta+273.15)**4)*viktwall*F_sh*0.5
        else:
            Lwallsun=0
            Lwallsh=SBC*ewall*((Ta+273.15)**4)*viktwall*0.5
    else: #nighttime
        Lwallsun=0
        Lwallsh=SBC*ewall*((Ta+273.15)**4)*viktwall*0.5

    if L_ani == 1:
        #Lsky = Ldown * 0.5
        Lveg=SBC*ewall*((Ta+273.15)**4)*viktveg*0.5
        Lground=LupW*0.5
        Lrefl=(Ldown_i+LupW)*(viktrefl)*(1-ewall)*0.5
        Lwest=Lwallsun+Lwallsh+Lveg+Lground+Lrefl
        #Lwest = Lsky + Lwallsun + Lwallsh + Lveg + Lground + Lrefl
    else:
        Lsky = ((svfW + svfWveg - 1) * Lsky_allsky) * viktsky * 0.5
        Lveg = SBC * ewall * ((Ta + 273.15) ** 4) * viktveg * 0.5
        Lground = LupW * 0.5
        Lrefl = (Ldown + LupW) * (viktrefl) * (1 - ewall) * 0.5
        Lwest = Lsky + Lwallsun + Lwallsh + Lveg + Lground + Lrefl

    # print('West', Lveg[0, 59], Lground[0, 59], Lrefl[0, 59], Lwest[0, 59])

    Lsky = ((svfW + svfWveg - 1) * Lsky_allsky) * viktsky * 0.5
    Lveg = SBC * ewall * ((Ta + 273.15) ** 4) * viktveg * 0.5
    Lground = LupW * 0.5
    Lrefl = (Ldown_i + LupW) * (viktrefl) * (1 - ewall) * 0.5
    Lwest_i = Lsky + Lwallsun + Lwallsh + Lveg + Lground + Lrefl

    # print(Lsky[0,59],Lveg[0, 59], Lground[0, 59], Lrefl[0, 59], Lwest_i[0, 59])

    Lsky_t = Lsky_t + Lsky

    # clear alfaB betaB betasun Lsky Lwallsh Lwallsun Lveg Lground Lrefl viktveg viktwall viktsky
    
    ## Lnorth
    [viktveg,viktwall,viktsky,viktrefl]=Lvikt_veg(svfN,svfNveg,svfNaveg,vikttot)
    
    if altitude>0: # daytime
        alfaB=np.arctan(svfalfaN)
        betaB=np.arctan(np.tan((svfalfaN)*F_sh))
        betasun=((alfaB-betaB)/2)+betaB
        # betasun = np.arctan(0.5*np.tan(svfalfaN)*(1+F_sh))
        if (azimuth > (90-t))  and  (azimuth <= (270-t)):
            Lwallsun=SBC*ewall*((Ta+273.15+Tw*np.sin(aziN*(np.pi/180)))**4)*\
                viktwall*(1-F_sh)*np.cos(betasun)*0.5
            Lwallsh=SBC*ewall*((Ta+273.15)**4)*viktwall*F_sh*0.5
        else:
            Lwallsun=0
            Lwallsh=SBC*ewall*((Ta+273.15)**4)*viktwall*0.5
    else: #nighttime
        Lwallsun=0
        Lwallsh=SBC*ewall*((Ta+273.15)**4)*viktwall*0.5

    if L_ani == 1:
        #Lsky = Ldown * 0.5
        Lveg=SBC*ewall*((Ta+273.15)**4)*viktveg*0.5
        Lground=LupN*0.5
        Lrefl=(Ldown_i+LupN)*(viktrefl)*(1-ewall)*0.5
        Lnorth=Lwallsun+Lwallsh+Lveg+Lground+Lrefl
        #Lnorth = Lsky + Lwallsun + Lwallsh + Lveg + Lground + Lrefl
    else:
        Lsky = ((svfN + svfNveg - 1) * Lsky_allsky) * viktsky * 0.5
        Lveg = SBC * ewall * ((Ta + 273.15) ** 4) * viktveg * 0.5
        Lground = LupN * 0.5
        Lrefl = (Ldown + LupN) * (viktrefl) * (1 - ewall) * 0.5
        Lnorth = Lsky + Lwallsun + Lwallsh + Lveg + Lground + Lrefl

    # print('North', Lveg[0, 59], Lground[0, 59], Lrefl[0, 59], Lnorth[0, 59])

    Lsky = ((svfN + svfNveg - 1) * Lsky_allsky) * viktsky * 0.5
    Lveg = SBC * ewall * ((Ta + 273.15) ** 4) * viktveg * 0.5
    Lground = LupN * 0.5
    Lrefl = (Ldown_i + LupN) * (viktrefl) * (1 - ewall) * 0.5
    Lnorth_i = Lsky + Lwallsun + Lwallsh + Lveg + Lground + Lrefl

    # print(Lsky[0,59],Lveg[0, 59], Lground[0, 59], Lrefl[0, 59], Lnorth_i[0, 59])

    Lsky_t = Lsky_t + Lsky

    # clear alfaB betaB betasun Lsky Lwallsh Lwallsun Lveg Lground Lrefl viktveg viktwall viktsky
    
    return Least,Lsouth,Lwest,Lnorth,Least_i,Lsouth_i,Lwest_i,Lnorth_i, Lsky_t