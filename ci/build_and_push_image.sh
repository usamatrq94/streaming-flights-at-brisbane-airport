REGION="australia-southeast1"
PROJECT_ID="streaming-flights-brisbane"
REPOSITORY_NAME="brisbane-airport-docker"

gcloud auth configure-docker $REGION-docker.pkg.dev --quiet

docker build -f orchestration/Dockerfile -t $REGION-docker.pkg.dev/$PROJECT_ID/$REPOSITORY_NAME/execution:latest .

docker push $REGION-docker.pkg.dev/$PROJECT_ID/$REPOSITORY_NAME/execution:latest


