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


def gttorari_stop(stop):
    """
    This function retrieves the bus line data for a specific stop.

    Parameters:
    stop (str): The stop to retrieve the bus line data for.

    Returns:
    list: The bus line data for the stop.
    str: The stop.
    """
    url = f" https://www.gtt.to.it/cms/index.php?option=com_gtt&task=palina.getTransitiOld&palina={stop}&bacino=U&realtime=true&get_param=value"
    data = api_data_json(url)
    if data.__contains__("Errore"):
        print(f"Errore: Fermata {stop} non trovata o sito non raggiungibile")
        return data, stop
    stops = []
    if data[0]['PassaggiRT'] == [] and data[0]['PassaggiPR'] == []:
        return "Nessun Dato trovato", stop
    pas = ""
    try:
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
        return stops, stop
    except:
        return "Errore: Fermata non trovata o sito non raggiungibile", stop


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
    data, stop = gttorari_stop(stop)
    if data == "Errore: Fermata non trovata o sito non raggiungibile":
        return data
    else:
        data = [x for x in data if x[0] == line]
        return data, stop
