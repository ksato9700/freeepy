# -*- coding: utf-8 -*-
#
# Copyright 2014 Kenichi Sato <ksato9700@gmail.com>
#
from __future__ import print_function, unicode_literals

from freee.client import FreeeClient
from freee.exception import *
import responses
import json


from nose.tools import eq_, ok_, raises

@raises(FreeeAccessTokenNotSet)
def test_access_token_not_set():
    client = FreeeClient(
        'my_client_id',
        'my_client_secret',
        'my_redirect_uri',
    )
    res = client.me

def _create_client():
    client = FreeeClient(
        'my_client_id',
        'my_client_secret',
        'my_redirect_uri',
    )
    client.set_token({
        'access_token': 'my_access_token',
        'token_type': 'my_token_type',
        'refresh_token': 'my_refresh_token',
    })
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
