# LEI Project

## NextCloud

### Prerequisites:

-   [Helm](https://helm.sh/docs/intro/install)
-   Nexcloud Repo (after install helm)
    ```bash
    helm repo add nextcloud https://nextcloud.github.io/helm
    helm repo update
    ```

### Usage

```bash
# install nexcloud in custom namespace named 'nextcloud'
helm install -n nextcloud my-release nextcloud/nextcloud -f values.yml --create-namespace

# uninstall
helm uninstall my-release
```

To switch to a different namespace:
```bash
kubectl config set-context --current --namespace=<NAMESPACE_NAME>
```

After installing, access [cloud74:30000](http://cloud74:30000).

## Authors

-   **Daniel Regado:** [guiyrt](https://github.com/guiyrt)
-   **Diogo Ferreira:** [DiogoFerreira99](https://github.com/DiogoFerreira99)
-   **Filipe Freitas:** [filipejsfreitas](https://github.com/filipejsfreitas)
-   **Vasco Ramos:** [vascoalramos](https://vascoalramos.me)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
