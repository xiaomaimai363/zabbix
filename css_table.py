#!/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import time
import json


def css_table_style(htmlfile):
    css = """
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN""http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
<title>CSS Tables</title>
<link href="styles.css" mce_href="styles.css" rel="stylesheet" type="text/css" />
</head>
<mce:style type="text/css"><!--
/* CSS Document */
body {
 font: normal 11px auto "Trebuchet MS", Verdana, Arial, Helvetica, sans-serif;
 color: #4f6b72;
 background: #E6EAE9;
}
a {
 color: #c75f3e;
}
#mytable {
 width: 1200px;
 padding: 0;
 margin: 0;
}
caption {
 padding: 0 0 5px 0;
 width: 1200px; 
 font: italic 11px "Trebuchet MS", Verdana, Arial, Helvetica, sans-serif;
 text-align: right;
}
th {
 font: bold 11px "Trebuchet MS", Verdana, Arial, Helvetica, sans-serif;
 color: #4f6b72;
 border-right: 1px solid #C1DAD7;
 border-bottom: 1px solid #C1DAD7;
 border-top: 1px solid #C1DAD7;
 letter-spacing: 2px;
 text-transform: uppercase;
 text-align: left;
 padding: 6px 6px 6px 12px;
 background: #CAE8EA url(images/bg_header.jpg) no-repeat;
}
th.nobg {
 border-top: 0;
 border-left: 0;
 border-right: 1px solid #C1DAD7;
 background: none;
}
td {
 border-right: 1px solid #C1DAD7;
 border-bottom: 1px solid #C1DAD7;
 background: #fff;
 font-size:11px;
 padding: 6px 6px 6px 12px;
 color: #4f6b72;
}

td.alt {
 background: #F5FAFA;
 color: #797268;
}
th.spec {
 border-left: 1px solid #C1DAD7;
 border-top: 0;
 background: #fff url(images/bullet1.gif) no-repeat;
 font: bold 10px "Trebuchet MS", Verdana, Arial, Helvetica, sans-serif;
}
th.specalt {
 border-left: 1px solid #C1DAD7;
 border-top: 0;
 background: #f5fafa url(images/bullet2.gif) no-repeat;
 font: bold 10px "Trebuchet MS", Verdana, Arial, Helvetica, sans-serif;
 color: #797268;
}
/*---------for IE 5.x bug*/
html>body td{ font-size:11px;}
--></mce:style><style type="text/css" mce_bogus="1">/* CSS Document */
body {
 font: normal 11px auto "Trebuchet MS", Verdana, Arial, Helvetica, sans-serif;
 color: #4f6b72;
 background: #E6EAE9;
}
a {
 color: #c75f3e;
}
#mytable {
 width: 1200px;
 padding: 0;
 margin: 0;
}
caption {
 padding: 0 0 5px 0;
 width: 1200px; 
 font: italic 11px "Trebuchet MS", Verdana, Arial, Helvetica, sans-serif;
 text-align: right;
}
th {
 font: bold 11px "Trebuchet MS", Verdana, Arial, Helvetica, sans-serif;
 color: #4f6b72;
 border-right: 1px solid #C1DAD7;
 border-bottom: 1px solid #C1DAD7;
 border-top: 1px solid #C1DAD7;
 letter-spacing: 2px;
 text-transform: uppercase;
 text-align: left;
 padding: 6px 6px 6px 12px;
 background: #CAE8EA url(images/bg_header.jpg) no-repeat;
}
th.nobg {
 border-top: 0;
 border-left: 0;
 border-right: 1px solid #C1DAD7;
 background: none;
}
td {
 border-right: 1px solid #C1DAD7;
 border-bottom: 1px solid #C1DAD7;
 background: #fff;
 font-size:11px;
 padding: 6px 6px 6px 12px;
 color: #4f6b72;
}

td.alt {
 background: #F5FAFA;
 color: #797268;
}
th.spec {
 border-left: 1px solid #C1DAD7;
 border-top: 0;
 background: #fff url(images/bullet1.gif) no-repeat;
 font: bold 10px "Trebuchet MS", Verdana, Arial, Helvetica, sans-serif;
}
th.specalt {
 border-left: 1px solid #C1DAD7;
 border-top: 0;
 background: #f5fafa url(images/bullet2.gif) no-repeat;
 font: bold 10px "Trebuchet MS", Verdana, Arial, Helvetica, sans-serif;
 color: #797268;
}
/*---------for IE 5.x bug*/
"""

    with open(htmlfile,'w') as f:
        f.write(css)


def html_start(htmlfile):
    html_start = """
<html>body td{ font-size:11px;}</style>
<body>
"""

    with open(htmlfile,"a+") as f:
        f.write(html_start)


