# -*- coding: utf-8 -*-
#
# Copyright 2014 Kenichi Sato <ksato9700@gmail.com>
#
from __future__ import print_function, unicode_literals

from freee.client import FreeeClient
from freee.exception import *

import io
import responses
import json
from requests.compat import is_py2
if is_py2:
    import urlparse
else:
    import urllib.parse as urlparse

from nose.tools import eq_, ok_, raises

def test_get_url():
    client = FreeeClient(
        'my_client_id',
        'my_client_secret',
        'my_redirect_uri',
    )
    eq_(client.get_code_url(),
        "https://secure.freee.co.jp/oauth/authorize?" +
        "client_id={}&redirect_uri={}&response_type=code".format(
            'my_client_id',
            'my_redirect_uri',
        ))

    eq_(client.get_token_url(),
        "https://secure.freee.co.jp/oauth/authorize?" +
        "client_id={}&redirect_uri={}&response_type=token".format(
            'my_client_id',
            'my_redirect_uri',
        ))


@responses.activate
def test_get_token_by_code():
    res_body = {
        'access_token': 'my_access_token',
        'token_type': 'bearer',
        'expires_in': 10000,
        'refresh_token': 'my_refresh_token',
        'scope': 'read write'
    }

    responses.add(responses.POST,
                  "https://secure.freee.co.jp/oauth/token",
                  status=200,
                  body = json.dumps(res_body),
                  content_type="application/json")

    token_fp = io.StringIO("")
    client = FreeeClient(
        'my_client_id',
        'my_client_secret',
        'my_redirect_uri',
        token_fp,
    )
    auth_code = 'my_auth_code'
    client.get_token_by_code(auth_code)
    for attr in ('access_token', 'token_type', 'refresh_token'):
        eq_(res_body[attr], getattr(client, attr))

    token_fp.seek(0)
    eq_(token_fp.read(),
        "{\"access_token\": \"my_access_token\", "
        "\"token_type\": \"bearer\", "
        "\"expires_in\": 10000, "
        "\"refresh_token\": \"my_refresh_token\", "
        "\"scope\": \"read write\"}")

    eq_(len(responses.calls), 1)
    req_body = urlparse.parse_qs(responses.calls[0].request.body)
    eq_(req_body, {
        'client_id': ['my_client_id'],
        'client_secret': ['my_client_secret'],
        'grant_type': ['authorization_code'],
        'code': [auth_code],
        'redirect_uri': ['my_redirect_uri'],
        })


@responses.activate
def test_fresh_token():
    res_body = {
        'access_token': 'my_access_token2',
        'token_type': 'bearer',
        'expires_in': 10000,
        'refresh_token': 'my_refresh_token2',
        'scope': 'read write'
    }

    responses.add(responses.POST,
                  "https://secure.freee.co.jp/oauth/token",
                  status=200,
                  body = json.dumps(res_body),
                  content_type="application/json")

    token_fp = io.StringIO("{\"access_token\": \"my_access_token\","
                           "\"token_type\": \"my_token_type\","
                           "\"refresh_token\": \"my_refresh_token\"}")
    client = FreeeClient(
        'my_client_id',
        'my_client_secret',
        'my_redirect_uri',
        token_fp,
    )
    client.token_refresh()
    for attr in ('access_token', 'token_type', 'refresh_token'):
        eq_(res_body[attr], getattr(client, attr))

    token_fp.seek(0)
    eq_(token_fp.read(),
        "{\"access_token\": \"my_access_token2\", "
        "\"token_type\": \"bearer\", "
        "\"expires_in\": 10000, "
        "\"refresh_token\": \"my_refresh_token2\", "
        "\"scope\": \"read write\"}")

    eq_(len(responses.calls), 1)
    req_body = urlparse.parse_qs(responses.calls[0].request.body)
    eq_(req_body, {
        'client_id': ['my_client_id'],
        'client_secret': ['my_client_secret'],
        'grant_type': ['refresh_token'],
        'refresh_token': ['my_refresh_token'],
        })


@raises(FreeeAccessTokenNotSet)
def test_access_token_not_set():
    client = FreeeClient(
        'my_client_id',
        'my_client_secret',
        'my_redirect_uri',
        io.StringIO("")
    )
    res = client.me

def _create_client():
    token_fp = io.StringIO("{\"access_token\": \"my_access_token\","
                           "\"token_type\": \"my_token_type\","
                           "\"refresh_token\": \"my_refresh_token\"}")
    client = FreeeClient(
        'my_client_id',
        'my_client_secret',
        'my_redirect_uri',
        token_fp,
    )
    return client


