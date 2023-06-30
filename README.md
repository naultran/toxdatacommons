# MSU SRC Tox Data Commons
Editor: Rance Nault & Shuangyu Zhao
## 1. Deployment of developer (local) instance of Gen3 using  Helm

For more instruction see [this](https://github.com/uc-cdis/gen3-helm/blob/master/docs/gen3_developer_environments.md#running-gen3-on-a-laptop-for-devs) and [this](https://github.com/uc-cdis/gen3-helm/blob/master/docs/gen3_developer_environments.md#local-dev-linux-ubuntu--rancher-desktop-problems) or the [Gen3 helm website](https://helm.gen3.org).

_The following are notes from our own deployment on an Ubuntu system._

---
### _Notes:_
- Gen3-helm needs at least 30GB of hard drive space or pods will fail and Kubernetes will crash.
- The first deployment can take some time to download all the images. For us it took ~40 minutes to start seeing everything run. If the images are already downloaded it can take ~15 mins.
- Our original deployment was not working with localhost. It either didn't load when using https protocol or would only show the page name using http (after forwarding port from rancher-desktop). We had to run the following.
```
sudo sysctl net.ipv4.ip_unprivileged_port_start
sudo sysctl net.ipv4.ip_unprivileged_port_start=80
```
- Elastic search threw the following error ```max virtual memory areas vm.max_map_count [65530] is too low, increase to at least [262144]```. The following commands changes the vm.max_map_count value for all of rancher-desktops images.
```
rdctl shell # enters the rancher-desktop vm
sudo sysctl -w vm.max_map_count=262144 # changes the value
sysctl vm.max_map_count # verifies that it has changed
```
> To make this change permanent use ```sudo nano /etc/sysctl.conf``` and add ``` vm.max_map_count=262144``` following line at the end of the document.


#### Useful commands
```
kubectl get pods # list running pods
kubectl logs {pod_name} # get logs for a pod
kubectl describe pods {pod_name} # Explains why it might be stuck in pending
helm uninstall {chart_name}
kubectl edit ingress revproxy
kubectl edit deployment -n kube-system traefik
kubectl rollout restart deployment traefik -n kube-system
```

### Creating a `local` certificate using route 53
#### Link of DNS
To be able to create a certificate it is necessary that the deployment be public facing. This can be done by adding to the `/etc/hosts` file as below:
```
<machine ip-address> fairtox.com
```
_fairtox.com was purchased through route53_

#### Create certificate
A certificate can be created using [certbot](https://certbot.eff.org/). It will ask you to create a DNS TXT record
```
sudo certbot certonly --manual --preferred-challenges=dns -d fairtox.com
```
- Log in to the AWS Management Console and navigate to the Route 53 service.
- Select your hosted zone for the fairtox.com domain.
- Click on "Create Record Set" to add a new DNS record.
- In the "Name" field, enter _acme-challenge
- Set the "Type" to "TXT".
- In the "Value" field, enter the verification value provided by Certbot.
- __WAIT UNTIL IT IS UPDATED (1 - 5 min)__
- Click on "Create" or "Save" to add the DNS TXT record.

#### Create secret
```
kubectl create secret tls <secret-name> --cert=<path-to-certificate.pem> --key=<path-to-key.pem>
```

#### Update ingress
```
kubectl edit ingress <ingress-name>

  tls:
  - hosts:
    - fairtox.com
    secretName: <secret-name>
```
#### override the revproxy
So you don't need to update ingress every time you reinstall the gen3
```
revproxy:
  ingress:
    enabled: true
    annotations:
    hosts:
    - host: <hostname>
      paths:
        - path: /
          pathType: Prefix
    tls:
      - secretName: <secret-name>
        hosts:
          - <hostname>

```
You can store this part in your values.yaml, and push it to gen3.

### Override the default values.yaml files
This part can customize the website.
* read the default values.yaml file [link for the all pods](https://github.com/uc-cdis/gen3-helm/tree/master/helm).
* edit your own values.yaml.

For example,
1. You want to customize the fence [link for the fence's values.yaml](https://github.com/uc-cdis/gen3-helm/blob/master/helm/fence/values.yaml). And what you want to change is the [USER_YAML](https://github.com/uc-cdis/gen3-helm/blob/master/helm/fence/values.yaml#LL479C2-L479C2) part. In the values.yaml which will be pushed to gen3/gen3, you should add:
```{yaml}
fence: # port name you want to override
# the following is what you want to change
  USER_YAML: |
      ....things you want to customize...
```
2. If you want to customize the [portal](https://github.com/uc-cdis/gen3-helm/blob/master/helm/portal/values.yaml) to read the image we prebuild([instruction to prebuild the portal](https://github.com/uc-cdis/gen3-helm/blob/4415e61a992e9c9113bc7f1531ec8387d3886404/docs/portal/prebuild-portal.md)). And [image](https://github.com/uc-cdis/gen3-helm/blob/master/helm/portal/values.yaml#L65) is the part we want to change.
```{yaml}
portal: # port name you want to override
# the following is what you want to change
  image:
    repository: <repository name in rancher destop>
    pullPolicy: IfNotPresent
    tag: <self defined tag which can be checked on rancher desktop>

```


### prebuild portal
The official instructions of prebuilding portal are shown in this [website](https://github.com/uc-cdis/gen3-helm/blob/4415e61a992e9c9113bc7f1531ec8387d3886404/docs/portal/prebuild-portal.md). In this part, Some tips will be provided.

1. To render the portal image, you should git pull the repository of gen3-helm first. And then locate to /gen3-helm/docs/portal/. ```Dockerfile``` is used to generate the portal image, and this location is where the command ```docker build -t image_name:image_tag .``` runs. In the configuration folder, a new sub-folder should be created to store the customized gitops.json, gitops.css and logo, whose name is always the portal's host name. Once you settle the name of folder, you should update the ```Dockerfile``` under the following instruction.
```
ARG CODE_VERSION=master
FROM node:16 as builder

ARG PORTAL_HOSTNAME=<the real host name which is consistent with the folder name settled.>
```

2. For the folder storing gitops.json, gitops.css and logo, the additional unmentioned folders or files should not be added, which means this folder only can store ```gitops.json```, ```gitops.css```, ```gitops-logo.png```, ```gitops-createdby.png``` and ```gitops-favicon.ico```.

3. To customize the color of website, you should edit ```gitops.css```. I personally recommend you to open the developer view to make sure the objects' names. To customize the content of website, you could edit ```gitops.json```. By the way, you can find a wealth of examples [here](https://github.com/uc-cdis/cdis-manifest/tree/a71ecb66cd5cc09dc8c0c9dc34a1eb406255a9b0). 

4. If you want to change the color of icons, you could use the filter to convert color.
```
.login-page__side-box {
  filter: hue-rotate(292deg);
}

.index-button-bar__icon {
  filter: hue-rotate(292deg);
}

```
The rotation degree depends on target color and the original color. I highly recommend this [website](https://isotropic.co/tool/hex-color-to-css-filter/) to calculate the rotation degree.

5. Because it is impossible to settle the website in one trail, so the disk possibly is filled with sleeping containers, unused images and volumes.
```
docker system prune --all --volumes  // remove all unused images, containers and volumes
docker container prune  // remove all stopped containers
docker image prune // delete all unused images
```

6. Every time you update the portal, the search engine possibly remember the older version, therefore, the website's appearance seems to be the same as before. You could open a private window to check it, or simply clean the history.


### building model for metadata(template)
.yaml file
normal node
```
$schema: "http://json-schema.org/draft-04/schema#"

id: "node_name"
title: node_name
type: object
category: category of node
program: '*'
project: '*'
description: >
  description
additionalProperties: false
submittable: true
validators: null

systemProperties: 
  - id
  - project_id
  - state
  - created_datetime
  - updated_datetime

required:
  - type
  - submitter_id #
  - targets #external key pointing to the previous node
  ...

uniqueKeys:
  - [id]
  - [project_id, submitter_id]

links:
  - name: targets
    backref: node_names
    label: member_of
    target_type: target
    multiplicity: many_to_one/one_to_one....
    required: true


properties: 
  type:
    enum: ["node_name"]
  id:
    $ref: "_definitions.yaml#/UUID"
  submitter_id:
    type: string
  targets:
    $ref: "_definitions.yaml#/to_one" / "_definitions.yaml#/to_many" # depending on links' multiplicities
  ....
  state:
    $ref: "_definitions.yaml#/state"
  project_id:
    $ref: "_definitions.yaml#/project_id"
  created_datetime:
    $ref: "_definitions.yaml#/datetime"
  updated_datetime:
    $ref: "_definitions.yaml#/datetime"

```
node of data file which link to core_metadata_collection
```
$schema: "http://json-schema.org/draft-04/schema#"

id: "node_file"
title: node_file
type: object
category: data_file
program: '*'
project: '*'
description: >
  description.
additionalProperties: false
submittable: true
validators: null

systemProperties: 
  - id
  - project_id
  - state
  - created_datetime
  - updated_datetime
  - file_state
  - error_type

required:
  - type
  - submitter_id
  - targets
  ...

uniqueKeys:
  - [id]
  - [project_id, submitter_id]

links:
  - exclusive: false
    required: true
    subgroup:
    - name: targets
      backref: node_files
      label: member_of
      target_type: target
      multiplicity: one_to_one/one_to_many
      required: true
    - name: core_metadata_collections
      backref: node_files
      label: data_from
      target_type: core_metadata_collection
      multiplicity: many_to_many
      required: false
  
properties:
  $ref: "_definitions.yaml#/data_file_properties"
  type:
    enum: ["node_file"]
  targets:
    $ref: "_definitions.yaml#/to_one"/"_definitions.yaml#/to_many"
  ...
  state:
    $ref: "_definitions.yaml#/state"
  project_id:
    type: string
  created_datetime:
    $ref: "_definitions.yaml#/datetime"
  updated_datetime:
    $ref: "_definitions.yaml#/datetime"
  core_metadata_collections:
    $ref: "_definitions.yaml#/to_many"


```
## 2. Using gen3(uploading and extracting data) 
### code for upload metadata by gen3 API
prerequirement
```{python}
import pandas as pd
import numpy as np
import subprocess
import sys
import gen3
import json
from gen3.submission import Gen3Submission
from gen3.auth import Gen3Auth
from gen3.index import Gen3Index
from gen3.query import Gen3Query
from gen3.metadata import Gen3Metadata
from gen3.file import Gen3File
import os

# download and import some custom Python scripts from https://github.com/cgmeyer/gen3sdk-python
# os.system("wget https://raw.githubusercontent.com/cgmeyer/gen3sdk-python/master/expansion/expansion.py")
from expansion import Gen3Expansion

api = 'https://fairtox.com/'
cred = '/path/to/credential.json' # can be created under profile tab
auth = Gen3Auth(api, refresh_file=cred)
sub = Gen3Submission(api, auth)
query = Gen3Query(auth)
index = Gen3Index(auth)
file = Gen3File(auth)
metadata = Gen3Metadata(auth)
exp = Gen3Expansion(api,auth,sub)
```
Create program
```
prog = 'program_name'

prog_txt = """{
    "dbgap_accession_number": "%s",
    "type": "program",
    "name": "%s"
}""" % (prog,prog)

prog_json = json.loads(prog_txt)
data = sub.create_program(json=prog_json)
```
Create project
```
proj_txt = """{
    "availability_type": "Open",
    "code": "project_name",
    "dbgap_accession_number": "project_name",
    "type": "project",
    "contact_name": "test",
    "institution": "MSU",
    "description": "test",
    "email_address": "xxxxx@fdas.sdfs",
    "telephone_number": "ssd-asdf-asdf"
    }"""
proj_json = json.loads(proj_txt)
data = sub.create_project(program="program_name",json=proj_json) 
```
Upload a file
```
data = sub.submit_file(filename="path/to/file", project_id="program_name-project_name")
```
Upload a single record
```
import requests
COMMONS = "https://fairtox.com/"
API_KEY_FILEPATH = '/path/to/credential.json'

projectname = 'project_name'
programname = 'program_name'
api_url = "{}/api/v0/submission/{}/{}".format(COMMONS,programname,projectname)
jsondata = [ 
{
        "type": "type",
        "feature1": "value1",
        "feature2": "value2",
        "feature3": "value3",
        "external_link": [
            {
                "submitter_id": "xxxxxxssss"
            }
        ]
}]
print(jsondata)
authn = Gen3Auth(COMMONS, refresh_file=API_KEY_FILEPATH)
output = requests.put(api_url, auth=authn, json=jsondata)
output.json()
```
When you try to upload a file, the feedback shows: 'latin-1' codec can't encode character '\uxxx' in position xxx. You could use this code:
```
import requests
COMMONS = "https://fairtox.com/"
API_KEY_FILEPATH = '/path/to/credential.json'

projectname = 'project_name'
programname = 'program_name'
api_url = "{}/api/v0/submission/{}/{}".format(COMMONS,programname,projectname)
df = pd.read_table('/path/to/file')
col_name = df.columns.tolist()
# this is external link
col_name.remove("links.submitter_id")

for _, row in df.iterrows():
    jsondata = []
    # this is for the external link
    dic = {
        "links": [
            {
                "submitter_id": row["links.submitter_id"]
            }
        ]
    }

    for i in col_name:
        value = row[i]
        if isinstance(value, float) and (value == float('inf') or value == float('-inf') or pd.isna(value)):
            dic[i] = str(value)
        else:
            dic[i] = value

    jsondata.append(dic)
    print(jsondata)
    authn = Gen3Auth(COMMONS, refresh_file=API_KEY_FILEPATH)
    output = requests.put(api_url, auth=authn, json=jsondata)
    output.json()
```
When uploading file to node whose type is data file, we need to insert the md5sum and file size in the file sheet. You can use the following code to automatically insert them.
```
import pandas as pd
import hashlib
import os
def calculate_md5(file_path):
    """Calculate the MD5 checksum for a file."""
    md5_hash = hashlib.md5()
    with open(file_path, 'rb') as file:
        for chunk in iter(lambda: file.read(4096), b''):
            md5_hash.update(chunk)
    return md5_hash.hexdigest()

# Provide the file name list and DataFrame
df = pd.read_table("/path/to/file.tsv")
file_names = df["file_name"].to_list()

folder_path = '/path/to/folder/containing/the/files'

# Update the MD5 checksum for each file name in the DataFrame
for file_name in file_names:
    file_path = folder_path + file_name
    md5_sum = calculate_md5(file_path)
    file_size = os.path.getsize(file_path)
    df.loc[df['file_name'] == file_name, 'md5sum'] = md5_sum
    df.loc[df['file_name'] == file_name, 'file_size'] = file_size
df['file_size'] = df['file_size'].astype(int)
df.to_csv("/path/to/new/file.tsv", sep='\t', index=False)
```

### code for upload raw data file by gen3 client(terminal)
You can find the official instruction [here](https://gen3.org/resources/user/gen3-client/). 

### extract metadata
prerequisite
```
import os
import sys
import csv
import gen3
import json
import mwtab
import warnings
import pandas as pd
import matplotlib.pyplot as plt

from io import StringIO
from datetime import datetime
from collections import OrderedDict
from expansion import Gen3Expansion # os.system("wget https://raw.githubusercontent.com/cgmeyer/gen3sdk-python/master/expansion/expansion.py")

from gen3.auth import Gen3Auth
from gen3.index import Gen3Index
from gen3.query import Gen3Query

from gen3.submission import Gen3Submission

current_date = datetime.now().date()
formatted_date = current_date.strftime('%Y-%m-%d')

warnings.filterwarnings("ignore", category=UserWarning)

def process_node_data(node_name, data, key):
    node_df = pd.read_csv(StringIO(data), sep='\t', header=0)
    node_df[key] = node_df[key].str.split(',')
    node_df = node_df.explode(key)
    pattern = r'(^|\.)id($|\.)'
    drop_columns = [col for col in node_df.columns if pd.Series(col).str.contains(pattern).any()]
    node_df = node_df.drop(drop_columns, axis=1)
    node_df = node_df.reset_index(drop=True)
    return node_df

def get_unique_values(dataframe, column_name):
    unique_values = dataframe[column_name].unique()
    unique_string = ','.join(map(str, unique_values))
    return unique_string

def remove_newlines(obj):
    if isinstance(obj, dict):
        return {key: remove_newlines(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [remove_newlines(element) for element in obj]
    elif isinstance(obj, str):
        return obj.replace('\n', '').replace('\r', '')
    else:
        return obj

# Initiate instances of the Gen3 SDK Classes using credentials file for authentication.
# Change the directory path in "cred" to reflect the location of your credentials file.
api = "https://fairtox.com"
cred = "path/to/credentials.json"
auth = Gen3Auth(api, refresh_file=cred) # authentication class
sub = Gen3Submission(api, auth) # submission class
query = Gen3Query(auth) # query class
exp = Gen3Expansion(api,auth,sub) # class with some custom scripts

```

get all the projects' names you have access to: 
```
exp.get_project_ids()
```





#### Wait for changes to propagate
