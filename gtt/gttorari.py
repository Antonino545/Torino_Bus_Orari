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
    now = datetime.datetime.now(pytz.timezone('Europe/Rome'))
    return (hours * 60 + minutes) - (now.hour * 60 + now.minute)


def printout(data):
    """
    This function formats the bus line data for output.

    Parameters:
    data (str): The bus line data.

    Returns:
    str: The formatted bus line data.
    """
    if data == "Errore: Fermata non trovata o sito non raggiungibile" or data == "":
        return data
    return ''.join([
                       f"Linea: {bus_line} ({direction})<br>Passaggi: {pas}<br>Prossimo passaggio: {'In arrivo' if int(nextpass) <= 1 else nextpass if nextpass != 'Non disponibile' else 'Non disponibile'}<br>"
                       for bus_line, pas, direction, nextpass in data])


def get_bus_stop_data(stop_id, url, pass_type):
    data = api_data_json(url)
    if not data[0][pass_type]:
        raise Exception("Errore: Fermata non trovata o sito non raggiungibile")
    stops = []
    for i in data:
        pas = ' '.join(i[pass_type])
        stops.append((i['Linea'], pas, i['Direzione'], next_pass(i[pass_type][0])))
    return stops


def Bus_stop_GTT(stop_id):
    """
    This function retrieves the bus line data for a specific stop.

    Parameters:
    stop (str): The stop to retrieve the bus line data for.

    Returns:
    list: The bus line data for the stop.
    str: The stop.
    """
    url = f"https://www.gtt.to.it/cms/index.php?option=com_gtt&task=palina.getTransitiOld&palina={stop_id}&bacino=U&realtime=true&get_param=value"
    return get_bus_stop_data(stop_id, url, 'PassaggiRT')


def Bus_stop_API(stop_id):
    url = f"https://gpa.madbob.org/query.php?stop={stop_id}"
    jsondata = api_data_json(url)
    orari_unificati = {passaggio['line']: {'orari': []} for passaggio in jsondata[:5]}
    for passaggio in jsondata[:5]:
        orari_unificati[passaggio['line']]['orari'].append(
            (datetime.datetime.strptime(passaggio['hour'], '%H:%M:%S')).strftime('%H:%M') + (
                '*' if passaggio['realtime'] else ''))
    return [(linea, ' '.join(info['orari']), "Direzione non disponibile",
             next_pass(' '.join(info['orari']).replace("*", ""))) for linea, info in orari_unificati.items()]


def gttorari_stop_line(stop, line):
    line = str(line)
    try:
        data = Bus_stop_GTT(stop)
    except:
        try:
            data = Bus_stop_API(stop)
        except Exception as err:
            return f"Errore:{err}"
    return [x for x in data if x[0] == line]
