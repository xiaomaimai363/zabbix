#!/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import time
import smtplib
import json
from email.mime.text import MIMEText

now =  time.strftime('%Y-%m-%d',time.localtime(time.time()-86400))

def send_message(maillist,errorlog_file):
    HOST = 'mail.yst.com.cn'
    SUBJECT = '运维日报 %s' % now
    #TO = '; '.join(maillist)
    TO = maillist
    #log_record.logging.info(TO)
    FROM = 'altermonitor@mail.yst.com.cn'
    with open(errorlog_file,'r') as f:
        text = ''.join(f.readlines())

    msg = MIMEText(text,"html","utf-8")
    msg['Subject'] = SUBJECT
    msg['From'] = FROM
    msg['To'] = TO

    try:    
        server = smtplib.SMTP()
        server.connect(HOST,"25")
        server.starttls()
        #server.login("altermonitor@mail.yst.com.cn","nf123456!")
        server.login("altermonitor","nf123456!")
        server.sendmail(FROM, TO, msg.as_string())
        server.quit()
    except Exception,e:
        print "send massage error: %s" % e


if __name__ == '__main__':
    maillist = ['sbzhang5@mail.yst.com.cn']
    send_message(maillist,'/root/zhangshaobing/scripts/zabbix/ops_daily/ops_daily_2015-09-11.txt')