def event_ack_table_start(htmlfile):
    table_start = """
<H2>有处理进度的报警</H2>
<table id="mytable" cellspacing="0" summary="OPS Daily">
<caption> </caption>
<tr>
    <th scope="col" abbr="group_name">group_name</th>
    <th scope="col" abbr="host_name">host_name</th>
    <th scope="col" abbr="trigger">trigger</th>
    <th scope="col" abbr="lastchange">lastchange</th>
    <th scope="col" abbr="trigger_id">trigger_id</th>
    <th scope="col" abbr="event_id">event_id</th>
    <th scope="col" abbr="acknowledges">acknowledges</th>
</tr>
"""

    with open(htmlfile,"a+") as f:
        f.write(table_start)


def event_noack_table_start(htmlfile):
    table_start = """
<H2>无ack汇报处理进度的报警</H2>
<table id="mytable" cellspacing="0" summary="OPS Daily">
<caption> </caption>
<tr>
    <th scope="col" abbr="group_name">group_name</th>
    <th scope="col" abbr="host_name">host_name</th>
    <th scope="col" abbr="trigger">trigger</th>
    <th scope="col" abbr="lastchange">lastchange</th>
    <th scope="col" abbr="trigger_id">trigger_id</th>
    <th scope="col" abbr="event_id">event_id</th>
    <th scope="col" abbr="acknowledges">acknowledges</th>
</tr>
"""

    with open(htmlfile,"a+") as f:
        f.write(table_start)


def noevent_table_start(htmlfile):
    table_start = """
<H2>无负责人的报警</H2>
<table id="mytable" cellspacing="0" summary="OPS Daily">
<caption> </caption>
<tr>
    <th scope="col" abbr="group_name">group_name</th>
    <th scope="col" abbr="host_name">host_name</th>
    <th scope="col" abbr="trigger">trigger</th>
    <th scope="col" abbr="lastchange">lastchange</th>
    <th scope="col" abbr="trigger_id">trigger_id</th>
    <th scope="col" abbr="event_id">event_id</th>
    <th scope="col" abbr="acknowledges">acknowledges</th>
</tr>
"""

    with open(htmlfile,"a+") as f:
        f.write(table_start)


def table_rows(htmlfile,count,row):
    if count % 2 != 0:
        msg = """
<tr>
    <td>%s</td>
    <td>%s</td>
    <td>%s</td>
    <td>%s</td>
    <td>%s</td>
    <td>%s</td>
    <td>%s</td>
</tr>
""" % (row[0], row[1], row[2], row[3], row[4], row[5], row[6])

        with open(htmlfile,"a+") as f:
            f.write(msg)
    else:
        msg = """
<tr>
    <td class="alt">%s</td>
    <td class="alt">%s</td>
    <td class="alt">%s</td>
    <td class="alt">%s</td>
    <td class="alt">%s</td>
    <td class="alt">%s</td>
    <td class="alt">%s</td>
</tr>
""" % (row[0], row[1], row[2], row[3], row[4], row[5], row[6])

        with open(htmlfile,"a+") as f:
            f.write(msg)


def discovered_host_table_start(htmlfile):
    table_start = """
<H2>Discovered hosts组未分配的主机</H2>
<table id="mytable" cellspacing="0" summary="OPS Daily">
<caption> </caption>
<tr>
    <th scope="col" abbr="host_id">host_id</th>
    <th scope="col" abbr="host_name">host_name</th>
    <th scope="col" abbr="ipaddr">ipaddr</th>
    <th scope="col" abbr="groups">groups</th>
</tr>
"""

    with open(htmlfile,"a+") as f:
        f.write(table_start)


def discovered_host_table_rows(htmlfile,count,row):
    if count % 2 != 0:
        msg = """
<tr>
    <td>%s</td>
    <td>%s</td>
    <td>%s</td>
    <td>%s</td>
</tr>
""" % (row[0], row[1], row[2], row[3])

        with open(htmlfile,"a+") as f:
            f.write(msg)
    else:
        msg = """
<tr>
    <td class="alt">%s</td>
    <td class="alt">%s</td>
    <td class="alt">%s</td>
    <td class="alt">%s</td>
</tr>
""" % (row[0], row[1], row[2], row[3])

        with open(htmlfile,"a+") as f:
            f.write(msg)


def table_end(htmlfile):
    table_end = """
</table>
"""
    with open(htmlfile,"a+") as f:
        f.write(table_end)


def html_end(htmlfile):
    html_end = """
</table>
</body>
</html> 
"""
    with open(htmlfile,"a+") as f:
        f.write(html_end)


if __name__ == "__main__":       
    css_table_style('htmlfile')
