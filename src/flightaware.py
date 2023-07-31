import time
from datetime import datetime

import pandas as pd
import requests
from pytz import timezone

from src.utils import get_secrets

flightaware_api_key = get_secrets(secret_id="flightaware-api-key")
flightaware_api_url = "https://aeroapi.flightaware.com/aeroapi/"


def request_brisbane_flights_on_date() -> dict:
    """
    THe functions gets all brisbane flights today
    """
    airport = "YBBN"  # brisbane airport icao

    date = datetime.utcnow().strftime("%Y-%m-%d")

    payload = {"max_pages": 2, "start": f"{date}T00:50:00Z", "end": f"{date}T23:59:59Z"}
    auth_header = {"x-apikey": flightaware_api_key}

    response = requests.get(
        flightaware_api_url + f"airports/{airport}/flights",
        params=payload,
        headers=auth_header,
        timeout=120,
    )

    if response.status_code == 200:
        response = response.json()
        response["date"] = date
        return response
    else:
        print(f"Error executing request :: {response.json()}")


def parse_brisbane_flights(response: dict) -> pd.DataFrame:
    """
    This function parses a json file as dataframe
    """
    dfs = [
        pd.json_normalize(response[status]).assign(status_type=status)
        for status in response.keys()
        if status
        in ["arrivals", "departures", "scheduled_arrivals", "scheduled_departures"]
    ]

    df = pd.concat(dfs)
    df.columns = [col.replace(".", "_") for col in df.columns]
    return df.assign(
        date=pd.to_datetime(response["date"], utc=True),
        scheduled_out=pd.to_datetime(df.scheduled_out, utc=True),
        estimated_out=pd.to_datetime(df.estimated_out, utc=True),
        scheduled_off=pd.to_datetime(df.scheduled_off, utc=True),
        scheduled_on=pd.to_datetime(df.scheduled_on, utc=True),
        estimated_on=pd.to_datetime(df.estimated_on, utc=True),
        scheduled_in=pd.to_datetime(df.scheduled_in, utc=True),
        estimated_in=pd.to_datetime(df.estimated_in, utc=True),
        scheduled_out_local=pd.to_datetime(df.scheduled_out, utc=True).dt.tz_convert(
            timezone("Australia/Brisbane")
        ),
        estimated_out_local=pd.to_datetime(df.estimated_out, utc=True).dt.tz_convert(
            timezone("Australia/Brisbane")
        ),
        scheduled_off_local=pd.to_datetime(df.scheduled_off, utc=True).dt.tz_convert(
            timezone("Australia/Brisbane")
        ),
        scheduled_on_local=pd.to_datetime(df.scheduled_on, utc=True).dt.tz_convert(
            timezone("Australia/Brisbane")
        ),
        estimated_on_local=pd.to_datetime(df.estimated_on, utc=True).dt.tz_convert(
            timezone("Australia/Brisbane")
        ),
        scheduled_in_local=pd.to_datetime(df.scheduled_in, utc=True).dt.tz_convert(
            timezone("Australia/Brisbane")
        ),
        estimated_in_local=pd.to_datetime(df.estimated_in, utc=True).dt.tz_convert(
            timezone("Australia/Brisbane")
        ),
    )


def request_flight_track(flight_id: str) -> dict:
    """
    The function gets all details of a flight
    """
    auth_header = {"x-apikey": flightaware_api_key}

    print(f"Searching -> {flight_id}")
    time.sleep(5)

    response = requests.get(
        flightaware_api_url + f"flights/{flight_id}/track",
        headers=auth_header,
        timeout=120,
    )

    if response.status_code == 200:
        response = response.json()
        response["flight_id"] = flight_id
        return response
    else:
        print(f"Error executing request :: {response.json()}")
        return {}


def parse_flight_track(flight_tracks: dict) -> pd.DataFrame:
    """
    The function parses track tracks from json to dataframe
    """
    df = pd.json_normalize(flight_tracks, record_path="positions", meta=["flight_id"])
    return df.assign(
        fa_flight_id=df.flight_id,
        timestamp=pd.to_datetime(df.timestamp, utc=True),
        timestamp_local=pd.to_datetime(df.timestamp, utc=True).dt.tz_convert(
            timezone("Australia/Brisbane")
        ),
        date=pd.to_datetime(df.timestamp, utc=True).dt.date,
    ).drop(columns=["flight_id"])
