#!/usr/bin/env python
import urllib2, base64
import lxml.html as lh
import sqlite3
from datetime import datetime
import os

ROUTER_ADDR = '192.168.1.1'
ROUTER_ADMIN = 'admin'
ROUTER_PWD = 'admin'
RXTX_PATH = '/statswan.cmd'
TX_XPATH = './/tr[3]/td[9]'
RX_XPATH = './/tr[3]/td[5]'

BASE = os.path.abspath(os.path.dirname(__file__))

passman = urllib2.HTTPPasswordMgrWithDefaultRealm()
passman.add_password(None, 'http://%s/' % ROUTER_ADDR, ROUTER_ADMIN, ROUTER_PWD)
urllib2.install_opener(urllib2.build_opener(urllib2.HTTPBasicAuthHandler(passman)))

req = urllib2.Request('http://%s%s' % (ROUTER_ADDR, RXTX_PATH))
content = urllib2.urlopen(req).read()
doc = lh.fromstring(content)

tx = doc.xpath(TX_XPATH)[0].text_content()
rx = doc.xpath(RX_XPATH)[0].text_content()

conn = sqlite3.connect(os.path.join(BASE, 'usage.db'))

c = conn.cursor()

c.execute('SELECT count(*) FROM sqlite_master WHERE type="table" AND name="usage_log"')
if c.fetchone()[0] == 0:
    c.execute("""
        CREATE TABLE usage_log (
            ts datetime,
            tx number,
            rx number)
        """)
    conn.commit()

c.execute("""
    INSERT INTO usage_log
    VALUES
    (?, ?, ?)
    """, (datetime.now(), tx, rx))

conn.commit()