@responses.activate
def test_get_me():
    body = {
        "user" : {
            "email" : "example@freee.co.jp",
            "display_name" : "フリー太郎",
            "first_name" : "太郎",
            "last_name" : "フリー",
            "first_name_kana" : "たろう",
            "last_name_kana" : "ふりー",
        }
    }

    responses.add(responses.GET,
                  "https://api.freee.co.jp/api/1/users/me",
                  status=200,
                  body = json.dumps(body),
                  content_type="application/json")

    client = _create_client()
    res = client.me
    eq_(res, body)

    eq_(len(responses.calls), 1)
    request_headers = responses.calls[0].request.headers
    eq_(request_headers['Authorization'], 'Bearer my_access_token')

@responses.activate
def test_get_account_items():
    body = {
        "account_items" : [
            {
                "id" : 101,
                "name" : "ソフトウェア",
                "shortcut" : "SOFUTO",
                "default_tax_id" : 12,
                "default_tax_code" : 108,
                "categories" : ["資産", "固定資産", "無形固定資産"]
            }
        ]}

    responses.add(responses.GET,
                  "https://api.freee.co.jp/api/1/account_items",
                  status=200,
                  body = json.dumps(body),
                  content_type="application/json")

    client = _create_client()
    res = client.account_items
    eq_(res, body)


@responses.activate
def test_add_account_items():
    req_body = {
        "company_id" : 1,
        "name" : "新しい勘定科目",
        "shortcut" : "NEWACCOUNTITEM",
        "shortcut_num" : "999",
        "tax_name" : "課税売上",
        "group_name" : "その他預金",
        "account_category" : "現金・預金",
        "corresponding_income_name" : "売掛金",
        "corresponding_expense_name" : "買掛金"
    }
    res_body = {
        "account_item" : {
            "id" : 102,
            "name" : "新しい勘定科目",
            "shortcut" : "NEWACCOUNTITEM",
            "shortcut_num" : "999",
            "tax_code" : 1,
            "group_name" : "その他預金",
            "account_category_id" : 36,
            "corresponding_income_name" : "売掛金",
            "corresponding_expense_name" : "買掛金"
            }
    }

    responses.add(responses.POST,
                  "https://api.freee.co.jp/api/1/account_items",
                  status=200,
                  body = json.dumps(res_body),
                  content_type="application/json")

    client = _create_client()
    res = client.add_account_item(req_body)
    eq_(res, res_body)


@responses.activate
def test_get_banks():
    body = {
        "banks" : [
            {
                "id" : 123,
                "name" : "〇〇銀行",
                "type" : "bank_account",
                "name_kana" : "マルマル"
            },
            {
                "id" : 456,
                "name" : "△△銀行",
                "type" : "bank_account",
                "name_kana" : "サンカク"
            },
        ]}

    responses.add(responses.GET,
                  "https://api.freee.co.jp/api/1/banks",
                  status=200,
                  body = json.dumps(body),
                  content_type="application/json")

    client = _create_client()
    res = client.banks
    eq_(res, body)

    
@responses.activate
def test_get_companies():
    body = {
        "companies" : [
            {
                "id" : 101,
                "name" : "freee事務所",
                "name_kana" : "フリージムショ",
                "display_name" : "freee事務所",
                "role" : "admin"
            },
            {
                "id" : 102,
                "name" : "freee事務所 2",
                "name_kana" : "フリージムショ2",
                "display_name" : "freee事務所2",
                "role" : "admin"
            },
        ]}

    responses.add(responses.GET,
                  "https://api.freee.co.jp/api/1/companies",
                  status=200,
                  body = json.dumps(body),
                  content_type="application/json")

    client = _create_client()
    res = client.companies
    eq_(res, body)


@responses.activate
def test_get_companies():
    companies_body = {
        "companies" : [
            {
                "id" : 101,
                "name" : "freee事務所",
                "name_kana" : "フリージムショ",
                "display_name" : "freee事務所",
                "role" : "admin"
            },
            {
                "id" : 102,
                "name" : "freee事務所 2",
                "name_kana" : "フリージムショ2",
                "display_name" : "freee事務所2",
                "role" : "admin"
            },
        ]}

    company_body = {
        "company": companies_body["companies"][1]
    }

    responses.add(responses.GET,
                  "https://api.freee.co.jp/api/1/companies",
                  status=200,
                  body = json.dumps(companies_body),
                  content_type="application/json")

    responses.add(responses.GET,
                  "https://api.freee.co.jp/api/1/companies/102",
                  status=200,
                  body = json.dumps(company_body),
                  content_type="application/json")

    client = _create_client()
    res = client.companies
    eq_(res, companies_body)
    res = client.company(102)
    eq_(res, company_body)
