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
    hours, minutes = map(int, pas.split(':'))
    rome_timezone = pytz.timezone('Europe/Rome')  # Set the time zone to Rome
    now = datetime.datetime.now(rome_timezone)
    nextpass = (hours * 60 + minutes) - (now.hour * 60 + now.minute)
    return nextpass


def printout(data):
    """
    This function formats the bus line data for output.

    Parameters:
    data (list): The bus line data.

    Returns:
    str: The formatted bus line data.
    """
    if data == "Errore: Fermata non trovata o sito non raggiungibile" or not data:
        return data
    formatted_data = []
    for bus_line, pas, direction, nextpass in data:
        formatted_data.append(
            f"Linea: {bus_line} ({direction})<br>"
            f"Passaggi: {pas}<br>"
            f"Prossimo passaggio: {'In arrivo' if nextpass <= 1 else f'{nextpass} minuti'}<br>"
        )
    return ''.join(formatted_data)


def get_bus_stop_data(stop_id, url, pass_type):
    data = api_data_json(url)
    if not data or not data[0].get(pass_type):
        raise Exception("Errore: Fermata non trovata o sito non raggiungibile")
    stops = []
    for i in data:
        if not i[pass_type]:
            continue
        pas = ' '.join([p + '*' if pass_type == 'PassaggiRT' else p for p in i[pass_type]])
        nextpass = next_pass(i[pass_type][0].replace('*', ''))
        stops.append((i['Linea'], pas, i['Direzione'], nextpass))
    return stops


def Bus_stop_GTT(stop_id):
    """
    This function retrieves the bus line data for a specific stop.

    Parameters:
    stop_id (str): The stop to retrieve the bus line data for.

    Returns:
    list: The bus line data for the stop.
    """
    url = (f"https://www.gtt.to.it/cms/index.php?option=com_gtt&task=palina.getTransitiOld&palina={stop_id}&bacino=U"
           f"&realtime=true&get_param=value")
    return get_bus_stop_data(stop_id, url, 'PassaggiRT')


def Bus_stop_API(stop_id):
    """
    This function retrieves the bus line data from an API for a specific stop.

    Parameters:
    stop_id (str): The stop to retrieve the bus line data for.

    Returns:
    list: The bus line data for the stop.
    """
    url = f"https://gpa.madbob.org/query.php?stop={stop_id}"
    jsondata = api_data_json(url)
    orari_unificati = {}
    for count, passaggio in enumerate(jsondata):
        if count > 4:
            break
        line = passaggio['line']
        orario = (datetime.datetime.strptime(passaggio['hour'], '%H:%M:%S')).strftime('%H:%M')
        realtime = passaggio['realtime']
        orari_unificati.setdefault(line, {'orari': []})
        orari_unificati[line]['orari'].append(orario + ('*' if realtime else ''))
    stops = [(linea, ' '.join(info['orari']), "Direzione non disponibile",
              next_pass(info['orari'][0].replace("*", "")))
             for linea, info in orari_unificati.items()]
    return stops


def gttorari_stop_line(stop, line):
    """
    This function retrieves and filters bus line data for a specific stop and line.

    Parameters:
    stop (str): The stop to retrieve the bus line data for.
    line (str): The line to filter the bus line data by.

    Returns:
    list: The filtered bus line data.
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
