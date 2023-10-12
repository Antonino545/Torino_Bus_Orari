from flask import Flask, jsonify, render_template
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
    return string + gttorari.printout(gttorari.gttorari_stop(fermata))


@app.route('/fermata/<int:fermata>/<int:line>', methods=['GET'])
def get_fermata_line(fermata, line):
    string = "i passaggi per la fermata " + str(fermata) + " sono: <br>"

    return string + gttorari.printout(gttorari.gttorari_stop_line(fermata, line))


@app.route('/flutter/fermata/<int:fermata>/json', methods=['GET'])
def get_fermata_json(fermata):
    return jsonify(gttorari.gttorari_stop(fermata))


@app.route('/flutter/fermata/<int:fermata>/<int:line>/json', methods=['GET'])
def get_fermata_line_json(fermata, line):
    return jsonify(gttorari.gttorari_stop_line(fermata, line))
