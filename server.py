import sqlite3

from bottle import route, run, template, install, static_file
from bottle_sqlite import SQLitePlugin
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import os
from collections import defaultdict
import matplotlib
import yaml

install(SQLitePlugin(dbfile='./usage.db'))

cfg = yaml.load(open('config.yaml').read())

#http://code.activestate.com/recipes/577081-humanized-representation-of-a-number-of-bytes/
#with a fix for correctly depicting float values
def humanize_bytes(bytes, precision=1):
    """Return a humanized string representation of a number of bytes.

    Assumes `from __future__ import division`.

    >>> humanize_bytes(1)
    '1 byte'
    >>> humanize_bytes(1024)
    '1.0 kB'
    >>> humanize_bytes(1024*123)
    '123.0 kB'
    >>> humanize_bytes(1024*12342)
    '12.1 MB'
    >>> humanize_bytes(1024*12342,2)
    '12.05 MB'
    >>> humanize_bytes(1024*1234,2)
    '1.21 MB'
    >>> humanize_bytes(1024*1234*1111,2)
    '1.31 GB'
    >>> humanize_bytes(1024*1234*1111,1)
    '1.3 GB'
    """
    abbrevs = (
        (1<<50L, 'PB'),
        (1<<40L, 'TB'),
        (1<<30L, 'GB'),
        (1<<20L, 'MB'),
        (1<<10L, 'kB'),
        (1, 'bytes')
    )
    if bytes == 1:
        return '1 byte'
    for factor, suffix in abbrevs:
        if bytes >= factor:
            break
    return '%.*f %s' % (precision, bytes / float(factor), suffix)

@route('/')
@route('/<ago:int>/')
def index(db, ago=0):
    now = datetime.now()
    target_date = now - timedelta(days=ago)
    if target_date.day > cfg['start_cycle_day']:
        from_date = "{year:04d}-{month:02d}-{day:02d}".format(
            year=target_date.year, month=target_date.month, day=11)
    else:
        from_date = "{year:04d}-{month:02d}-{day:02d}".format(
            year=target_date.year, month=target_date.month - 1, day=11)
    sql = '''SELECT tx, rx, ts FROM usage_log WHERE
        ts > datetime("{from_date}", "start of day") AND
        ts <= datetime('now', 'localtime', '-{ago} day')
        '''.format(from_date=from_date, ago=ago)
    c = db.execute(sql)
    prevtx = 0
    prevrx = 0
    totaltx, totalrx = (0, 0)
    for row in c:
        if prevtx == 0:
            valtx = 0
        elif row[0] < prevtx:
            valtx = row[0]
        else:
            valtx = row[0] - prevtx

        if prevrx == 0:
            valrx = 0
        elif row[1] < prevrx:
            valrx = row[1]
        else:
            valrx = row[1] - prevrx
        prevtx = row[0]
        prevrx = row[1]
        totaltx += valtx
        totalrx += valrx
    checkprev = db.execute("""
        SELECT count(*) FROM usage_log
            WHERE ts < datetime('%s', 'start of day')
        """ % (target_date.strftime("%Y-%m-%d")))
    cp = checkprev.fetchone()
    if cp[0] == 0:
        is_prev = False
    else:
        is_prev = True
    
    checknext = db.execute("""
        SELECT count(*) FROM usage_log
            WHERE ts > datetime('%s', 'start of day', '+1 day')
        """ % (target_date.strftime("%Y-%m-%d")))
    if checknext.fetchone()[0] == 0:
        is_next = False
    else:
        is_next = True
    return template('show_index', for_date=target_date, 
        from_date=from_date, 
        totaltx=humanize_bytes(totaltx, precision=3), 
        totalrx=humanize_bytes(totalrx, precision=3),
        total=humanize_bytes(totaltx + totalrx, precision=3),
        is_prev=is_prev,
        is_next=is_next,
        ago=ago
        )


@route('/usage')
@route('/usage/')
@route('/usage/<ago:int>')
def usage(db, ago=0):
    now = datetime.now()
    target_date = now - timedelta(days=ago)
    target_midnight = datetime(target_date.year, target_date.month, target_date.day, 0, 0, 0)
    target_end = datetime(target_date.year, target_date.month, target_date.day,
    23, 59, 59)
    c = db.execute('''SELECT * FROM usage_log
        WHERE ts > ? AND ts < ?
    ''', (target_midnight, target_end))
    data = c.fetchall()
    return template('show_usage', data=data)

