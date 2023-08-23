# Deployment of a local Gen3-helm instance

Editor: Shuangyu Zhao, Michigan State University

<p align="center">  <img src="https://img.shields.io/badge/status-work%20in%20progress-yellow" alt="Work in Progress">  <br>  <strong>🚧 This repository is a work in progress 🚧</strong>  <br> Please check in regularly for updates .  If you have any questions feel free to contact us using <i>issues</i>.</p>

----
This README is an overview on how to set up a local [Gen3](gen3.org) using the [Helm deployment workflow](https://helm.gen3.org/). 

### Table of Contents
1. [Before you start!](#before-you-start)<br>
	a. [Installing rancher-desktop and Gen3 helm chart](#setup)<br>
	b. [downloading this repository](#pull)<br>
2. [Building your data model](#data-modeling)<br>
3.  [Deploying a local Gen3 instance](#deploy)<br>
	a. [Setting up credentials](#credentials)<br>
	b. [Setting up permissions](#user.yaml)<br>
4. [Creating a certificate](#certificate)<br>
5. [Prebuilding a portal](#portal)<br>
6. [Data upload (AWS S3)](#s3)<br>
7. [Deploy using custom scripts](#deploy-sh)<br>
8. [Set up exploration tab](#explore)<br>
9. [Set up indexd](#indexd)<br>

---
<a id='before-you-start'></a>
## Before you start!

<a id='setup'></a>
### Installing Rancher Desktop and Gen3
Rancher desktop and the Gen3 helm charts are installed without modification as described [here](https://github.com/uc-cdis/gen3-helm/blob/master/docs/gen3_developer_environments.md#local-dev-linux-ubuntu--rancher-desktop-problems).

For a video walkthrough on getting started with Gen3 helm charts see the [Gen3 community events and webinars](https://gen3.org/community/events/). 

<a id='pull'></a>
### Download custom files (before you start)
To follow the instructions below you will need to do the following:
* Pull this deploy_gen3 repository
* Get the python script at toxdatacommons/custom_configs/schema_compile.py
* See the custom portal build folder at gen3-helm/docs/portal [link](https://github.com/uc-cdis/gen3-helm/tree/master/docs/portal)

<a id='data-modeling'></a>
## Building the data model

The ToxDataCommons team is developing a workflow for building the Gen3 data model following community developed Reporting Standards. See the following links from the University of [Chicago Center for Translational Data Science](https://github.com/uc-cdis) and [ToxRSCat](https://github.com/naultran/ToxRSCat/tree/main/templates#TDC) for more details. Below is an overview for reference.

* Creating a folder which stores all nodes' yaml files (Note: ```_definitions.yaml```, ```_settings.yaml```, ```_terms.yaml```, ```program.yaml```, ```project.yaml```, ```core_metadata_collection.yaml``` are required).

* Writing the nodes' file
normal nodes
```yaml
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
nodes of data file 
```yaml
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
* run the schema_compile.py (replace some values in it first)
```python
from dictionaryutils import dump_schemas_from_dir
import json

#import dictionaryutils 
schema = dump_schemas_from_dir(directory="xxx/xxx")   # path to the folder which stores all the nodes' files
schema["_settings.yaml"]["_dict_version"] = "0.1"    # replae the "0.1" to the dictionary version you want

with open('.xxxx/schema.json', 'w') as json_file:  # path to where you want to store the schema.json
    json.dump(schema, json_file)

```
Note: The schema.json should be backup in a PUBLIC online repository. 
* repace the value in ```global_portal_cert_workspace-config.yaml```
```yaml
global:
  dev: true
  hostname: fairtox.com 
  dictionaryUrl: "https://raw.githubusercontent.com/naultran/toxdatacommons/main/custom_configs/schema.json" # the links of schema.json(raw file )
  tierAccessLevel: "libre"
  tierAccessLimit: '"1000"'
```

<a id='deploy'></a>
## Deploying your local Gen3 instance

<a id='credentials'></a>
### 1. Setting up credentials 
> This section relates to passwords, usernames, and AWS access information. Be very careful not to share sensitive information!

Update the information in [`secret.yaml`](https://github.com/naultran/toxdatacommons/blob/main/deploy_gen3/fairtox.com/value_yaml/secret.yaml):
```
google_client_id="xxxx"
google_client_secret="xxx"
aws_access_key_id='xxx'
aws_secret_access_key='xxx'
```
See [this](https://github.com/uc-cdis/compose-services/blob/master/docs/setup.md#setting-up-google-oauth-client-id-for-fence) for more information about setting up the google authentication and [this](aws.amazon.com) for setting up AWS access information.

```google_client_id``` and ```google_client_secret``` enable the use of google linked accounts to log in; ```aws_access_key_id``` and ```aws_secret_access_key``` are used to enable upload of files to S3 buckets.

<a id='user.yaml'></a>
### 2. Setting user permissions (_user.yaml_)

We have separated the users from the typical user.yaml file to make it easier to add/revise new users and their permissions. To use this follow the standard `user.yaml` syntax as shown below. For more details on the user.yaml file see [here](https://github.com/uc-cdis/gen3-helm/blob/master/docs/CONFIGURATION.md#fence). 

#### Customize user_template.yaml
[`user_template.yaml`](https://github.com/naultran/toxdatacommons/blob/main/deploy_gen3/fairtox.com/value_yaml/user_template.yaml)
```yaml
groups: 
  # can CRUD programs and projects and upload data files
  - name: MSUSRC_member
    policies:
    - data_upload
    - all_programs_reader
    users: {}
  
  - name: MSUSRC_admin
    policies:
    - services.sheepdog-admin
    - data_upload
    - all_programs_submitter
    - workspace
    - indexd_admin
    users: {}
...
policies:
...
- id: all_programs_reader
    role_ids:
    - reader
    - storage_reader
    resource_paths:
    - /programs
  - id: all_programs_submitter
    role_ids:
    - reader
    - creator
    - updater
    - deleter
    - storage_reader
    - storage_writer
    resource_paths:
    - /programs
  - id: PROJECT1_submitter
    role_ids:
    - reader
    - creator
    - updater
    - deleter
    - storage_reader
    - storage_writer
    resource_paths:
    - /programs/MSUSRC/projects/PROJECT1
  - id: PROJECT2_submitter
    role_ids:
    - reader
    - creator
    - updater
    - deleter
    - storage_reader
    - storage_writer
    resource_paths:
    - /programs/MSUSRC/projects/PROJECT2
  - id: PROJECT3_submitter
    role_ids:
    - reader
    - creator
    - updater
    - deleter
    - storage_reader
    - storage_writer
    resource_paths:
    - /programs/MSUSRC/projects/PROJECT3
  - id: PROJECT4_submitter
    role_ids:
    - reader
    - creator
    - updater
    - deleter
    - storage_reader
    - storage_writer
    resource_paths:
    - /programs/MSUSRC/projects/PROJECT4
  - id: PROJECT5_submitter
    role_ids:
    - reader
    - creator
    - updater
    - deleter
    - storage_reader
    - storage_writer
    resource_paths:
    - /programs/MSUSRC/projects/PROJECT5
  - id: PROJECT6_submitter
    role_ids:
    - reader
    - creator
    - updater
    - deleter
    - storage_reader
    - storage_writer
    resource_paths:
    - /programs/MSUSRC/projects/PROJECT6
  - id: DMAC_submitter
    role_ids:
    - reader
    - creator
    - updater
    - deleter
    - storage_reader
    - storage_writer
    resource_paths:
    - /programs/MSUSRC/projects/DMAC
  - id: RETCC_submitter
    role_ids:
    - reader
    - creator
    - updater
    - deleter
    - storage_reader
    - storage_writer
    resource_paths:
    - /programs/MSUSRC/projects/RETCC
  - id: CEC_submitter
    role_ids:
    - reader
    - creator
    - updater
    - deleter
    - storage_reader
    - storage_writer
    resource_paths:
    - /programs/MSUSRC/projects/CEC
  - id: CMC_submitter
    role_ids:
    - reader
    - creator
    - updater
    - deleter
    - storage_reader
    - storage_writer
    resource_paths:
    - /programs/MSUSRC/projects/CMC    

resources:
...
- name: programs
    subresources:
    - name: MSUSRC
      subresources:
      - name: projects
        subresources:
        - name: PROJECT1
        - name: PROJECT2
        - name: PROJECT3
        - name: PROJECT4
        - name: PROJECT5
        - name: PROJECT6
        - name: DMAC
        - name: RETCC
        - name: CEC
        - name: CMC    
    - name: MyFirstProgram
      subresources:
      - name: projects
        subresources:
        - name: MyFirstProject
...
```
#### Customize emails.json
[`emails.json`](https://github.com/naultran/toxdatacommons/blob/main/deploy_gen3/fairtox.com/value_yaml/emails.json)
```json
// customize it
{
    "MSUSRC_admin": {
        "user1@sss.sss": {
            "tags":{
                "name": "user1",
                "email": "user1@sss.sss"
            }
        }
    },
    "MSUSRC_member": {
        "user2@sss.sss": {
            "tags":{
                "name": "user2",
                "email": "user2@sss.sss"
            }
        }
    }
}
```

<a id='certificate'></a>
### 3. Creating a certificate (AWS Route53)
You can create a certificate to associate with your local machine as described [here](https://github.com/naultran/toxdatacommons/blob/main/README.md#creating-a-local-certificate-using-route-53). Once the certificate has been created you will want to make sure that the rancher-desktop ingress associated that certificate with your Gen3 helm deployment. 

 #### Updating global_portal_cert_workspace-config
[`global_portal_cert_workspace-config.yaml`](https://github.com/naultran/toxdatacommons/blob/main/deploy_gen3/fairtox.com/value_yaml/global_portal_cert_workspace-config.yaml)
```yaml
global:
  dev: true
  hostname: fairtox.com  # your host name
  dictionaryUrl: "https://raw.githubusercontent.com/naultran/toxdatacommons/main/custom_configs/schema.json" 
  tierAccessLevel: "libre"
  tierAccessLimit: '"1000"'

...

revproxy:
  ingress:
    
    enabled: true
    
    annotations:
    hosts:
    
    - host: fairtox.com  # host name
      paths:
        - path: /
          pathType: Prefix
    tls:
      
      - secretName: fairtox-cert # secret name 
        hosts:

          - fairtox.com  # host name
...
```

<a id='portal'></a>
### 4. Prebuilding your portal
In our experience, `portal` is often the slowest piece when deploying your Gen3-helm instance. To address this you can prebuild the portal as outlined [here](https://github.com/uc-cdis/gen3-helm/blob/master/docs/CONFIGURATION.md#portal). Using this deployment mechanism change the following in [`global_portal_cert_workspace-config.yaml`](https://github.com/naultran/toxdatacommons/blob/main/deploy_gen3/fairtox.com/value_yaml/global_portal_cert_workspace-config.yaml).

#### Updating the Gitops.json file
Eventually you may want to edit the portal to fit your own data model. [See here for instruction on editing your `Gitops.json` file](https://github.com/uc-cdis/data-portal/blob/258781b73f1444d9db0b97f5aad4f4fd71f7efda/docs/portal_config.md)
```yaml
...
portal:
  gitops:  
    json|
     ...... # the [gitops.json](https://github.com/uc-cdis/gen3-helm/blob/master/helm/portal/values.yaml#L202-L461)  
...
```
> This part can be deleted when using the default portal for testing.

#### Build the portal image 
> __Note: When you prebuilding the portal, your gen3 should be running at the same time.__

* Pull the portal folder [here](google.com) and then enter this folder.
* Go to the `configuration` folder and create a new one named by your host name (_e.g._, fairtox.com).
* In this folder, store `gitops.json`, `gitops.css`. For more details on these files see [here](https://github.com/uc-cdis/data-portal/blob/258781b73f1444d9db0b97f5aad4f4fd71f7efda/docs/portal_config.md))
* Revise the following lines in the `Dockerfile`:
```shell
ARG CODE_VERSION=master
FROM node:16 as builder

ARG PORTAL_HOSTNAME  # ARG PORTAL_HOSTNAME=<the real host name which is consistent with the folder name settled.>

ENV APP gitops
ENV BASENAME /
...
# if you want to set ```resources``` in portal, I recommend you pulling the repository which store the html files and png files
RUN git clone https://xxxx.xxx/xxxx
...
RUN COMMIT=`git rev-parse HEAD` && echo "export const portalCommit = \"${COMMIT}\";" >src/versions.js \
    && VERSION=`git describe --always --tags` && echo "export const portalVersion =\"${VERSION}\";" >>src/versions.js

# replace above code to be the following one
RUN COMMIT=`git rev-parse HEAD` && echo "export const portalCommit = \"${COMMIT}\";" >src/versions.js \
  && echo "export const portalVersion ='2023.08';" >>src/versions.js 
 # replace '2023.08' to be the portal version you want
...

COPY --from=builder /data-portal/src/css/ /usr/share/nginx/html/src/css/
# if you want to set ```resources``` in portal
COPY --from=builder /data-portal/<repository_name_you_pulling>/ /usr/share/nginx/html/<repository_name_you_pulling>/
COPY overrides/dockerStart.sh dockerStart.sh
CMD bash ./dockerStart.sh
```
* Follow the [code here](https://github.com/uc-cdis/gen3-helm/blob/master/docs/portal/prebuild-portal.md) to build a new portal image, and replace the portal part to be the real values.
[`global_portal_cert_workspace-config.yaml`](https://github.com/naultran/toxdatacommons/blob/main/deploy_gen3/fairtox.com/value_yaml/global_portal_cert_workspace-config.yaml)
```yaml
portal:
 image:
   repository: test_portal13 #real
   pullPolicy: IfNotPresent
   tag: "master" #real
```
<a id='s3'></a>
### 5. Enabling data upload to AWS S3 bucket
* Create an S3 Bucket in AWS
* Replacing the values in the fence-config values file:
[`fence-config.yaml`](https://github.com/naultran/toxdatacommons/blob/main/deploy_gen3/fairtox.com/value_yaml/fence-config.yaml)
```yaml
fence:
  FENCE_CONFIG:
    OPENID_CONNECT:
      google:
        client_id: $google_client_id
        client_secret: $google_client_secret
    AWS_CREDENTIALS:
      'CRED1':
        aws_access_key_id: $aws_access_key_id
        aws_secret_access_key: $aws_secret_access_key
    S3_BUCKETS:
      toxdatacommons-default-243323637959-upload: # real one
        cred: 'CRED1'
        region: 'us-east-1' # real one
    DATA_UPLOAD_BUCKET: 'toxdatacommons-upload' # real one
  USER_YAML: |
```

<a id='deploy-sh'></a>
## Deploying Gen3 using custom bash script 
To streamline the deployment of our local Gen3 instance we automated the process in `deploy_gen3.sh` which can be run after following the instructions above. 

Run `deploy_gen3.sh`.
```shell
chmod +x deploy_gen3.sh
./deploy_gen3.sh   # in the deploy_gen3.sh, you should remove the guppy_override.yaml and indexd_config.yaml at this time
```
Every time you want to upgrade the Gen3 deployment, just run this file.
Note: this file runs `fence_combine.sh`, `fence_email.py`. Please make sure Python3 is installed and that `fence_combine.sh` has the appropriate permissions.

<a id='explore'></a>
## Enabling the exploration page
Before doing this, you must make sure that some metadata has already been deposited to your Gen3 database and the your Gen3 instance is running.
* Use helm to install a elasticsearch (__must be version 7.10.2__)
```shell
helm repo add elastic https://helm.elastic.co
helm repo update
helm upgrade --install gen3 elastic/elasticsearch --version 7.10.2 -f values.yaml
```
```values.yaml```
```yaml
// https://github.com/jawadqur/gen3-argo-gitops/blob/master/qureshi.planx-pla.net/values/elasticsearch.yaml
clusterName: gen3-elasticsearch
maxUnavailable: 0
singleNode: true
replicas: 1
esConfig:
  elasticsearch.yml: |
    # Here we can add elasticsearch config
```
* Edit the `guppy_override.yaml` and `elasticsearch_setting.yaml`

```elasticsearch_setting.yaml```
```yaml
...
# replacing etlMapping.yaml part  with instruction(https://github.com/uc-cdis/tube/blob/7450d5dc16ec875733bb2868782489921a622dc6/docs/configuration_file.md)
etlMapping.yaml: |
    mappings:
...
```
```guppy_override.yaml```
```yaml
guppy:
  enabled: true
  ...
  
  indices:
    - index: fairtox_etl  #consistent with elasticsearch_setting.yaml
      type: subject #consistent with elasticsearch_setting.yaml
    - index: fairtox_file #consistent with elasticsearch_setting.yaml
      type: file #consistent with elasticsearch_setting.yaml
  configIndex: fairtox_etl-array-config #consistent with elasticsearch_setting.yaml

  ...

```
* Put ```guppy_override.yaml``` back  ```deploy_gen3.sh``` and run it
* run the following code
```shell
kubectl apply -f ./value_yaml/elasticsearch_setting.yaml
```
* At this time you might see some issues in ETL pods, this is because the official image has a bug (if you don't meet it, possibly because it was fixed.) Run the following code to fix it
```shell
docker run -it --name correct_tube_image quay.io/cdis/tube:feat_helm_test /bin/bash
# and then you access to the image folder
cd ./tube/elt/outputs/es
vi timestamp.py
```
changing the following code
```py
def get_timestamp_from_index(es, versioned_index):
    res = es.indices.get_alias(index=versioned_index, name="time_*")
    iso_str = list(res[versioned_index]["aliases"].keys())[0].replace("plus", "+")[5:]
    return datetime.strptime(iso_str, "%Y-%m-%dT%H:%M:%S.%f") # to be "%Y-%m-%dT%H-%M-%S.%f"

```
```shell
exit
docker commit correct_tube_image quay.io/cdis/tube:feat_helm_test
```
* edit ```update_exploration.sh``` and run it
```shell
KUBECTL_PATH=/home/rance/.rd/bin/kubectl # run ```which kubectl``` and replace this line
$KUBECTL_PATH delete jobs etl2
$KUBECTL_PATH apply -f ./value_yaml/elasticsearch_setting.yaml # replace this line to be the absolute path.
```
* every time you upload new data, you should run ```update_exploration.sh```. Or, you could create a cronjob to run this file per hour.

<a id='indexd'></a>
## Setting up Indexd
The instruction below describe how to assign a prefix for indexd records and enable the monitoring and linking of data objects to their record in Gen3. _Note that some of these pieces are not optimized but they do work_. 
* Edit the [`indexd_config`](google.com) file
```yaml
indexd:
  enabled: true

  
  defaultPrefix: "dg.TDC/"  # replace with real one


  secrets:
    userdb:
      fence:
      sheepdog:
ssjdispatcher:
  enabled: true  # be false first
  image:
    repository: quay.io/cdis/ssjdispatcher

    pullPolicy: IfNotPresent
 
    tag: "test"
  awsRegion: us-east-1 # replace with real one
  
  awsStsRegionalEndpoints: regional
  ssjcreds:
    sqsUrl: "https://sqs.us-east-1.amazonaws.com/243323637959/toxdatacommons-upload/" # replace with real one
    jobPattern: "s3://toxdatacommons-default-upload/*" # replace with real one
    jobUser: "gdcapi" 
    jobPassword: "gdcapi"
    metadataserviceUsername: "toxdatacommon_ssj_job_metadataservice"
    metadataservicePassword: "ssj_job_metadataservice"
```
*  Create a new admin user in the indexd pod to enable linking data files to data model nodes. This can be done as described [here](https://github.com/naultran/toxdatacommons/blob/c9addf2abb3baed0ecfd13dd3ae2f26cbbe7d958/README.md?plain=1#L160C1-L160C1).
* After editing the `indexd_config.yaml`, put it back `deploy_gen3.sh` and run it.
* Following [these instructions](https://github.com/naultran/toxdatacommons/blob/main/README.md#enabling-ssjdispatcher) to enable ssjdispatcher.
* run ```deploy_gen3.sh``` again.
