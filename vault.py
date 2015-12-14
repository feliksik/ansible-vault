import os, sys
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

        splitted = terms.split(':')
        if len(splitted)<2:
            raise errors.AnsibleError("secret '%s' does not specify a secret field, only a path." % terms)

        secret = splitted[0]
        field = splitted[1]

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

        if field == "": # we want the entire dict
            return [ data ]
        else:
           if not (field in data):
               raise errors.AnsibleError("Vault secret %s does not contain field %s" % (secret, field))
           return [ data[field] ]
