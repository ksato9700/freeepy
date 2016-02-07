# -*- coding: utf-8 -*-
#
# Copyright 2016 Kenichi Sato
#
from freee.client import FreeeClient

import os
import sys
import json

def main():
    client = FreeeClient(
        os.environ['OAUTH2_FREEE_CLIENT_ID'],
        os.environ['OAUTH2_FREEE_CLIENT_SECRET'],
        os.environ['OAUTH2_FREEE_REDIRECT_URI'],
    )

    TOKEN_FILE = 'freee.token'
    try:
        with open(TOKEN_FILE) as fp:
            resp = json.load(fp)
    except IOError as e:
        print(e)
        if len(sys.argv) > 1:
            resp = client.get_token_by_code(sys.argv[1])
            with open(TOKEN_FILE, 'w') as wfp:
                wfp.write(json.dumps(resp))
        else:
            print(client.get_code_url())
            sys.exit(0)

    client.set_token(resp)

    req_body = {
        "company_id" : 583235,
        "name" : "新しい勘定科目",
        "shortcut" : "NEWACCOUNTITEM",
        "shortcut_num" : "999",
        "tax_name" : "課税売上",
        "group_name" : "その他預金",
        "account_category" : "現金・預金",
        "corresponding_income_name" : "売掛金",
        "corresponding_expense_name" : "買掛金"
    }

    print(client.add_account_item(req_body))
    #co = client.companies['companies'][0]['display_name']
    #print(co)
    #print(client.me)

if __name__ == '__main__':
    main()
