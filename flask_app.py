from flask import Flask, render_template, request, session
from petprocessing import petcalc
from petprocessingprognose import petcalcprognose
import numpy as np
import Solweig_v2015_metdata_noload as metload
import clearnessindex_2013b as ci
import requests
import json
import base64
import pandas as pd


app = Flask(__name__)
app.config["DEBUG"] = True
app.config["SECRET_KEY"] = "klefiedoedfoiefnnoefnveodf"

calcresult = []
result = []

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/petresult', methods=["GET", "POST"])
def petresult():
    return render_template("petresult.html", result=result)

@app.route('/prognoseerror', methods=["GET", "POST"])
def prognoseerror():
    return render_template("prognoseerror.html", result=result)

@app.route('/prognose', methods=["GET", "POST"])
def prognose():
    if request.method == "GET":
        return render_template("prognose.html")

    if request.method == "POST":
        city = request.form["city"]
        if city == 'Gothenburg, Sweden':
            url = 'https://api.github.com/repos/David-Rayner-GVC/pet_data/contents/json/Gothenburg.json'
            lat = 57.7
            lon = 12.0
            UTC = 1
        else:
            return render_template("prognoseerror.html", result='Prognose for ' + city + ', not found.')

        # download data from github
        req = requests.get(url)
        if req.status_code == requests.codes.ok:
            req = req.json()  # the response is a JSON
            content = base64.b64decode(req['content'])
        else:
            return render_template("petprognoseresult.html", result='Content was not found.')

        dict_loaded = json.loads(content)

        for key, value in dict_loaded['data_vars'].items():
            dict_loaded['data_vars'][key]['data'] = [np.nan if isinstance(x,str) else x for x in value['data'] ]

        timestamp = dict_loaded['coords']['time']['data']

        # putting data in separate vectors
        veclen = timestamp.__len__()
        year = np.empty(veclen, int)
        month = np.empty(veclen, int)
        day = np.empty(veclen, int)
        hour = np.empty(veclen, int)
        minu = np.empty(veclen, int)
        year = np.empty(veclen, int)
        Ta = np.empty(veclen, float)
        RH = np.empty(veclen, float)
        radD = np.empty(veclen, float)
        radI = np.empty(veclen, float)
        radG = np.empty(veclen, float)
        Ws = np.empty(veclen, float)

        for i in range(0, veclen):
            year[i] = int(timestamp[i][0:4])
            month[i] = int(timestamp[i][5:7])
            day[i] = int(timestamp[i][8:10])
            hour[i] = int(timestamp[i][11:13])
            minu[i] = int(timestamp[i][14:16])
            Ta[i] = float(dict_loaded['data_vars']['air_temperature']['data'][i])
            RH[i] = float(dict_loaded['data_vars']['relative_humidity']['data'][i])
            radD[i] = float(dict_loaded['data_vars']['downward_diffuse']['data'][i])
            radI[i] = float(dict_loaded['data_vars']['downward_direct']['data'][i])
            Ws[i] = np.sqrt(float(dict_loaded['data_vars']['eastward_wind']['data'][i])**2 + float(dict_loaded['data_vars']['northward_wind']['data'][i])**2)
            
        with np.errstate(invalid='ignore'):
          radI[radI < 0.] = 0.
          radD[radD < 0.] = 0.
        radG = radD + radI

        # re-create xarray Dataset
        #x_loaded = Dataset.from_dict(dict_loaded)

        # putting data in separate vectors
        #year = np.empty((x_loaded.air_temperature.time.shape[0]), int)

        #uResponse = requests.get(uri)
        #try:
        #    uResponse = requests.get(uri)
        #except requests.ConnectionError:
        #    return "Connection Error"

        #Jresponse = uResponse.text
        #result = json.loads(Jresponse)

        #with urllib.request.urlopen(uri) as url:
        #    result = json.loads(url.read().decode())

        #return '''
        #        <html>
        #            <body>
        #                <div class="container">
        ##                    <p>{result}</p>
        #                    <p><a href="/">Click here to calculate again</a>
        #                <div>
        #            </body>
        #        </html>
        #    '''.format(result=city)

        poi_save = petcalcprognose(Ta, RH, Ws, radG, radD, radI, year, month, day, hour, minu, lat, lon, UTC)

        tab = pd.DataFrame(poi_save[1:,[1,2,22,24,26,33]])
        tab.columns = ['Day of Year', 'Hour','T_air','RH','Tmrt', 'PET']

        tabhtml = tab.to_html(classes='data', header="true")

        doy = poi_save[1:, 1]
        hour = poi_save[1:, 2]
        petres = poi_save[:,26]
        #petres = str(round(poi_save[:,26], 1))

        return render_template("petprognoseresult.html", result1=doy, result2=hour, result3=tabhtml)