@route('/debug/<year:int>/<month:int>/<day:int>')
def debug(db, year, month, day):
    usagetx = defaultdict(int)
    usagerx = defaultdict(int)
    for i in range(24):
        usagetx[i] = 0
        usagerx[i] = 0
    pc = db.execute('''
        SELECT tx, rx FROM usage_log WHERE
        ts < datetime('%d-%02d-%02d', 'start of day')
        LIMIT 1
        ''' % (year, month, day))
    try:
        prevtx, prevrx = pc.fetchone()
    except TypeError:
        print "error getting prev rx,tx"
        prevtx, prevrx = (0, 0)

    c = db.execute('''
        SELECT ts, strftime('%%H', ts), tx, rx FROM usage_log
        WHERE ts >= datetime('%d-%02d-%02d', 'start of day') AND
            ts <= datetime('%d-%02d-%02d', 'start of day', '+24 hour', '-1 second')
    ''' % (year, month, day, year, month, day))

    for row in c:
        if prevtx == 0:
            valtx = 0
        elif row[2] < prevtx:
            valtx = row[2]
        else:
            valtx = row[2] - prevtx
        if prevrx == 0:
            valrx = 0
        elif row[3] < prevrx:
            valrx = row[3]
        else:
            valrx = row[3] - prevrx

        usagetx[int(row[1])] += valtx
        usagerx[int(row[1])] += valrx
        prevtx = row[2]
        prevrx = row[3]

    return template('show_debug', tx=usagetx, rx=usagerx)
    
@route('/img/plot/<year:int>/<month:int>/<day:int>.png')
def plot(db, year, month, day):
    filename = '{0}/{1}/{2}.png'.format(year, month, day)
    #if not os.path.exists(os.path.join('static', filename)):
    try:
        os.makedirs(os.path.dirname(os.path.join('static', filename)))
    except OSError:
        pass
    fig = plt.figure(figsize=(8., 5.))
    plot = fig.add_subplot(111)
    plot.set_ylabel('Bytes')
    plot.set_xlabel('Hour')
    usagetx = defaultdict(int)
    usagerx = defaultdict(int)
    #http://stackoverflow.com/a/7039989/203454
    ax = plt.gca()
    mkfunc = lambda x, pos: '%1.1fM' % (x * 1e-6) if x >= 1e6 else '%1.1fK' % (x * 1e-3) if x >= 1e3 else '%1.1f' % x
    mkformatter = matplotlib.ticker.FuncFormatter(mkfunc)
    ax.yaxis.set_major_formatter(mkformatter)
    for i in range(24):
        usagetx[i] = 0
        usagerx[i] = 0
    pc = db.execute('''
        SELECT tx, rx FROM usage_log WHERE
        ts < datetime('%d-%02d-%02d', 'start of day')
        ORDER BY ts DESC
        LIMIT 1
        ''' % (year, month, day))
    try:
        prevtx, prevrx = pc.fetchone()
    except TypeError:
        print "error getting prev rx,tx"
        prevtx, prevrx = (0, 0)

    c = db.execute('''
        SELECT ts, strftime('%%H', ts), tx, rx FROM usage_log
        WHERE ts >= datetime('%d-%02d-%02d', 'start of day') AND
            ts <= datetime('%d-%02d-%02d', 'start of day', '+24 hour', '-1 second')
    ''' % (year, month, day, year, month, day))

    for row in c:
        if prevtx == 0:
            valtx = 0
        elif row[2] < prevtx:
            valtx = row[2]
        else:
            valtx = row[2] - prevtx
        if prevrx == 0:
            valrx = 0
        elif row[3] < prevrx:
            valrx = row[3]
        else:
            valrx = row[3] - prevrx

        usagetx[int(row[1])] += valtx
        usagerx[int(row[1])] += valrx
        prevtx = row[2]
        prevrx = row[3]
        
    plot.bar(range(24), usagerx.values(), facecolor='#3322ff', edgecolor='white')
    plot.bar(range(24), usagetx.values(), facecolor='#aabbcc', edgecolor='white')
    totaltx = sum(usagetx.values())
    totalrx = sum(usagerx.values())
    fig.text(0.75, 0.98, "Tx: %s" % humanize_bytes(totaltx, precision=3), 
        fontsize=9, color='black')
    fig.text(0.75, 0.95, "Rx: %s" % humanize_bytes(totalrx, precision=3), 
        fontsize=9, color='black')
    fig.text(0.75, 0.92, "Total: %s" % humanize_bytes(totalrx + totaltx, precision=3), 
        fontsize=10, color='black')
    fig.text(0.45, 0.95, "{year}-{month:02d}-{day:02d}".format(
        year=year, month=month, day=day))
    fig.savefig(os.path.join('static',filename))            

    return static_file(filename, root='static')

run(host=cfg['server_addr'], port=cfg['server_port'], reloader=True)

