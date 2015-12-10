# ansible-vault lookup module
This is a lookup module for generic secrets in [Vault](https://vaultproject.io/)(the  HashiCorp project).

### Installation
lookup plugins can be loaded from several different locations similar to $PATH, see
[http://docs.ansible.com/ansible/intro_configuration.html#lookup-plugins](docs).

This module require the [requests](http://docs.python-requests.org/en/latest/) python library.

### Usage
The address to the Vault server and the auth token are fetched from environment variables

    export VAULT_ADDR=http://192.168.33.10:8200/
    export VAULT_TOKEN=56f48aef-8ad3-a0c4-447b-8e96990776ff

ansible-vault then works as any other lookup plugin

```yaml
- debug: msg="{{lookup('vault', 'secret=secret/foo field=somevalue')}}"
```

```yaml
- debug: msg="{{item}}"
  with_vault: secret=secret/foo field=somevalue
```
