# -*- coding: utf-8 -*-
#
# Copyright 2016 Kenichi Sato
#
from freee.client import FreeeClient

import os
import sys

def main():
    client = FreeeClient(
        os.environ['OAUTH2_FREEE_CLIENT_ID'],
        os.environ['OAUTH2_FREEE_CLIENT_SECRET'],
        os.environ['OAUTH2_FREEE_REDIRECT_URI'],
    )

    if(len(sys.argv)>1):
        client.get_token_by_code(sys.argv[1])
    try:
        print(client.me)
    except Exception as e:
        print(e)
        print(client.get_code_url())

    # req_body = {
    #     "company_id" : 583235,
    #     "name" : "新しい勘定科目",
    #     "shortcut" : "NEWACCOUNTITEM",
    #     "shortcut_num" : "999",
    #     "tax_name" : "課税売上",
    #     "group_name" : "その他預金",
    #     "account_category" : "現金・預金",
    #     "corresponding_income_name" : "売掛金",
    #     "corresponding_expense_name" : "買掛金"
    # }

if __name__ == '__main__':
    main()
