import json
import requests
import logging
import pandas as pd
import datetime
from enum import Enum
import logging
import argparse
from secret_loader import token, prod_db, dev_db

notion_version = '2022-06-28'
insert_url = "https://api.notion.com/v1/pages"

class Lang(Enum):
    SPANISH = 'Español'
    GERMAN = 'Deutsch'

class Db(Enum):
    PROD = prod_db
    DEV = dev_db

def read_raw_data(file_path):
    return pd.read_excel(file_path)

def get_translation_entry(database_id, lang, **props):
    data = {
        "parent": {
            "database_id": database_id
        },
        "properties": {
            "Target": {
                "title": [
                    {
                        "text": {
                            "content": props['target_text']
                        }
                    }
                ]
            },
            "Source": {
                "rich_text": [
                    {
                        "type": "text",
                        "text": {
                            "content": props['source_text']
                        }
                    }
                ]
            },
            "Lang": {
                "select": {"name": lang.value}
            },
            "Sekunde": {
                "number": props['seconds']
            },
            "Time_str": {
                "rich_text": [
                    {
                        "type": "text",
                        "text": {
                            "content": props['time_str']
                        }
                    }
                ]
            },
            "Video": {
                "relation": [
                    {
                        "id": props['video_id']
                    }
                ]
            },
            "Date": {
                "date": {
                    "start": datetime.datetime.now().isoformat()
                }
            }
        }
    }
    print('data\n', data)
    return data

def insert_translation(database_id, lang, props):
    # url = f"https://api.notion.com/v1/databases/{database_id}/query"
    url = insert_url
    data = get_translation_entry(database_id, lang, **props)
    # TODO: add retries on timeout
    try:
        r = requests.post(url, headers={
            "Authorization": f"Bearer {token}",
            "Notion-Version": notion_version,
            "Content-Type": "application/json"
        }, timeout=5, data=json.dumps(data))
        # throw error on non-200's
        r.raise_for_status()
    except requests.exceptions.HTTPError as e:
        logging.error(f"status error: {e}")
    except requests.exceptions.Timeout as e:
        logging.error(f"timeout: {e}")
    except requests.exceptions.RequestException as e:
        logging.error(f"general request error: {e}")
    else:
        print("status: ", r.status_code)

def get_second(time):
    if 's' in time:
        return int(time.strip('s'))
    time_by_unit = time.split(":") # 1:13:14
    last_idx = len(time_by_unit)-1
    sec = 0
    for idx, t in enumerate(time_by_unit):
        t_num = int(t)
        # get reverse idx to find power
        # e.g. if time is H:M:S, power for time in H slot
        # is 2 - 0 = 2
        power = last_idx - idx
        sec += t_num * 60 ** power
    return sec
    

if __name__ == "__main__":
    videos = {
        "Elite E1": {
            "id": "10df59c8bd9641b38010fead21b8eb58",
            "file": "elite_s1_ep1.xlsx",
            "lang": "es"
        },
        "HTSDO S3E1": {
            "id": "?",
            "file": "s3_ep1_how_to_sell_drogs_online.xlsx",
            "lang": "de"
        },
        "Paquita Salas E1": {
            "id": "8ede647f6f0b4201af5f3ca6e0463edc",
            "file": "paquita_salas_e1.xlsx",
            "lang": "es"
        }
    }
    parser = argparse.ArgumentParser()
    parser.add_argument('-db', '--database')
    parser.add_argument('-l', '--lang')
    parser.add_argument('-s', '--start_time', nargs='?', const=0, type=int)
    parser.add_argument('-m', '--max', nargs='?', const=None, type=int)
    args = parser.parse_args()
    video_name = "Paquita Salas E1"

    video = videos[video_name]
    video_lang = video["lang"]
    if args.lang != video_lang:
        print(f"mismatch between video language ({video_lang}) and selected language ({args.lang}). please select correct language.")
        exit(0)
    
    # TODO: parse a different way, completely mapping to enum type and checking for all
    lang = Lang.SPANISH if args.lang == 'es' else Lang.GERMAN
    max_entries = args.max
    start_time = args.start_time
    db_type = Db.PROD if args.database == 'prod' else Db.DEV

    file_path = "./data/" + video["file"]
    df = read_raw_data(file_path)
    # TODO: create function that gets this id by looking up the name of the video via API
    video_id = video["id"]
    database_id = db_type.value
    config = f"""
        'db': {db_type}
        'video': {video_name}
        'path': {file_path}
        'lang': {lang}
        'max_entries': {max_entries}
        'start_time': {start_time}
    """
    config_okay = input(f"is the following config ok? (y/n)\n{config}\n")
    if config_okay.lower() != "y":
        print("k, exiting.")
        exit(0)
    else:
        print("okay, inserting data into DB!")

    n_entries = len(df)
    curr_entries = 0
    for idx, row in df.iterrows():
        if max_entries and curr_entries >= max_entries:
            break
        target_text = row["Subtitle"]
        source_text = row.get("Machine Translation") or row.get("Translation")
        time_str = row["Time"]
        time_sec = get_second(time_str)
        props = {
            'target_text': target_text,
            'source_text': source_text,
            'video_id': video_id,
            'seconds': time_sec,
            'time_str': time_str
        }
        if not start_time:
            insert_translation(database_id, lang, props)
            curr_entries += 1
        # TODO: just start the iteration at the start time instead of checking for it
        elif time_sec >= start_time:
            insert_translation(database_id, lang, props)
            curr_entries += 1
            