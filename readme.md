install terraform to jenkins
gcloud compute ssh --zone "australia-southeast1-c" "jenkins-ci-vm" --project "streaming-flights-brisbane"

sudo apt-get update
sudo apt-get install unzip

wget https://releases.hashicorp.com/terraform/1.0.5/terraform_1.0.5_linux_amd64.zip

unzip terraform_1.0.5_linux_amd64.zip
sudo mv terraform /usr/local/bin/

terraform version
