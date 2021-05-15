A storage class local tem o nome de local-storage.
A storage class do NFS tem o nome de nfs-client.

A storage class do NFS foi instalada com o helm:
> helm repo add nfs-subdir-external-provisioner https://kubernetes-sigs.github.io/nfs-subdir-external-provisioner/
> helm install nfs-subdir-external-provisioner nfs-subdir-external-provisioner/nfs-subdir-external-provisioner --set nfs.server=192.168.112.108 --set nfs.path=/mnt/nfs-share
