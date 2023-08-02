#!/bin/bash

# Reading YAML file
file="orchestration/deployments.yaml"
repo_name="streaming-flights-at-brisbane-airport"

# Counting the number of flows
num_flows=$(yq '.flows | length' $file)

deployment_files=()
# # Looping over each flow
for ((flow_index=0; flow_index<$num_flows; flow_index++)); do

    flow_name=$(yq ".flows[$flow_index].name" $file)
    flow_path=$(yq ".flows[$flow_index].flow_path" $file)
  
    echo "-> Deploying Flow :: $flow_path:$flow_name"
  
    num_deployments=$(yq ".flows[$flow_index].deployments | length" $file)

    for ((dep_index=0; dep_index<$num_deployments; dep_index++)); do
        dep_name=$(yq ".flows[$flow_index].deployments[$dep_index].name" $file)
        cron=$(yq ".flows[$flow_index].deployments[$dep_index].cron" $file)

        output_dep="ci/prefect_deployments/$flow_name"-"$dep_name".yaml
        
        prefect deployment build "$flow_path":"$flow_name" \
            --name "$dep_name" \
            --tag "$repo_name" \
            --output "$output_dep" \
            --storage-block "gcs-bucket/$repo_name" \
            --infra-block "cloud-run-job/$repo_name" \
            --cron "$cron"\
            --skip-upload
        
        echo "--> Deployment :: $dep_name | $output_dep"
        
        prefect deployment apply $output_dep --upload
        
    done
done

