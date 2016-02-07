#
# Copyright 2016 Kenichi Sato
#
from __future__ import print_function
from .exception import *

import requests

# import logging
# logging.basicConfig(level=logging.INFO)

FREEE_AUTH_ENDPOINT_URL = "https://secure.freee.co.jp"
FREEE_API_ENDPOINT_URL = "https://api.freee.co.jp"


class FreeeClient:
    def __init__(self, client_id, client_secret, redirect_uri):
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri

    def _authz_url(self, response_type):
        return "{}{}?client_id={}&redirect_uri={}&response_type={}".format(
            FREEE_AUTH_ENDPOINT_URL,
            "/oauth/authorize",
            self.client_id,
            self.redirect_uri,
            response_type
        )

    def get_code_url(self):
        return self._authz_url('code')

    def get_token_url(self):
        return self._authz_url('token')

    def get_token_by_code(self, auth_code):
        r = requests.post(
            FREEE_AUTH_ENDPOINT_URL + "/oauth/token",
            data={
                'client_id': self.client_id,
                'client_secret': self.client_secret,
                'grant_type': 'authorization_code',
                'code': auth_code,
                'redirect_uri': self.redirect_uri,
            }
        )
        return r.json()

    def set_token(self, token):
        self.access_token = token['access_token']
        self.token_type = token['token_type']
        self.refresh_token = token['refresh_token']

    def _get_resource(self, path):
        if not hasattr(self, 'access_token'):
            raise FreeeAccessTokenNotSet
        r = requests.get(
            FREEE_API_ENDPOINT_URL + path,
            headers={'Authorization': "Bearer " + self.access_token},
        )
        rj = r.json()
        if 'errors' in rj:
            print("".join(rj['errors'][0]['messages']))
        return rj

    def _post_resource(self, path, data):
        if not hasattr(self, 'access_token'):
            raise FreeeAccessTokenNotSet
        r = requests.post(
            FREEE_API_ENDPOINT_URL + path,
            headers={
                'Authorization': "Bearer " + self.access_token,
            },
            json=data,
        )
        print(r)
        print(r.text)
        rj = r.json()
        if 'errors' in rj:
            print("".join(rj['errors'][0]['messages']))
        return rj

    @property
    def account_items(self):
        return self._get_resource('/api/1/account_items')

    def add_account_item(self, item):
        return self._post_resource('/api/1/account_items', item)

    @property
    def banks(self):
        return self._get_resource('/api/1/banks')

    @property
    def companies(self):
        return self._get_resource('/api/1/companies')

    @property
    def deals(self):
        return self._get_resource('/api/1/deals')

    @property
    def items(self):
        return self._get_resource('/api/1/items')

    @property
    def journals(self):
        return self._get_resource('/api/1/journals')

    @property
    def partners(self):
        return self._get_resource('/api/1/partners')

    @property
    def sections(self):
        return self._get_resource('/api/1/sections')

    @property
    def selectables(self):
        return self._get_resource('/api/1/forms/selectables')

    @property
    def tags(self):
        return self._get_resource('/api/1/tags')

    @property
    def taxes(self):
        return self._get_resource('/api/1/taxes/codes')

    @property
    def transfers(self):
        return self._get_resource('/api/1/transfers')

    @property
    def wallet_txns(self):
        return self._get_resource('/api/1/wallet_txns')

    @property
    def walletables(self):
        return self._get_resource('/api/1/walletables')

    @property
    def me(self):
        return self._get_resource('/api/1/users/me')