@app.route('/petprognoseresult', methods=["GET", "POST"])
def petprognoseresult():
    if request.method == "GET":
        return render_template("petprognoseresult.html", result1=result1, result2=result2, result3=result3)

    if request.method == "POST":
        return render_template("petprognoseresult.html", result1=result1, result2=result2, result3=result3)


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "GET":
        return render_template("main_page.html", calcresult=calcresult)

    if request.method == "POST":
        try:
            month = int(request.form["month"])
        except:
            month = -999
        try:
            day = int(request.form["day"])
        except:
            day = -999
        try:
            hour = int(request.form["hour"])
        except:
            hour = -999
        year = 2019
        minu = 30
        try:
            Ta = float(request.form["Ta"])
        except:
            Ta = -999
        try:
            RH = float(request.form["RH"])
        except:
            RH = -999
        try:
            Ws = float(request.form["Ws"])
        except:
            Ws = -999
        #try:
        #    radG = float(request.form["radG"])
        #except:
        #    errors += "<p>{!r} is not a number.</p>\n".format(request.form["radG"])
        sky = request.form["sky"]

        if month > 12 or month < 0:
            return render_template("petresult.html", result="Incorrect month filled in")
        if day > 31 or day < 0:
            return render_template("petresult.html", result="Incorrect day filled in")
        if hour > 23 or hour < 0:
            return render_template("petresult.html", result="Incorrect hour filled in")
        if Ta > 60 or Ta < -60:
            return render_template("petresult.html", result="Unreasonable air temperature filled in")
        if RH > 100 or RH < 0:
            return render_template("petresult.html", result="Unreasonable relative humidity filled in")
        if Ws > 100 or Ws < 0:
            return render_template("petresult.html", result="Unreasonable Wind speed filled in")

        #day of year
        if (year % 4) == 0:
            if (year % 100) == 0:
                if (year % 400) == 0:
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

        # Currently looked to Gothenburg
        location = {'longitude': 12.0, 'latitude': 57.7, 'altitude': 3.}
        UTC = 1

        # Radiation
        P = -999.
        radG = 40.

        metdata = np.zeros((1, 24)) - 999.
        metdata[0, 0] = year
        metdata[0, 1] = doy
        metdata[0, 2] = hour
        metdata[0, 3] = minu
        metdata[0, 11] = Ta
        metdata[0, 10] = RH

        YYYY, altitude, azimuth, zen, jday, leafon, dectime, altmax = metload.Solweig_2015a_metdata_noload(metdata, location, UTC)
        if altitude > 0.:
            I0, _, Kt, _, _ = ci.clearnessindex_2013b(zen, jday, Ta, RH / 100., radG, location, P)

            if sky == "Clear (100%)":
                radG = I0
            elif sky == "Semi-cloudy (80%)":
                radG = I0 * 0.8
            elif sky == "Cloudy (60%)":
                radG = I0 * 0.6
            else:
                radG = I0 * 0.4

            I0, _, Kt, _, _ = ci.clearnessindex_2013b(zen, jday, Ta, RH / 100., radG, location, P)
        else:
            radG = 0.

        # Main calculation
        if Ta is not None and RH is not None and Ws is not None and radG is not None:
            Tmrt, resultPET, resultUTCI = petcalc(Ta, RH, Ws, radG, year, month, day, hour, minu)
            result = str(round(resultPET, 1))
            return render_template("petresult.html", result=result)

            #'''
            #    <html>
            #        <body>
            #            <div class="container">
            #                <p><font size="14">{result}</font></p>
            #                <p><a href="/"><font size="10">Click here to calculate again</font></a>
            #            <div>
            #        </body>
            #    </html>
            #'''.format(result=testout)

