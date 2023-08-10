#!/bin/bash
./fence_combine.sh
# Read secrets and set environment variables

while IFS= read -r line; do
    export "$line"
done < ./value_yaml/secret.yaml

# Perform environment variable substitution and generate temp.yaml
envsubst < ./value_yaml/fence-temp.yaml > ./value_yaml/temp.yaml
rm ./value_yaml/fence-temp.yaml
# Check if the release exists (gen3v1)
if helm status gen3v1 >/dev/null 2>&1; then
    # Upgrade the existing release
    helm upgrade gen3v1 gen3/gen3 -f ./value_yaml/temp.yaml -f ./value_yaml/global_portal_cert_workspace-config.yaml -f ./value_yaml/guppy_override.yaml -f ./value_yaml/indexd_config.yaml
else
    # Install the release if it doesn't exist
    helm install gen3v1 gen3/gen3 -f ./value_yaml/temp.yaml -f ./value_yaml/global_portal_cert_workspace-config.yaml -f ./value_yaml/guppy_override.yaml -f ./value_yaml/indexd_config.yaml
fi

# Clean up the temp.yaml file
rm ./value_yaml/temp.yaml
