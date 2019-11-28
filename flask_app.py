from flask import Flask, redirect, render_template, request, url_for, session
from petprocessing import petcalc

app = Flask(__name__)
app.config["DEBUG"] = True

calcresult = []

@app.route("/", methods=["GET", "POST"])
def index():
    errors = ""
    if request.method == "GET":
        return render_template("main_page.html", calcresult=calcresult)

    if request.method == "POST":
        #year = float(request.form["year"])
        month = int(request.form["month"])
        day = int(request.form["day"])
        hour = int(request.form["hour"])
        #minu = float(request.form["minu"])
        year = 2019
        #month = 6
        #day = 20
        #hour = 12
        minu = 30
        Ta = None
        RH = None
        Ws = None
        radG = None

        try:
            Ta = float(request.form["Ta"])
        except:
            errors += "<p>{!r} is not a number.</p>\n".format(request.form["Ta"])
        try:
            RH = float(request.form["RH"])
        except:
            errors += "<p>{!r} is not a number.</p>\n".format(request.form["RH"])
        try:
            Ws = float(request.form["Ws"])
        except:
            errors += "<p>{!r} is not a number.</p>\n".format(request.form["Ws"])
        try:
            radG = float(request.form["radG"])
        except:
            errors += "<p>{!r} is not a number.</p>\n".format(request.form["radG"])

        if Ta is not None and RH is not None and Ws is not None and radG is not None:
            Tmrt, resultPET, resultUTCI = petcalc(Ta, RH, Ws, radG, year, month, day, hour, minu)
            #resultPET = month
            return '''
                <html>
                    <body>
                        <p>{result}</p>
                        <p><a href="/">Click here to calculate again</a>
                    </body>
                </html>
            '''.format(result=resultPET)


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
