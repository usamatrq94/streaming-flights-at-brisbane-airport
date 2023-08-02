import json
import logging

import pandas as pd
from google.cloud import bigquery, secretmanager
from prefect import task

logger = logging.getLogger()

# Test changes for jenkins


def get_secrets(
    secret_id: str = None,
    version: str = "latest",
):
    """
    This function is currently defaulting to streaming-flights-brisbane project id
    """
    client = secretmanager.SecretManagerServiceClient()

    name = f"projects/927398552309/secrets/{secret_id}/versions/{version}"

    response = client.access_secret_version(name=name)

    return response.payload.data.decode("UTF-8")


@task
def save_dateformatted_data_to_storage(
    df: pd.DataFrame, bucket: str, prefix: str, suffix: str = None
) -> None:
    """
    Saving parquet file to GCP storage
    """
    if df.empty:
        logger.warning("RECEIVED: Empty df")
        return None

    date = df["date"].unique()[0]
    suffix = df[suffix].unique()[0] if suffix else f"{date:%d}"
    partition = f"year={date:%Y}/month={date:%m}/day={date:%d}/{suffix}.parquet"
    path = f"gs://{bucket}/{prefix}/{partition}"

    df.to_parquet(path=path, engine="pyarrow")
    logger.info(f"SUCCESSFUL : Placed data to bucket -> {path}")


def generate_schema(df: pd.DataFrame, output_path: str = None) -> None:
    """
    Function to generate schema
    """
    output_path = output_path or "schema.json"
    schema = [
        {
            "name": col,
            "type": dtype_to_bqtype(df[col].dtype),
            "mode": "REQUIRED" if df[col].isnull().sum() == 0 else "NULLABLE",
            "description": "",
        }
        for col in df.columns
    ]

    with open(output_path, "w") as w:
        json.dump(schema, w)

    logger.info(f"SUCCESSFUL : Saved schema to -> {output_path}")


def dtype_to_bqtype(dtype):
    """
    Function to configure schema dtype
    """
    if pd.api.types.is_integer_dtype(dtype):
        return "INTEGER"
    elif pd.api.types.is_float_dtype(dtype):
        return "FLOAT"
    elif pd.api.types.is_string_dtype(dtype):
        return "STRING"
    elif pd.api.types.is_datetime64_any_dtype(dtype):
        return "TIMESTAMP"
    elif pd.api.types.is_bool_dtype(dtype):
        return "BOOLEAN"
    # Add more conditions here if necessary
    else:
        raise ValueError(f"Data type {dtype} is not currently supported")


@task
def query_bq_for_df(query: str) -> pd.DataFrame:
    """Function return query results as dataframe"""
    client = bigquery.Client()
    job = client.query(query)
    return job.to_dataframe()


@task
def partition_df_by_column(
    df: pd.DataFrame, columns: list = ["date"]
) -> list[pd.DataFrame]:
    """
    Function to partiton dataframe by column
    """
    grouped = df.groupby(columns)
    return [grp for _, grp in grouped]


def update_bq_table(table_id: str, uri: str) -> None:
    """
    Function to create and update Big Query Table
    """
    client = bigquery.Client()

    job_config = bigquery.LoadJobConfig(
        source_format=bigquery.SourceFormat.PARQUET,
    )

    load_job = client.load_table_from_uri(uri, table_id, job_config=job_config)

    load_job.result()
