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
import zabbix_login
from pprint import pprint
from json2html import *
import send_message
import css_table


zabbix_api_url = "http://monitor.idc.yst.com.cn/zabbix/api_jsonrpc.php"
session = zabbix_login.login()
                                                                        
head = ['Content-Type:application/json']
curl = pycurl.Curl()
curl.setopt(pycurl.URL, zabbix_api_url)
curl.setopt(pycurl.CONNECTTIMEOUT, 1)
curl.setopt(pycurl.TIMEOUT, 60)
curl.setopt(pycurl.NOPROGRESS, 1)
#curl.setopt(pycurl.FORBID_REUSE, 1)
curl.setopt(pycurl.HTTPHEADER,  head)


def trigger_get_monitored():
    trigger_get_monitored_json = json.dumps({
        "jsonrpc": "2.0",
        "method": "trigger.get",
        "params": {
            "output": ["description","triggerid","lastchange"],
            "only_true": 1,
            "monitored": 1
            },
        "auth": session,
        "id": 1})

    result = StringIO.StringIO()
    curl.setopt(pycurl.POSTFIELDS,trigger_get_monitored_json)
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

    trigger_dict = {}
    now = int(str(time.time()).split('.')[0])
    for r in json.loads(result.getvalue())['result']:
        #print r["triggerid"], r["description"], r["lastchange"]
        triggerid = r["triggerid"].encode('utf-8')
        description = r["description"].encode('utf-8')
        lastchange = r["lastchange"].encode('utf-8')
        lastchange = (now - int(lastchange)) / 86400
        lastchange = str(lastchange) + 'd ago'

        trigger_dict[triggerid] = [description, lastchange]

    result.close()
    return trigger_dict


def host_get_with_monitored_triggers():
    triggers = trigger_get_monitored()
    ops_daily = {}

    for k,v in triggers.items():
        host_get_with_monitored_triggers_json = json.dumps({
            "jsonrpc": "2.0",
            "method": "host.get",
            "params": {
                "output": ["host","groupid"],
                "triggerids": k,
                "selectGroups": "extend"
                },
            "auth": session,
            "id": 1})

        result = StringIO.StringIO()
        curl.setopt(pycurl.POSTFIELDS,host_get_with_monitored_triggers_json)
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

        for r in json.loads(result.getvalue())['result']:
            group_name = r["groups"][0]["name"].encode('utf-8')
            host_name = r["host"].encode('utf-8')

            ops_daily[k] = [group_name, host_name, v[0], v[1]]

    return ops_daily


def format_output():

    logfile_time =  time.strftime('%Y-%m-%d',time.localtime())
    ops_daily_dir = '/root/zhangshaobing/scripts/zabbix/ops_daily/'
    ops_daily_file = ops_daily_dir + 'ops_daily_%s.html' % logfile_time
    if os.path.exists(ops_daily_dir):
        pass
    else:
        os.makedirs(ops_daily_dir)

    ops_daily = host_get_with_monitored_triggers()
    #print type(ops_daily)

    css_table.css_table(ops_daily_file)

    html_start = """
<html>body td{ font-size:11px;}</style>
<body>
<table id="mytable" cellspacing="0" summary="OPS Daily %s">
<caption> </caption>
<tr>
    <th scope="col" abbr="group_name">group_name</th>
    <th scope="col" abbr="host_name">host_name</th>
    <th scope="col" abbr="trigger">trigger</th>
    <th scope="col" abbr="lastchange">lastchange</th>
    <th scope="col" abbr="trigger_id">trigger_id</th>
</tr>
""" % logfile_time

    with open(ops_daily_file,"a+") as f:
        f.write(html_start)

    #ops_daily_format = []
    count = 0
    for k,v in sorted(ops_daily.items(), lambda x, y: cmp(x[1], y[1])):
        #print k,v[0],v[1],v[2],v[3]
        #dict = {"trigger_id":k, "group_name":v[0], "host_name":v[1], "trigger":v[2], "lastchange":v[3]}
        #ops_daily_format.append(dict)

        count = count + 1
        if count % 2 != 0:
            row = """
<tr>
    <td>%s</td>
    <td>%s</td>
    <td>%s</td>
    <td>%s</td>
    <td>%s</td>
</tr>
""" % (v[0], v[1], v[2], v[3], k)

            with open(ops_daily_file,"a+") as f:
                f.write(row)
        else:
            row = """
<tr>
    <td class="alt">%s</td>
    <td class="alt">%s</td>
    <td class="alt">%s</td>
    <td class="alt">%s</td>
    <td class="alt">%s</td>
</tr>
""" % (v[0], v[1], v[2], v[3], k)

            with open(ops_daily_file,"a+") as f:
                f.write(row)

    html_end = """
</table>
</body>
</html> 
"""
    with open(ops_daily_file,"a+") as f:
        f.write(html_end)

    maillist = 'nf_xxbywb@mail.nfsq.com.cn'
    send_message.send_message(maillist,ops_daily_file)


if __name__ == '__main__':
    #trigger_get_monitored()
    #host_get_with_monitored_triggers()
    format_output()
