import os

from prefect.filesystems import GCS
from prefect_gcp import GcpCredentials
from prefect_gcp.cloud_run import CloudRunJob
from prefect_gcp.cloud_storage import GcsBucket

with open("orchestration/prefect-service-account.json", "r") as file:
    service_account = file.read()

# block = GCS(
#     bucket_path="prefect-deployments-dev/streaming-flights-at-brisbane-airport",
#     service_account_info=service_account,
#     project="streaming-flights-brisbane",
# )

credentials = GcpCredentials.load("prefect-gcp-service-role")

block = GcsBucket(
    bucket="prefect-deployments-dev",
    gcp_credentials=credentials,
    bucket_folder="streaming-flights-at-brisbane-airport",
)

block.save("streaming-flights-at-brisbane-airport", overwrite=True)


block = CloudRunJob(
    credentials=credentials,
    project="streaming-flights-brisbane",
    image="australia-southeast1-docker.pkg.dev/streaming-flights-brisbane/brisbane-airport-docker/execution",
    region="australia-southeast1",
)

block.save("streaming-flights-at-brisbane-airport", overwrite=True)
