from flask import Flask, render_template

import gttorari

app = Flask(__name__)

if __name__ == '__main__':
    app.run()


@app.route("/")
def hello():
    return render_template('index.html')


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
        gtt, stop = gttorari.gttorari_stop(fermata)
        gtt = gttorari.printout(gtt)
        string = "Fermata:" + stop + "<br>"
        if (gtt != "Errore: Fermata non trovata o sito non raggiungibile") and (gtt is not None):
            return string + gtt
        else:
            return gtt
    except Exception as err:
        print(err)
        return "Errore: Fermata non trovata o sito non raggiungibile"


@app.route('/fermata/<int:fermata>', methods=['GET'])
def get_stop_web(fermata):
    try:
        data, stop = gttorari.gttorari_stop(fermata)
        return render_template('orari.html', data=data, stop=stop)
    except Exception as err:
        print(err)
        return render_template('error.html')
