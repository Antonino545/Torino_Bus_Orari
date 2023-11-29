import pandas as pd
from flask import Flask, render_template
from gtt import gttorari, extra

stopsdata = pd.read_csv("Resources/NewStop.csv")
app = Flask(__name__)


@app.route("/")
def hello():
    return render_template('welcome.html', title='Home')


@app.route('/orari_fermata')
def orari_fermata():
    return "Orari fermata"


@app.route('/whoare')
def chi_sono():
    return render_template('whoare.html')


@app.route('/shortcuts')
def shortcuts():
    return render_template('shortcuts.html')


@app.route('/error')
def error():
    return render_template('error.html')


@app.route('/fermata/<int:fermata>', methods=['POST'])
def get_fermata(fermata):
    try:
        if stopsdata._get_axis(0).__contains__(fermata):
            data, stop = gttorari.gttorari_stop(fermata)
            stop = extra.NameStop(stop, stopsdata)
            if (data != "Fermata non trovata o sito non raggiungibile"):
                data = str(gttorari.printout(data))
                string = "Fermata:" + str(stop) + "<br>"
                return string + data
            else:
                return data
        else:
            return "Errore: Fermata non trovata"
    except Exception as err:
        print(err)
        return "Errore:" + str(err)


@app.route('/fermata/<int:fermata>', methods=['GET'])
def get_stop_web(fermata):
    if stopsdata._get_axis(0).__contains__(fermata):
        data, stop = gttorari.gttorari_stop(fermata)
        stop = f"{stop}-{extra.NameStop(stop, stopsdata)}"
        if data.__contains__("Errore"):
            return render_template('error.html', error=data)
        return render_template('orari.html', data=data, stop=stop)

    else:
        return render_template('error.html', error="Fermata non trovata")


@app.route('/fermata/<int:fermata>/<string:linea>', methods=['POST'])
def get_linea_post(fermata, linea):
    if stopsdata._get_axis(0).__contains__(fermata):
        try:
            data, stop = gttorari.gttorari_stop_line(fermata, linea)
            stop = extra.NameStop(stop, stopsdata)
            gtt = gttorari.printout(data)
            string = "Fermata:" + stop + "<br>"
            if (gtt != "Errore: Fermata non trovata o sito non raggiungibile") and (gtt is not None):
                return string + gtt
            else:
                return gtt
        except Exception as err:
            print(err)
            return "Errore: Fermata non trovata o sito non raggiungibile" + str(err)
    else:
        return "Errore: Fermata non trovata o sito non raggiungibile"


@app.route('/fermata/<int:fermata>/<string:linea>', methods=['GET'])
def get_linea_web(fermata, linea):
    if stopsdata._get_axis(0).__contains__(fermata):
        try:
            data, stop = gttorari.gttorari_stop_line(fermata, linea)
            stop = f"{stop}-{extra.NameStop(stop, stopsdata)}"
            if data.__contains__("Errore"):
                return render_template('error.html', error=data)
            return render_template('orari.html', data=data, stop=stop)
        except Exception as err:
            print(err)
            return render_template('error.html', error=err)
    else:
        return render_template('error.html', error="Fermata non trovata")


if __name__ == '__main__':
    app.run()
