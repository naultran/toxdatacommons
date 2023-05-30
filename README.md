# MSU SRC Tox Data Commons

## Deployment of developer (local) instance of Gen3 using  Helm

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

#### override the default values.yaml file
This part can customize the website.
* read the default values.yaml file [link for the all pods](https://github.com/uc-cdis/gen3-helm/tree/master/helm).
* edit your own values.yaml.

For example,
1. You want to customize the fence [link for the fence's values.yaml](https://github.com/uc-cdis/gen3-helm/blob/master/helm/fence/values.yaml). And what you want to change is the [USER_YAML](https://github.com/uc-cdis/gen3-helm/blob/master/helm/fence/values.yaml#LL479C2-L479C2) part. In the values.yaml which will be pushed to gen3/gen3, you should add:
```
fence:
  USER_YAML: |
      ....things you want to customize...
```
2. If you want to customize the portal to read the image we prebuild([instruction to prebuild the portal](https://github.com/uc-cdis/gen3-helm/blob/4415e61a992e9c9113bc7f1531ec8387d3886404/docs/portal/prebuild-portal.md)). And this is the [part](https://github.com/uc-cdis/gen3-helm/blob/master/helm/portal/values.yaml#L65) we want to change.
```
portal:
  image:
    repository: <repository name in rancher destop>
    pullPolicy: IfNotPresent
    tag: <self defined tag which can be checked on rancher desktop>

```

#### Wait for changes to propagate
