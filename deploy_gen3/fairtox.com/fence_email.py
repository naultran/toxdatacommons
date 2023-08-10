import yaml
import json

with open('./value_yaml/user_template.yaml', 'r') as yaml_file:
    users = yaml.safe_load(yaml_file)

with open('./value_yaml/emails.json', 'r') as file:
    json_data = file.read()
email_data = json.loads(json_data)

group_names = list(email_data.keys())
for group_name in group_names:
    for group in users["authz"]["groups"]:
        if group['name'] == group_name:
            group['users'] = list(email_data[group_name].keys())
for i in email_data.keys():
    users["users"].update(email_data[i])

output ={}
output['fence'] = {}
output['fence']['USER_YAML'] = users
with open("./value_yaml/user.yaml", 'w') as f:
    yaml.dump(dict(output), f, sort_keys=False, default_flow_style=False)
