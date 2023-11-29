import os
import requests


def api_data_json(url):
    """
    This function retrieves JSON data from a given URL.

    Parameters:
    url (str): The URL from which to retrieve the data.

    Returns:
    dict: The JSON data retrieved from the URL.
    str: An error message if the request fails.
    """
    timeout = 5
    try:
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()
    except requests.exceptions.RequestException as err:
        print(f"Errore API: {err}")
        return f"Errore: Impossibile ottenere i dati dall'API "
    return response.json()


def api_data_html(url):
    """
    This function retrieves HTML data from a given URL.

    Parameters:
    url (str): The URL from which to retrieve the data.

    Returns:
    str: The HTML data retrieved from the URL.
    str: An error message if the request fails.
    """
    timeout = 5
    try:
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()
    except requests.exceptions.RequestException as err:
        print(err)
        return f"Errore: Impossibile ottenere i dati dall'API ({err})"
    return response.text


def NameStop(stop, df):
    """
    This function searches for a stop in a DataFrame.

    Parameters:
    stop (str): The stop to search for.
    df (DataFrame): The DataFrame in which to search.

    Returns:
    str: The name of the stop if found.
    None: If the stop is not found.
    """
    result = df[df.iloc[:, 0].astype(str) == str(stop)]
    if not result.empty:
        return result.iloc[0, 1]
    return None


def writefile(file_path, data):
    """
    This function writes data to a file. If the file does not exist, it is created.

    Parameters:
    file_path (str): The path to the file.
    data (str): The data to write to the file.

    Returns:
    None
    """
    try:
        if not os.path.exists(file_path):
            with open(file_path, 'w') as file:
                file.write(data)
        else:
            with open(file_path, 'a') as file:
                file.write(data)
    except Exception as e:
        print(f"Errore nella scrittura del file : {e}")