#
#
#from flask import Flask, request, session
#
#from processing import calculate_mode
#
#app = Flask(__name__)
#app.config["DEBUG"] = True
#app.config["SECRET_KEY"] = "klefiedoedfoiefnnoefnveodf"
#
##inputs = []
#
#@app.route("/", methods=["GET", "POST"])
#def mode_page():
#    if "inputs" not in session:
#        session["inputs"] = []
#    errors = ""
#    if request.method == "POST":
#        try:
#            #inputs.append(float(request.form["number"]))
#            session["inputs"].append(float(request.form["number"]))
#            session.modified = True
#        except:
#            errors += "<p>{!r} is not a number.</p>\n".format(request.form["number"])
#
#        if request.form["action"] == "Calculate number":
#            #result = calculate_mode(inputs)
#            result = calculate_mode(session["inputs"])
#            #inputs.clear()
#            session["inputs"].clear()
#            session.modified = True
#            return '''
#                <html>
#                    <body>
#                        <p>{result}</p>
#                        <p><a href="/">Click here to calculate again</a>
#                    </body>
#                </html>
#            '''.format(result=result)
#
##    if len(inputs) == 0:
#    if len(session["inputs"]) == 0:
#        numbers_so_far = ""
#    else:
#        numbers_so_far = "<p>Numbers so far:</p>"
#        for number in session["inputs"]:
#        #for number in inputs:
#            numbers_so_far += "<p>{}</p>".format(number)
#
#    return '''
#        <html>
#            <body>
#                {numbers_so_far}
#                {errors}
#                <p>Enter your number:</p>
#                <form method="post" action=".">
#                    <p><input name="number" /></p>
#                    <p><input type="submit" name="action" value="Add another" /></p>
#                    <p><input type="submit" name="action" value="Calculate number" /></p>
#                </form>
#            </body>
#        </html>
#    '''.format(numbers_so_far=numbers_so_far, errors=errors)
#



#from flask import Flask, request
#from processing import do_calculation
#
#app = Flask(__name__)
#app.config["DEBUG"] = True
#
#@app.route("/", methods=["GET", "POST"])
#def adder_page():
#    errors = ""
#    if request.method == "POST":
#        number1 = None
#        number2 = None
#        try:
#            number1 = float(request.form["number1"])
#        except:
#            errors += "<p>{!r} is not a number.</p>\n".format(request.form["number1"])
#        try:
#            number2 = float(request.form["number2"])
#        except:
#            errors += "<p>{!r} is not a number.</p>\n".format(request.form["number2"])
#        if number1 is not None and number2 is not None:
#            result = do_calculation(number1, number2)
#            return '''
#                <html>
#                   <body>
#                        <p>The result is {result}</p>
#                        <p><a href="/">Click here to calculate again</a>
#                    </body>
#                </html>
#            '''.format(result=result)
#
#    return '''
#        <html>
#            <body>
#                {errors}
#                <p>Enter your numbers:</p>
#                <form method="post" action=".">
#                    <p><input name="number1" /></p>
#                    <p><input name="number2" /></p>
#                    <p><input type="submit" value="Do calculation" /></p>
#                </form>
#            </body>
#        </html>
#    '''.format(errors=errors)
