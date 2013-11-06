#!/usr/bin/env python
import urllib2, base64
import lxml.html as lh
import sqlite3
from datetime import datetime

TX_XPATH = './/tr[3]/td[9]'
RX_XPATH = './/tr[3]/td[5]'

passman = urllib2.HTTPPasswordMgrWithDefaultRealm()
passman.add_password(None, 'http://192.168.1.1/', 'admin', 'admin')
urllib2.install_opener(urllib2.build_opener(urllib2.HTTPBasicAuthHandler(passman)))

req = urllib2.Request('http://192.168.1.1/statswan.cmd')
content = urllib2.urlopen(req).read()
doc = lh.fromstring(content)

tx = doc.xpath(TX_XPATH)[0].text_content()
rx = doc.xpath(RX_XPATH)[0].text_content()

conn = sqlite3.connect('/home/arun/Projects/router-monitor/usage.db')

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
