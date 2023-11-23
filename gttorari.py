import csv
import datetime

import bs4
import pytz
import requests


def next_pass(pas):
    hours, minutes = map(int, pas.split(' ')[0].split(':'))
    rome_timezone = pytz.timezone('Europe/Rome')  # Set the time zone to Rome
    now = datetime.datetime.now(rome_timezone)
    nextpass = (hours * 60 + minutes) - (now.hour * 60 + now.minute)
    return nextpass


def printwithoudef(data):
    var = ""
    if data == "Errore: Fermata non trovata o sito non raggiungibile":
        return data
    for bus_line, pas, nextpass in data:
        var += "Linea: " + bus_line + " <br>"
        var += "Passaggi: " + pas + "<br>"
        if nextpass == "Non disponibile":
            var += "Prossimo passaggio: Non disponibile <br>"
        elif int(nextpass) <= 1:
            var += "Prossimo passaggio: In arrivo" + "<br>"
        else:
            var += "Prossimo passaggio: " + str(nextpass) + " minuti" + "<br>"
    return var


def printout(data):
    var = ""
    if data == "Errore: Fermata non trovata o sito non raggiungibile":
        return data
    for bus_line, pas, direction, nextpass in data:
        var += "Linea: " + str(bus_line) + " (" + str(direction) + ")<br>"
        var += "Passaggi: " + str(pas) + "<br>"
        if nextpass == "Non disponibile":
            var += "Prossimo passaggio: Non disponibile <br>"
        elif int(nextpass) <= 1:
            var += "Prossimo passaggio: In arrivo" + "<br>"
        else:
            var += "Prossimo passaggio: " + str(nextpass) + " minuti" + "<br>"
    return var


def formatta_orario(input_string):
    result = ''
    for i in range(0, len(input_string), 4):
        result += input_string[i:i + 2] + ':' + input_string[i + 2:i + 4] + ' '
    # Rimuovi lo spazio in eccesso alla fine
    result = result[:-1]
    return result


def gttorari_stop(stop):
    url = f" https://www.gtt.to.it/cms/index.php?option=com_gtt&task=palina.getTransitiOld&palina={stop}&bacino=U&realtime=true&get_param=value"
    data = api_data(url)
    stops = []
    preal =""
    for i in data:
        if i['PassaggiRT'] == []:
            nextpass = "Non disponibile"
            for passaggi in i["PassaggiPR"]:
                preal = preal + str(passaggi)+" "
            pas = preal
        else:
            pas = i['PassaggiRT']
            for passaggi in pas:
                preal= preal + str(passaggi)+"* "
            pas = preal
            nextpass = next_pass(i['PassaggiRT'][0])
        stops.append((i['Linea'], pas, i['Direzione'], nextpass))
        preal = ""
    return stops, stop


def gttorariAPI(stop):
    url = "https://gpa.madbob.org/query.php?stop=" + str(stop)
    dati = api_data(url)
    orari_unificati = {}

    for count, passaggio in enumerate(dati):
        if count > 4:
            break

        linea = passaggio['line']
        orario_dt = datetime.datetime.strptime(passaggio['hour'], '%H:%M:%S')
        orario = orario_dt.strftime('%H:%M')
        realtime = passaggio['realtime']

        orari_unificati.setdefault(linea, {'orari': []})

        if realtime:
            orari_unificati[linea]['orari'].append(orario + '*')
        else:
            orari_unificati[linea]['orari'].append(orario)

    risultato = [(linea, ' '.join(info['orari']).replace("*", ""), next_pass(' '.join(info['orari']).replace("*", "")))
                 for linea, info in orari_unificati.items()]

    return risultato, stop


def api_data(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.exceptions.HTTPError as err:
        print(err)
        return "Errore: Fermata non trovata o sito non raggiungibile"
    return response.json()


def gttorari_stop_line(stop, line):
    line = str(line)
    data, stop = gttorari_stop(stop)
    if data == "Errore: Fermata non trovata o sito non raggiungibile":
        return data
    else:
        data = [x for x in data if x[0] == line]
        return data, stop


def read_csv(file_path):
    with open(file_path, 'r') as infile:
        reader = csv.reader(infile)
        return list(reader)


def NameStop(stop, data):
    for row in data:
        if row[0] == str(stop):
            return row[1]


