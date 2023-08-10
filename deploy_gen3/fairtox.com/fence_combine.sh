python3 fence_email.py
tail -n +3 ./value_yaml/user.yaml > ./value_yaml/user2.yaml
rm ./value_yaml/user.yaml
cat ./value_yaml/fence-config.yaml <(cat ./value_yaml/user2.yaml) > ./value_yaml/fence-temp.yaml
rm ./value_yaml/user2.yaml
