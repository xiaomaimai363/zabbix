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
    trigger_with_host = {}

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
            group_id = r["groups"][0]["groupid"].encode('utf-8')
            host_name = r["host"].encode('utf-8')
            host_id = r["hostid"].encode('utf-8')
            trigger_id = k
            trigger_desc = v[0]
            trigger_lastchange = v[1]

            trigger_with_host[trigger_id] = [group_name, group_id, host_name, host_id, trigger_desc, trigger_lastchange]

        result.close()
    #print trigger_with_host
    return trigger_with_host


def trigger_and_host_with_event():
    trigger_with_host = host_get_with_monitored_triggers()
    trigger_and_host_with_event = {}

    for k,v in trigger_with_host.items():
    #有ack的trigger，声明"acknowledged": "true"，无ack的将trigger将不会输出
    #按照event的clock和id进行sort desc并limit 1，从而获得trigger对应最新的event
        trigger_and_host_with_event_json = json.dumps({
            "jsonrpc": "2.0",
            "method": "event.get",
            "params": {
                "output": "acknowledged",
                "objectids": k,
                "acknowledged": "true",
                "select_acknowledges": ['acknowledgeid','eventid','message','name','clock'],
                "sortfield": ["clock", "eventid"],
                "sortorder": "DESC",
                "limit" : 1
                },
            "auth": session,
            "id": 1})

        result = StringIO.StringIO()
        curl.setopt(pycurl.POSTFIELDS,trigger_and_host_with_event_json)
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

        if json.loads(result.getvalue())['result']:
            for r in json.loads(result.getvalue())['result']:
                group_name = v[0]
                group_id = v[1]
                host_name = v[2] 
                host_id = v[3] 
                trigger_id = k
                trigger_desc = v[4] 
                trigger_lastchange = v[5]
                event_id = r["acknowledges"][0]["eventid"].encode('utf-8')
                ack = []
                for m in r["acknowledges"]:
                    ack_user = m["name"].encode('utf-8')
                    ack_msg = m["message"].encode('utf-8')
                    ack_clock = int(m["clock"].encode('utf-8'))
                    ack_clock = time.strftime('%Y-%m-%d %H:%M',time.localtime(ack_clock))
                    ack.append([ack_clock, ack_user, ack_msg])

                trigger_and_host_with_event[trigger_id] = [group_name, group_id, host_name, host_id, trigger_desc, trigger_lastchange, event_id, ack]
            result.close()
                #print trigger_and_host_with_event[trigger_id][7][0][0]

        else:
        #有event但无ack的trigger，"acknowledged"为0
            trigger_and_host_with_event_json = json.dumps({
                "jsonrpc": "2.0",
                "method": "event.get",
                "params": {
                    "output": "extend",
                    "objectids": k,
                    "sortfield": ["clock", "eventid"],
                    "sortorder": "DESC",
                    "limit" : 1
                    },
                "auth": session,
                "id": 1})
    
            result = StringIO.StringIO()
            curl.setopt(pycurl.POSTFIELDS,trigger_and_host_with_event_json)
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
    
            if json.loads(result.getvalue())['result']:
                for r in json.loads(result.getvalue())['result']:
                    group_name = v[0]
                    group_id = v[1]
                    host_name = v[2] 
                    host_id = v[3] 
                    trigger_id = k
                    trigger_desc = v[4] 
                    trigger_lastchange = v[5]
                    event_id = r["eventid"].encode('utf-8')
                    ack = ["0"]
                    trigger_and_host_with_event[trigger_id] = [group_name, group_id, host_name, host_id, trigger_desc, trigger_lastchange, event_id, ack]
                    #print trigger_and_host_with_event[trigger_id]
                result.close()

            else:
            #无event的trigger
                    group_name = v[0]
                    group_id = v[1]
                    host_name = v[2] 
                    host_id = v[3] 
                    trigger_id = k
                    trigger_desc = v[4] 
                    trigger_lastchange = v[5]
                    event_id = "0"
                    ack = ["0"]
                    trigger_and_host_with_event[trigger_id] = [group_name, group_id, host_name, host_id, trigger_desc, trigger_lastchange, event_id, ack]
                    #print trigger_and_host_with_event[trigger_id]

    return trigger_and_host_with_event


def discovered_hosts():
    get_groupid_json = json.dumps({
        "jsonrpc": "2.0",
        "method": "hostgroup.get",
        "params": {
            "output": "extend",
            "filter":{
                "name": "Discovered hosts",
                }
            },
        "auth": session,
        "id": 1})

    result = StringIO.StringIO()
    curl.setopt(pycurl.POSTFIELDS,get_groupid_json)
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

    discovered_hosts_groupid = json.loads(result.getvalue())["result"][0]["groupid"]
    #print discovered_hosts_groupid
    result.close()

    discovered_hosts_json = json.dumps({
        "jsonrpc": "2.0",
        "method": "host.get",
        "params": {
            "groupids": discovered_hosts_groupid,
            "selectGroups": ["name"],
            "selectInterfaces": ["ip"],
            "output": ["hostid","host","interfaces","groups"]
            },
        "auth": session,
        "id": 1})

    result = StringIO.StringIO()
    curl.setopt(pycurl.POSTFIELDS,discovered_hosts_json)
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

    discovered_hosts_list = {}
    for i in json.loads(result.getvalue())["result"]:
        host_id = i["hostid"].encode('utf-8')
        host_name = i["host"].encode('utf-8')
        ipaddr = i["interfaces"][0]["ip"].encode('utf-8')
        group_name = []
        for g in i["groups"]:
            group_msg = g["name"].encode('utf-8')
            group_name.append(group_msg)
        discovered_hosts_list[host_id]=[host_name, ipaddr, group_name]
    #print discovered_hosts_list
    result.close()

    return discovered_hosts_list


