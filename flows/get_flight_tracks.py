import logging
from datetime import datetime

from src.flightaware import parse_flight_track, request_flight_track
from src.utils import (
    partition_df_by_column,
    query_bq_for_df,
    save_dateformatted_data_to_storage,
)

logger = logging.getLogger()


def get_flight_tracks() -> None:
    """
    This function get flight tracks and save them to bucket
    """
    date = datetime.utcnow().strftime("%Y-%m-%d")

    query = f"""
        SELECT distinct fa_flight_id 
        FROM `streaming-flights-brisbane.brisbaneairport.flights` 
        WHERE status_type = "scheduled_arrivals"
        AND DATE(TIMESTAMP_TRUNC(date, DAY)) = '{date}'
    """

    print(query)

    flights = query_bq_for_df(query=query)

    flight_ids = flights["fa_flight_id"].tolist()

    if not flight_ids:
        print("No valid flight ids")
        return None

    flight_paths = [request_flight_track(f_id) for f_id in flight_ids]

    if not flight_paths:
        logger.warning(f"WARNING - No flight tracks found at {datetime.utcnow()})")
        return None

    parsed = parse_flight_track(flight_tracks=flight_paths)

    dfs = partition_df_by_column(parsed, columns=["date", "fa_flight_id"])

    for df in dfs:
        save_dateformatted_data_to_storage(
            df=df,
            bucket="brisbane-airport",
            prefix="flight_tracks",
            suffix="fa_flight_id",
        )


if __name__ == "__main__":
    get_flight_tracks()
    # print(request_flight_track(flight_id="QLK2422-1690632759-airline-358p"))
