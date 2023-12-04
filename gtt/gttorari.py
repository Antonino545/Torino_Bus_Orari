import datetime
import pytz

from gtt.extra import api_data_json


def next_pass(pas):
    """
    This function calculates the time in minutes until the next bus pass.

    Parameters:
    pas (str): The time of the next bus pass in the format 'HH:MM'.

    Returns:
    int: The time in minutes until the next bus pass.
    """
    hours, minutes = map(int, pas.split(' ')[0].split(':'))
    rome_timezone = pytz.timezone('Europe/Rome')  # Set the time zone to Rome
    now = datetime.datetime.now(rome_timezone)
    nextpass = (hours * 60 + minutes) - (now.hour * 60 + now.minute)
    return nextpass


def printout(data):
    """
    This function formats the bus line data for output.

    Parameters:
    data (str): The bus line data.

    Returns:
    str: The formatted bus line data.
    """
    var = ""
    if data == "Errore: Fermata non trovata o sito non raggiungibile" or data == "":
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


def Bus_stop_GTT(stop_id):
    """
    This function retrieves the bus line data for a specific stop.

    Parameters:
    stop (str): The stop to retrieve the bus line data for.

    Returns:
    list: The bus line data for the stop.
    str: The stop.
    """
    url = (f" https://www.gtt.to.it/cms/index.php?option=com_gtt&task=palina.getTransitiOld&palina={stop_id}&bacino=U"
           f"&realtime=true&get_param=value")
    data = api_data_json(url)
    stops = []
    if data[0]['PassaggiRT'] == [] and data[0]['PassaggiPR'] == []:
        raise Exception("Errore: Fermata non trovata o sito non raggiungibile")
    pas = ""
    for i in data:
        if not i['PassaggiRT']:
            for passaggi in i["PassaggiPR"]:
                pas = pas + str(passaggi) + " "
            nextpass = next_pass(i["PassaggiPR"][0])
        else:
            for passaggi in i['PassaggiRT']:
                pas = pas + str(passaggi) + "* "
            nextpass = next_pass(i['PassaggiRT'][0])
        stops.append((i['Linea'], pas, i['Direzione'], nextpass))
        pas = ""
    return stops


def Bus_stop_API(stop_id):
    url = "https://gpa.madbob.org/query.php?stop=" + str(stop_id)
    jsondata = api_data_json(url)
    orari_unificati = {}
    for count, passaggio in enumerate(jsondata):
        if count > 4:
            break
        line = passaggio['line']
        orario = (datetime.datetime.strptime(passaggio['hour'], '%H:%M:%S')).strftime('%H:%M')
        realtime = passaggio['realtime']
        orari_unificati.setdefault(line, {'orari': []})
        if realtime:
            orari_unificati[line]['orari'].append(orario + '*')
        else:
            orari_unificati[line]['orari'].append(orario)
    stops = [(linea, ' '.join(info['orari']), "Direzione non disponibile",
              next_pass(' '.join(info['orari']).replace("*", "")))
             for linea, info in orari_unificati.items()]
    return stops


def gttorari_stop_line(stop, line):
    """
    This function retrieves the bus line data for a specific stop and line.

    Parameters:
    stop (str): The stop to retrieve the bus line data for.
    line (str): The line to retrieve the bus line data for.

    Returns:
    list: The bus line data for the stop and line.
    str: The stop.
    """
    line = str(line)
    try:
        data = Bus_stop_GTT(stop)
    except Exception as err:
        print(f"Errore GTT: {err}")
        print("Use API")
        try:
            data = Bus_stop_API(stop)
        except Exception as err:
            print(f"Errore API: {err}")
            return "Errore:" + str(err)
    data = [x for x in data if x[0] == line]
    return data
