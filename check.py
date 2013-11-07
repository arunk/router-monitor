#!/usr/bin/env python
import urllib2, base64
import lxml.html as lh
import sqlite3
from datetime import datetime
import os
import yaml

cfg = yaml.load(open('config.yaml').read())

ROUTER_ADDR = cfg['router_addr']
ROUTER_USER = cfg['router_user']
ROUTER_PWD = cfg['router_password']
ROUTER_RXTX_PATH = cfg['router_rxtx_path']
TX_XPATH = cfg['tx_xpath']
RX_XPATH = cfg['rx_xpath']

BASE = os.path.abspath(os.path.dirname(__file__))

passman = urllib2.HTTPPasswordMgrWithDefaultRealm()
passman.add_password(None, 'http://%s/' % ROUTER_ADDR, ROUTER_USER, ROUTER_PWD)
urllib2.install_opener(urllib2.build_opener(urllib2.HTTPBasicAuthHandler(passman)))

req = urllib2.Request('http://%s/%s' % (ROUTER_ADDR, ROUTER_RXTX_PATH))
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
