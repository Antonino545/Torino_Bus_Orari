import os

import requests
import json
from datetime import datetime, timedelta
import sqlite3


def do_curl(body):
    url = 'https://plan.muoversiatorino.it/otp/routers/mato/index/graphql'
    headers = {'Content-Type': 'application/json'}
    response = requests.post(url, data=body, headers=headers)
    return response.json()


def probe_stop(stop):
    request = {
        "id": "q01",
        "query": """
            query StopRoutes($id_0:String!,$startTime_1:Long!,$timeRange_2:Int!,$numberOfDepartures_3:Int!) {
                stop(id:$id_0) {
                    id,
                    ...F2
                }
            }
            fragment F0 on Alert {
                id,
                alertDescriptionText,
                alertHash,
                alertHeaderText,
                alertSeverityLevel,
                alertUrl,
                effectiveEndDate,
                effectiveStartDate,
                alertDescriptionTextTranslations {
                    language,
                    text
                },
                alertHeaderTextTranslations {
                    language,
                    text
                },
                alertUrlTranslations {
                    language,
                    text
                }
            }
            fragment F1 on Route {
                alerts {
                    id,
                    ...F0
                },
                id
            }
            fragment F2 on Stop {
                _stoptimesWithoutPatterns4nTcNn:stoptimesWithoutPatterns(
                    startTime:$startTime_1,
                    timeRange:$timeRange_2,
                    numberOfDepartures:$numberOfDepartures_3,
                    omitCanceled:false
                ) {
                    realtimeState,
                    trip {
                        pattern {
                            code,
                            id
                        },
                        route {
                            gtfsId,
                            shortName,
                            longName,
                            mode,
                            color,
                            id,
                            ...F1
                        },
                        id
                    }
                },
                id
            }
        """,
        "variables": {
            "id_0": f"gtt:{stop}",
            "startTime_1": int(datetime.now().timestamp()),
            "timeRange_2": 900,
            "numberOfDepartures_3": 100
        }
    }

    result = do_curl(json.dumps(request))

    if 'data' not in result or 'stop' not in result['data']:
        print(f"Error fetching data: {result}")
        return []

    stop_id = result['data']['stop']['id']

    offset = 60 * 60 * 2

    request = {
        "id": "q02",
        "query": """
            query StopPageContentContainer_StopRelayQL($id_0:ID!,$startTime_1:Long!,$timeRange_2:Int!,$numberOfDepartures_3:Int!) {
                node(id:$id_0) {
                    ...F2
                }
            }
            fragment F1 on Stoptime {
                realtimeState,
                realtimeDeparture,
                scheduledDeparture,
                realtimeArrival,
                scheduledArrival,
                realtime,
                trip {
                    pattern {
                        route {
                            shortName,
                            id
                        },
                        id
                    },
                    id
                }
            }
            fragment F2 on Stop {
                _stoptimesWithoutPatterns1WnWVl:stoptimesWithoutPatterns(
                    startTime:$startTime_1,
                    timeRange:$timeRange_2,
                    numberOfDepartures:$numberOfDepartures_3,
                    omitCanceled:false
                ) {
                    ...F1
                },
                id
            }
        """,
        "variables": {
            "id_0": stop_id,
            "startTime_1": int(datetime.now().timestamp()),
            "timeRange_2": offset,
            "numberOfDepartures_3": 100
        }
    }

    result = do_curl(json.dumps(request))
    ret = []

    for prop, data in result['data']['node'].items():
        if prop.startswith('_stoptimes'):
            for row in data:
                ret.append({
                    'line': row['trip']['pattern']['route']['shortName'],
                    'hour': (datetime.today()),
                    'realtime': row['realtimeState'] == 'UPDATED'
                })

    return ret


def create_database(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS stops (
            stop INTEGER,
            line INTEGER,
            hour VARCHAR(10),
            realtime BOOLEAN,
            date DATETIME
        )
    ''')
    conn.commit()
    return conn


import os
import sqlite3

import os
import sqlite3

def ask_stop(stop):
    db_path = 'gtt.db'

    if not os.path.exists(db_path):
        db = create_database(db_path)
    else:
        db = sqlite3.connect(db_path)

    query = "SELECT * FROM stops WHERE stop = ? AND strftime('%s', 'now') - strftime('%s', date) < 300"
    data = db.execute(query, (stop,))
    ret = []

    for r in data.fetchall():
        # Extract hours and minutes without seconds
        formatted_time = r[2].split()[1].split('+')[0].rsplit(':', 1)[0]

        ret.append({
            'line': r[1],
            'hour': formatted_time,
            'realtime': 'true' if r[3] else 'false'
        })

    if not ret:
        fetch = probe_stop(stop)
        if not fetch:
            return []

        db.execute("DELETE FROM stops WHERE stop = ?", (stop,))
        for f in fetch:
            query = "INSERT INTO stops (stop, line, hour, realtime, date) VALUES (?, ?, ?, ?, datetime('now'))"
            db.execute(query, (stop, f['line'], f['hour'], 1 if f['realtime'] else 0))

        ret = fetch

    db.commit()
    db.close()

    # Return the result as a Python object
    return ret



if __name__ == "__main__":
    stop = input('Enter stop: ')
    if stop.isdigit():
        data = ask_stop(stop)
        for d in data:
            print(f"{d['line']} {d['hour']} { d['realtime']}")
