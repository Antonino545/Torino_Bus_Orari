import pandas as pd
from flask import Flask, render_template
from gtt import gttorari, extra

stopNum = pd.read_csv("Resources/NewStop.csv")
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

@app.route('/api')
def api():
    return render_template('api.html')

@app.route('/shortcuts')
def shortcuts():
    return render_template('shortcuts.html')


@app.route('/error')
def error():
    return render_template('error.html')


@app.route('/fermata/<int:fermata>', methods=['POST'])
def get_fermata(fermata):
    if fermata not in stopNum['Stop_id'].values:
        return "Errore: Fermata non trovata"
    try:
        data = gttorari.Bus_stop_GTT(fermata)
    except Exception as err:
        print("Use API")
        print(err)
        try:
            data = gttorari.Bus_stop_API(fermata)
        except error as err:
            print(error)
            return "Errore:" + str(err)
    fermata = extra.NameStop(fermata, stopNum)
    if data != "Fermata non trovata o sito non raggiungibile":
        data = str(gttorari.printout(data))
        string = "Fermata:" + str(fermata) + "<br>"
        return string + data
    else:
        return data


@app.route('/fermata/<int:fermata>', methods=['GET'])
def get_stop_web(fermata):
    if fermata not in stopNum['Stop_id'].values:
        return render_template('error.html', error="Fermata non trovata")
    stop = f"{fermata}-{extra.NameStop(fermata, stopNum)}"
    try:
        print("GTT")
        data = gttorari.Bus_stop_GTT(fermata)
    except Exception as err:
        print("Use API")
        print(err)
        try:
            print("GTT API")
            data = gttorari.Bus_stop_API(fermata)
        except error as err:
            print(error)
            return "Errore:" + str(err)
    if data.__contains__("Errore"):
        return render_template('error.html', error=data)
    return render_template('orari.html', data=data, stop=stop)


@app.route('/fermata/<int:fermata>/<string:linea>', methods=['POST'])
def get_linea_post(fermata, linea):
    if fermata not in stopNum['Stop_id'].values:
        return "Errore: Fermata non trovata"
    try:
        data = gttorari.gttorari_stop_line(fermata, linea)
        fermata = extra.NameStop(fermata, stopNum)
        gtt = gttorari.printout(data)
        string = "Fermata:" + fermata + "<br>"
        if (gtt != "Errore: Fermata non trovata o sito non raggiungibile") and (gtt is not None):
            return string + gtt
        else:
            return gtt
    except Exception as err:
        print(err)
        return "Errore: Fermata non trovata o sito non raggiungibile" + str(err)


@app.route('/fermata/<int:fermata>/<string:linea>', methods=['GET'])
def get_linea_web(fermata, linea):
    if fermata not in stopNum['Stop_id'].values:
        return render_template('error.html', error="Fermata non trovata")
    try:
        data = gttorari.gttorari_stop_line(fermata, linea)
        fermata = f"{fermata}-{extra.NameStop(fermata, stopNum)}"
        if data.__contains__("Errore"):
            return render_template('error.html', error=data)
        return render_template('orari.html', data=data, stop=fermata)
    except Exception as err:
        print(err)
        return render_template('error.html', error=err)


if __name__ == '__main__':
    app.run()
