#!/bin/bash

# Get current date and time
current_year=$(date +%Y)
current_month=$(date +%m)
current_day=$(date +%d)

# Construct the file path
file_path="gs://brisbane-airport/traffic/year=$current_year/month=$current_month/day=$current_day/*.parquet"

# Load data into BigQuery
bq load --source_format=PARQUET brisbaneairport.flights $file_path
