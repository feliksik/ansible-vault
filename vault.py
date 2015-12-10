import os
from urlparse import urljoin
from ansible import utils, errors
from ansible.utils import template

try:
    import requests
except ImportError:
    raise errors.AnsibleError("Module 'requests' is required to do vault lookups")

class LookupModule(object):

    def __init__(self, basedir=None, **kwargs):
        self.basedir = basedir

    def run(self, terms, inject=None, **kwargs):

        try:
            terms = template.template(self.basedir, terms, inject)
        except Exception, e:
            pass

        vault_args = terms.split(' ')
        vault_dict = {}

        for param in vault_args:
            key, value = param.split('=')
            vault_dict[key] = value

        if not ('secret' in vault_dict):
            raise errors.AnsibleError('module needs secret= parameter')
        if not ('field' in vault_dict):
            raise errors.AnsibleError('module needs field= parameter')

        secret = vault_dict['secret']
        field = vault_dict['field']

        url = os.getenv('VAULT_ADDR')
        if not url:
            raise errors.AnsibleError('VAULT_ADDR environment variable is missing')

        token = os.getenv('VAULT_TOKEN')
        if not token:
            raise errors.AnsibleError('VAULT_TOKEN environment variable is missing')

        request_url = urljoin(url, "v1/%s" % (secret))
        r = requests.get(request_url, headers = {
            "X-Vault-Token": "%s" % token,
            "Content-Type": "application/json" }
        )

        if r.status_code != 200:
           raise errors.AnsibleError("Failed to get %s from Vault: %s" % (secret, ','.join(r.json()['errors'])))

        data = r.json()['data']

        if not (field in data):
           raise errors.AnsibleError("Vault secret %s does not contain field %s" % (secret, field, str(data)))

        return [ data[field] ]
