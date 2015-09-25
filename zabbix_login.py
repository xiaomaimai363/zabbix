#!/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import tab
import re
import commands
import time
import json
import pycurl
import StringIO
import log_record

def login():
    zabbix_api_url = "http://you_zabbix_url/api_jsonrpc.php"
    zabbix_user = "xxx"
    zabbix_pwd = "xxx"
    session = ""

    login_json = json.dumps({
        "jsonrpc": "2.0",
        "method": "user.login",
        "params": {
                "user": zabbix_user,
                "password": zabbix_pwd
            },
        "id": 1})

    head = ['Content-Type:application/json']
    curl = pycurl.Curl()
    curl.setopt(pycurl.URL, zabbix_api_url)
    curl.setopt(pycurl.CONNECTTIMEOUT, 1)
    curl.setopt(pycurl.TIMEOUT, 1)
    curl.setopt(pycurl.NOPROGRESS, 1)
    #curl.setopt(pycurl.FORBID_REUSE, 1)
    curl.setopt(pycurl.HTTPHEADER,  head)
    result = StringIO.StringIO()
    curl.setopt(pycurl.POSTFIELDS,login_json)
    curl.setopt(pycurl.WRITEFUNCTION, result.write)
                  
    count = 0
    while 1:
        count = count + 1
        if count > 3:
            print "Login error retry 3 times, exit!"
            sys.exit()
        else:
            try:
                curl.perform()
                break
            except Exception,e:
                print "connect nos error: %s" % e
                log_record.logging.warn(e)
                time.sleep(0.1)

    session = json.loads(result.getvalue())['result']
    return session


if __name__ == '__main__':
    login()
