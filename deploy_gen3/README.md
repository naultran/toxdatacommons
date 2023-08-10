# Instruction of deploying gen3-helm locally logging in with google accouts
Editor: Shuangyu Zhao, Michigan State University

## 1. Installing Racher Desktop and Gen3
Following the [official instruction](https://github.com/uc-cdis/gen3-helm/blob/master/docs/gen3_developer_environments.md#local-dev-linux-ubuntu--rancher-desktop-problems).

## 2. Pulling the templates needed

* The whole deploy_gen3 folder
* The python script: toxdatacommons/custom_configs/schema_compile.py
* The folder: gen3-helm/docs/portal [link](https://github.com/uc-cdis/gen3-helm/tree/master/docs/portal)

## 3. Building the metadate schema

* Creating a folder which stores all nodes' yaml files(Note: ```_definitions.yaml```, ```_settings.yaml```, ```_terms.yaml```, ```program.yaml```, ```project.yaml```, ```core_metadata_collection.yaml``` are required).

* Writing the nodes' file
normal nodes
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
nodes of data file 
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
* run the schema_compile.py (replace some values in it first)
```
from dictionaryutils import dump_schemas_from_dir
import json

#import dictionaryutils 
schema = dump_schemas_from_dir(directory="xxx/xxx")   // path to the folder which stores all the nodes' files
schema["_settings.yaml"]["_dict_version"] = "0.1"    // replae the "0.1" to the dictionary version you want

with open('.xxxx/schema.json', 'w') as json_file:  // path to where you want to store the schema.json
    json.dump(schema, json_file)

```
Note: The schema.json should be backup in a PUBLIC online repository. 
* repace the value in ```global_portal_cert_workspace-config.yaml```
```
global:
  dev: true
  hostname: fairtox.com 
  dictionaryUrl: "https://raw.githubusercontent.com/naultran/toxdatacommons/main/custom_configs/schema.json" // the links of schema.json(raw file )
  tierAccessLevel: "libre"
  tierAccessLimit: '"1000"'
```

## 4. fullfilling the secret.yaml in value_yaml folder
```google_client_id``` and ```google_client_secret``` are related with the option of using google accounts to log in; ```aws_access_key_id``` and ```aws_secret_access_key``` are used to link to S3 bucket where the data files are uploaded.

## 5. Setting the limitations for visitors
You should customize two files.
* ```user_template.yaml``` 
```
// customize it
...
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
* ```emails.json```
```
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
## 6. Creating the certificate
* Following the [instruction](https://github.com/naultran/toxdatacommons/blob/main/README.md)
* Updating values 
```global_portal_cert_workspace-config.yaml```
```
global:
  dev: true
  hostname: fairtox.com  // your host name
  dictionaryUrl: "https://raw.githubusercontent.com/naultran/toxdatacommons/main/custom_configs/schema.json" 
  tierAccessLevel: "libre"
  tierAccessLimit: '"1000"'

...

revproxy:
  ingress:
    # Enable the custom ingress resource included by helm. Add any configurations as needed.
    enabled: true
    # Any annotations that needs to be passed to the ingress resource
    annotations:
    hosts:
    # Replace with your hostname
    - host: fairtox.com  // host name
      paths:
        - path: /
          pathType: Prefix
    tls:
      # this is the secret generated by the cert and key from global.tls
      # if you have your own secret, reference that. 
      - secretName: fairtox-cert // secret name 
        hosts:
        # Replace with your hostname
          - fairtox.com  // host name
...
```
## 7. AWS S3 (uploading data files)
* creating a S3 Bucket in AWS
* replacing the values
```fence-config.yaml```
```
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
      toxdatacommons-default-243323637959-upload: // real one
        cred: 'CRED1'
        region: 'us-east-1' // real one
    DATA_UPLOAD_BUCKET: 'toxdatacommons-default-243323637959-upload' // real one
  USER_YAML: |
```

## 8. Setting portal
If you have not prebuilt the portal, in the ```global_portal_cert_workspace-config.yaml```, please change the portal part be this.
[gitops.json instruction](https://github.com/uc-cdis/data-portal/blob/258781b73f1444d9db0b97f5aad4f4fd71f7efda/docs/portal_config.md)
```
...
portal:
  gitops:  
    json|
     ......// the [gitops.json](https://github.com/uc-cdis/gen3-helm/blob/master/helm/portal/values.yaml#L202-L461)  
...
```
or delete this part using the default portal which is fine when you just test.

### prebuilding portal 
When you prebuilding the portal, your gen3 should be running at the same time.
* Go to the portal folder pulled from uc-cdis.
* Go to the ```configuration```, and create a folder named by your host name.
* In this folder, store ```gitops.json```, ```gitops.css```...([gitops.json instruction](https://github.com/uc-cdis/data-portal/blob/258781b73f1444d9db0b97f5aad4f4fd71f7efda/docs/portal_config.md))
* change some code in Dockerfile
```
ARG CODE_VERSION=master
FROM node:16 as builder

ARG PORTAL_HOSTNAME  // ARG PORTAL_HOSTNAME=<the real host name which is consistent with the folder name settled.>

ENV APP gitops
ENV BASENAME /
...
// if you want to set ```resources``` in portal, I recommend you pulling the repository which store the html files and png files
RUN git clone https://xxxx.xxx/xxxx
...
RUN COMMIT=`git rev-parse HEAD` && echo "export const portalCommit = \"${COMMIT}\";" >src/versions.js \
    && VERSION=`git describe --always --tags` && echo "export const portalVersion =\"${VERSION}\";" >>src/versions.js

// replace above code to be the following one
RUN COMMIT=`git rev-parse HEAD` && echo "export const portalCommit = \"${COMMIT}\";" >src/versions.js \
  && echo "export const portalVersion ='2023.08';" >>src/versions.js // replace '2023.08' to be the portal version you want
...

COPY --from=builder /data-portal/src/css/ /usr/share/nginx/html/src/css/
// if you want to set ```resources``` in portal
COPY --from=builder /data-portal/<repository_name_you_pulling>/ /usr/share/nginx/html/<repository_name_you_pulling>/
COPY overrides/dockerStart.sh dockerStart.sh
CMD bash ./dockerStart.sh
```
* following the [code](https://github.com/uc-cdis/gen3-helm/blob/master/docs/portal/prebuild-portal.md) to build a new image, and replace the portal part to be the real values.
```global_portal_cert_workspace-config.yaml```
```
portal:
 image:
   repository: test_portal13 //real
   pullPolicy: IfNotPresent
   tag: "master" //real
```

## 9. Deploying gen3 
Run ```deploy_gen3.sh``` file in terminal.
```
chmod +x deploy_gen3.sh
./deploy_gen3.sh   // in the deploy_gen3.sh, you should remove the guppy_override.yaml and indexd_config.yaml at this time
```
Every time you want to upgrade the gen3 website, just run this file.
Note: this file runs ```fence_combine.sh```, ```fence_email.py```. Please make sure installing the python3, and giving the permission to ```fence_combine.sh``` file.

## 10. Setting exploration
Before doing this, you must make sure database has some data, and gen3 is running.
* Use helm to install a elasticsearch (do not use the latest version)
```
helm repo add elastic https://helm.elastic.co
helm repo update
helm upgrade --install gen3 elastic/elasticsearch --version 7.10.2 -f values.yaml
```
```values.yaml```
```
// https://github.com/jawadqur/gen3-argo-gitops/blob/master/qureshi.planx-pla.net/values/elasticsearch.yaml
clusterName: gen3-elasticsearch
maxUnavailable: 0
singleNode: true
replicas: 1
esConfig:
  elasticsearch.yml: |
    # Here we can add elasticsearch config
```
* editing the ```guppy_override.yaml``` and ```jawad_setting.yaml```
```jawad_setting.yaml```
... //editing the following part with [instruction](https://github.com/uc-cdis/tube/blob/7450d5dc16ec875733bb2868782489921a622dc6/docs/configuration_file.md)
etlMapping.yaml: |
    mappings:
      - name: fairtox_etl
        doc_type: subject
        type: aggregator
        root: subject
        props:
          - name: submitter_id
          - name: project_id
          - name: sex
          - name: euthanasia_method
          - name: strain
        parent_props:
          - path: studies[studyID:submitter_id, organism, study_design, study_type, experimental_setting]
        nested_props:
          - name: treatment
            path: treatments
            props:
              - name: test_article_name
        aggregated_props:
          - name: _samples_count
            path: samples
            fn: count
          - name: _aliquots_count
            path: samples.aliquots
            fn: count
          - name: _flow_data_count
            path: samples.aliquots.flow_cytometry_assays.flow_datas
            fn: count
          - name: _flow_analysis_data_count
            path: samples.aliquots.flow_cytometry_assays.flow_datas.flow_analysises.flow_analysis_datas
            fn: count
          - name: _ms_raw_data_count
            path: samples.aliquots.mass_spec_assays.ms_raw_datas
            fn: count
          - name: _ms_analysed_data_count
            path: samples.aliquots.mass_spec_assays.ms_raw_datas.ms_analyses
            fn: count
          - name: _weight_measurement_count
            path: housings.diets.weight_measurements
            fn: count
          - name: _slide_image_count
            path: samples.aliquots.slides.slide_images
            fn: count
          - name: _unaligned_read_count
            path: samples.aliquots.read_groups.unaligned_reads
            fn: count
          - name: _unaligned_reads_qc_count
            path: samples.aliquots.read_groups.unaligned_reads_qcs
            fn: count
          - name: _aligned_read_count
            path: samples.aliquots.read_groups.aligned_reads
            fn: count
          - name: _aligned_reads_analyzed_data_count
            path: samples.aliquots.read_groups.aligned_reads.alignment_workflows.aligned_reads_analyzed_datas
            fn: count
        joining_props:
          - index: file
            join_on: _subject_id
            props:
              - name: data_format
                src: data_format
                fn: set
              - name: data_type
                src: data_type
                fn: set
              - name: file_name
                src: file_name
                fn: set

      - name: fairtox_file
        doc_type: file
        type: collector
        root: None
        category: data_file
        props:
          - name: object_id
          - name: md5sum
          - name: file_name
          - name: file_size
          - name: data_format
          - name: data_type
          - name: state
          - name: SRA_accession_id
        injecting_props:
          subject:
            props:
              - name: _subject_id
                src: id
                fn: set
              - name: project_id
          study:
            props:
              - name: study_submitter_id
                src: submitter_id
                fn: set
              - name: _study_id
                src: id
                fn: set
              - name: project_id
...
```guppy_override.yaml```
```
elasticsearch:
  enabled: false
guppy:
  enabled: true
  # -- (int) Only relevant if tireAccessLevel is set to "regular". 
  # The minimum amount of files unauthorized users can filter down to

  image:
    repository: quay.io/cdis/guppy
    pullPolicy: IfNotPresent
    tag: "feat_es7"

  # -- (list) Elasticsearch index configurations
  indices:
    - index: fairtox_etl  //consistent with jawad_setting.yaml
      type: subject //consistent with jawad_setting.yaml
    - index: fairtox_file //consistent with jawad_setting.yaml
      type: file //consistent with jawad_setting.yaml
  # -- (string) The Elasticsearch configuration index
  configIndex: fairtox_etl-array-config //consistent with jawad_setting.yaml
  # -- (string) The field used for access control and authorization filters
  authFilterField: auth_resource_path
  # -- (bool) Whether or not to enable encryption for specified fields
  enableEncryptWhitelist: true
  # -- (string) A comma-separated list of fields to encrypt
  encryptWhitelist: test1

  esEndpoint: "gen3-elasticsearch-master:9200"

  dbRestore: False

```
* Put back the ```guppy_override.yaml``` and run ```deploy_gen3.sh```
* run the following code
```
kubectl apply -f ./value_yaml/jawad_settings.yaml
```
* At this time you might meet issue in etl pods, this is because the official image has a bug(if you don't meet it, possibly because it was fixed.) Run the following code to fix it
```
docker run -it --name correct_tube_image quay.io/cdis/tube:feat_helm_test /bin/bash
// and then you access to the image folder
cd ./tube/elt/outputs.es
vi timestamp.py
```
changing the following code
```
def get_timestamp_from_index(es, versioned_index):
    res = es.indices.get_alias(index=versioned_index, name="time_*")
    iso_str = list(res[versioned_index]["aliases"].keys())[0].replace("plus", "+")[5:]
    return datetime.strptime(iso_str, "%Y-%m-%dT%H:%M:%S.%f") // to be "%Y-%m-%dT%H-%M-%S.%f"

```
```
exit
docker commit correct_tube_image quay.io/cdis/tube:feat_helm_test
```
* edit ```update_exploration.sh``` and run it
```
KUBECTL_PATH=/home/rance/.rd/bin/kubectl // run ```which kubectl``` and replace this line
$KUBECTL_PATH delete jobs etl2
$KUBECTL_PATH apply -f ./value_yaml/jawad_settings.yaml // replace this line to be the absolute path.
```
* every time you upload new data, you should run ```update_exploration.sh```. Or, you could create a cronjob to run this file per hour.

## 11. Setting indexd
* Edit indexd_config
```
indexd:
  enabled: true

  # default prefix that gets added to all indexd records.
  defaultPrefix: "dg.TDC/"  // replace with real one

  # Secrets for fence and sheepdog to use to authenticate with indexd.
  # If left blank, will be autogenerated.
  secrets:
    userdb:
      fence:
      sheepdog:
ssjdispatcher:
  enabled: true  // be false first
  image:
    repository: quay.io/cdis/ssjdispatcher
  # -- (string) Docker pull policy.
    pullPolicy: IfNotPresent
  # -- (string) Overrides the image tag whose default is the chart appVersion.
    tag: "test"
  awsRegion: us-east-1 // replace with real one
  # -- (string) AWS STS to issue temporary credentials to users and roles that make an AWS STS request. Values regional or global.
  awsStsRegionalEndpoints: regional
  ssjcreds:
    sqsUrl: "https://sqs.us-east-1.amazonaws.com/243323637959/toxdatacommons-default-243323637959-upload_data_upload/" // replace with real one
    jobPattern: "s3://toxdatacommons-default-243323637959-upload/*" // replace with real one
    jobUser: "gdcapi" 
    jobPassword: "gdcapi"
    metadataserviceUsername: "toxdatacommon_ssj_job_metadataservice"
    metadataservicePassword: "ssj_job_metadataservice"
```
* Put back the ```indexd_config.yaml``` and run ```deploy_gen3.sh```
* following [this instruction](https://github.com/naultran/toxdatacommons/blob/main/README.md#enabling-ssjdispatcher) to enable ssjdispatcher
* run ```deploy_gen3.sh``` again.





