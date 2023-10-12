from flask import Flask, jsonify, render_template
import gttorari

app = Flask(__name__)

if __name__ == '__main__':
    app.run()


@app.route("/")
def hello():
    return render_template('index.html')


@app.route('/fermata/<int:fermata>', methods=['GET'])
def get_fermata(fermata):
    return gttorari.printout(gttorari.gttorari_stop(fermata))


@app.route('/fermata/<int:fermata>/<int:line>', methods=['GET'])
def get_fermata_line(fermata, line):
    return gttorari.printout(gttorari.gttorari_stop_line(fermata, line))


@app.route('/flutter/fermata/<int:fermata>/json', methods=['GET'])
def get_fermata_json(fermata):
    return jsonify(gttorari.gttorari_stop(fermata))


@app.route('/flutter/fermata/<int:fermata>/<int:line>/json', methods=['GET'])
def get_fermata_line_json(fermata, line):
    return jsonify(gttorari.gttorari_stop_line(fermata, line))
