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
```
