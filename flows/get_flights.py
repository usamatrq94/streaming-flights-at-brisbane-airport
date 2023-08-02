from prefect import flow

from src.flightaware import parse_brisbane_flights, request_brisbane_flights_on_date
from src.utils import (
    partition_df_by_column,
    save_dateformatted_data_to_storage,
    update_bq_table,
)


@flow
def get_flights():
    response = request_brisbane_flights_on_date()
    parsed = parse_brisbane_flights(response=response)

    dfs = partition_df_by_column(df=parsed, columns=["date"])

    for df in dfs:
        save_dateformatted_data_to_storage(
            df=df, bucket="brisbane-airport", prefix="traffic"
        )

    uri = "gs://brisbane-airport/traffic/*.parquet"

    update_bq_table(
        table_id="streaming-flights-brisbane.brisbaneairport.flights", uri=uri
    )


if __name__ == "__main__":
    get_flights()
