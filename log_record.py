#!/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import tab
import time
import logging

logfile_time =  time.strftime('%Y-%m-%d',time.localtime())
applog_dir = '/root/zhangshaobing/scripts/zabbix/applog/'
applog = applog_dir + 'applog_%s' % logfile_time
if os.path.exists(applog_dir):
    pass
else:
    os.makedirs(applog_dir)

logging.basicConfig(filename = applog,
                    filemode = 'a',
                    level = logging.INFO,
                    format = '%(asctime)s %(levelname)s %(filename)s:%(lineno)d %(funcName)s %(message)s',
                    datefmt = '%Y-%m-%d %H:%M',
                    )

if __name__ == '__main__':
    logging.warn('this is a test logging')
