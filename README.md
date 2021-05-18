# LEI Project

## NextCloud

### Prerequisites:

-   [Helm](https://helm.sh/docs/intro/install)
-   Nextcloud Repo (after install helm)
    ```bash
    helm repo add nextcloud https://nextcloud.github.io/helm
    helm repo update
    ```

### Usage

```bash
# install nexcloud in custom namespace named 'nextcloud'
helm install -n nextcloud nextcloud  nextcloud/nextcloud -f nextcloud.yml --create-namespace

# uninstall
helm uninstall -n nextcloud nextcloud
```

To switch to a different namespace:

```bash
kubectl config set-context --current --namespace=<NAMESPACE_NAME>
```

After installing, access [cloud74:30000](http://cloud74:30000).

## Wiki

### Prerequisites:

-   [Helm](https://helm.sh/docs/intro/install)

### Usage

```bash
# install nexcloud in custom namespace named 'nextcloud'
cd wiki
helm install -n wiki wiki helm -f wiki.yml --create-namespace

# uninstall
helm uninstall -n wiki wiki
```

After installing, access [cloud74:30002](http://cloud74:30002).

## Peertube

### Prerequisites:

-   [Helm](https://helm.sh/docs/intro/install)

### Usage

```bash
# install nexcloud in custom namespace named 'nextcloud'
cd wiki
helm install -n peertube peertube helm -f peertube.yml --create-namespace

# uninstall
helm uninstall -n peertube peertube
```

After installing, access [cloud74.cluster.lsd.di.uminho.pt:30001](http://cloud74.cluster.lsd.di.uminho.pt:30001).

To switch to a different namespace:

```bash
kubectl config set-context --current --namespace=<NAMESPACE_NAME>
```

## Authors

-   **Daniel Regado:** [guiyrt](https://github.com/guiyrt)
-   **Diogo Ferreira:** [DiogoFerreira99](https://github.com/DiogoFerreira99)
-   **Filipe Freitas:** [filipejsfreitas](https://github.com/filipejsfreitas)
-   **Vasco Ramos:** [vascoalramos](https://vascoalramos.me)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
