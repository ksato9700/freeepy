#
# Copyright 2016 Kenichi Sato
#
from __future__ import print_function
from .exception import *

import requests
import json

# import logging
# logging.basicConfig(level=logging.INFO)

FREEE_AUTH_ENDPOINT_URL = "https://secure.freee.co.jp"
FREEE_API_ENDPOINT_URL = "https://api.freee.co.jp"

DEFAULT_TOKENFILE = ".freee.token"

class FreeeClient:
    def __init__(self, client_id, client_secret, redirect_uri, token_fp=None):
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.token_fp = token_fp or open(DEFAULT_TOKENFILE, 'a+')

        try:
            self.token_fp.seek(0)
            self._set_token(json.load(self.token_fp))
        except Exception as e:
            print(e)
            pass

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

    def _get_set_write_token(self, data):
        r = requests.post(FREEE_AUTH_ENDPOINT_URL + "/oauth/token", data=data)
        r.raise_for_status()
        rtxt = r.text
        self.token_fp.seek(0)
        self.token_fp.truncate()
        self.token_fp.write(rtxt)
        self._set_token(json.loads(rtxt))

    def get_token_by_code(self, auth_code):
        self._get_set_write_token({
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'grant_type': 'authorization_code',
            'code': auth_code,
            'redirect_uri': self.redirect_uri,
        })

    def token_refresh(self):
        self._get_set_write_token({
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'grant_type': 'refresh_token',
            'refresh_token': self.refresh_token,
        })

    def _set_token(self, token):
        self.access_token = token['access_token']
        self.token_type = token['token_type']
        self.refresh_token = token['refresh_token']

    def _access_resource(self, method, path, data=None):
        if not hasattr(self, 'access_token'):
            raise FreeeAccessTokenNotSet

        url = FREEE_API_ENDPOINT_URL + path
        headers = {
            'Authorization': "Bearer " + self.access_token
        }
        if data:
            r = requests.post(url, headers=headers, json=data)
        else:
            r = requests.get (url, headers=headers)

        r.raise_for_status()

        rj = r.json()
        if 'errors' in rj:
            raise FreeeResponseError(rj)
        return rj


    def _get_resource(self, path):
        return self._access_resource(requests.get, path)

    def _post_resource(self, path, data):
        return self._access_resource(requests.post, path, data)

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

    def company(self, id):
        return self._get_resource('/api/1/companies/{}'.format(id))

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
