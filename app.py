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


@app.route('/chi_sono')
def chi_sono():
    return render_template('whoare.html')


@app.route('/fermata/<int:fermata>', methods=['GET'])
def get_fermata(fermata):
    string = "I passaggi per la fermata " + str(fermata) + " sono: <br>"
    gtt = gttorari.printout(gttorari.gttorari_stop(fermata))

    if (gtt != "Errore: Fermata non trovata o sito non raggiungibile") and (gtt is not None):
        return string + gtt
    else:
        return gtt
