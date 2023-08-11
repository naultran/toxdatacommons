KUBECTL_PATH=/home/rance/.rd/bin/kubectl
$KUBECTL_PATH delete jobs etl2
$KUBECTL_PATH apply -f ./value_yaml/elasticsearch_setting.yaml