def format_output():

    logfile_time =  time.strftime('%Y-%m-%d',time.localtime())
    ops_daily_dir = '/root/zhangshaobing/scripts/zabbix/ops_daily/'
    ops_daily_file = ops_daily_dir + 'ops_daily_%s.html' % logfile_time
    if os.path.exists(ops_daily_dir):
        pass
    else:
        os.makedirs(ops_daily_dir)

    ops_daily = trigger_and_host_with_event()
    #print type(ops_daily)

    css_table.css_table_style(ops_daily_file)
    css_table.html_start(ops_daily_file)

    count = 0
    css_table.event_ack_table_start(ops_daily_file)
    for k,v in sorted(ops_daily.items(), lambda x, y: cmp(x[1], y[1])):
        #print k,v[0],v[1],v[2],v[3]
        #dict = {"trigger_id":k, "group_name":v[0], "host_name":v[1], "trigger":v[2], "lastchange":v[3]}
        group_name = v[0]
        group_id = v[1]
        host_name = v[2] 
        host_id = v[3] 
        trigger_id = k
        trigger_desc = v[4] 
        trigger_lastchange = v[5]
        event_id = v[6]
        ack = ""
        for i in v[7]:
            ack = ack + (' ').join(i) + '<br>'

        if int(event_id) > 1 and len(ack) > 10:
            count = count + 1
            #row = [group_name, host_name, trigger_desc, trigger_lastchange, trigger_id]
            row = [group_name, host_name, trigger_desc, trigger_lastchange, trigger_id, event_id, ack]
            #print (' ').join(row)
            css_table.table_rows(ops_daily_file,count,row)
    css_table.table_end(ops_daily_file)

    count = 0
    css_table.event_noack_table_start(ops_daily_file)
    for k,v in sorted(ops_daily.items(), lambda x, y: cmp(x[1], y[1])):
        #print k,v[0],v[1],v[2],v[3]
        #dict = {"trigger_id":k, "group_name":v[0], "host_name":v[1], "trigger":v[2], "lastchange":v[3]}
        group_name = v[0]
        group_id = v[1]
        host_name = v[2] 
        host_id = v[3] 
        trigger_id = k
        trigger_desc = v[4] 
        trigger_lastchange = v[5]
        event_id = v[6]
        ack = ""
        for i in v[7]:
            ack = ack + (' ').join(i) + '<br>'

        if int(event_id) > 1 and len(ack) < 10:
            count = count + 1
            #row = [group_name, host_name, trigger_desc, trigger_lastchange, trigger_id]
            row = [group_name, host_name, trigger_desc, trigger_lastchange, trigger_id, event_id, ack]
            #print (' ').join(row)
            css_table.table_rows(ops_daily_file,count,row)
    css_table.table_end(ops_daily_file)

    count = 0
    css_table.noevent_table_start(ops_daily_file)
    for k,v in sorted(ops_daily.items(), lambda x, y: cmp(x[1], y[1])):
        #print k,v[0],v[1],v[2],v[3]
        #dict = {"trigger_id":k, "group_name":v[0], "host_name":v[1], "trigger":v[2], "lastchange":v[3]}
        group_name = v[0]
        group_id = v[1]
        host_name = v[2] 
        host_id = v[3] 
        trigger_id = k
        trigger_desc = v[4] 
        trigger_lastchange = v[5]
        event_id = v[6]
        ack = ""
        for i in v[7]:
            ack = ack + (' ').join(i) + '<br>'

        if int(event_id) == 0:
            count = count + 1
            #row = [group_name, host_name, trigger_desc, trigger_lastchange, trigger_id]
            row = [group_name, host_name, trigger_desc, trigger_lastchange, trigger_id, event_id, ack]
            #print (' ').join(row)
            css_table.table_rows(ops_daily_file,count,row)
    css_table.table_end(ops_daily_file)

    discovered_hosts_list = discovered_hosts() 
    count = 0
    css_table.discovered_host_table_start(ops_daily_file)
    for k,v in sorted(discovered_hosts_list.items(), lambda x, y: cmp(x[1], y[1])):
        host_id = k
        host_name = v[0] 
        ipaddr = v[1]
        group_name = ""
        for i in v[2]:
            group_name = group_name + i + '<br>'

        count = count + 1
        row = [host_id, host_name,ipaddr,group_name] 
        #print (' ').join(row)
        css_table.discovered_host_table_rows(ops_daily_file,count,row)
    css_table.table_end(ops_daily_file)

    css_table.html_end(ops_daily_file)

    maillist = 'nf_xxbywb@mail.nfsq.com.cn'
    #maillist = 'sbzhang5@mail.yst.com.cn'
    send_message.send_message(maillist,ops_daily_file)


if __name__ == '__main__':
    #trigger_get_monitored()
    #host_get_with_monitored_triggers()
    #trigger_and_host_with_event()
    #discovered_hosts()
    format_output()

