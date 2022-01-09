import os, sys
import time

from flask import Flask, request
import logging
import sqlite3
from collections import namedtuple
from configparser import ConfigParser
from model.metric import ElaMetric
from model.proto import RetMsg
import dsnparse

config_file = f'./config.ini'
config = ConfigParser()
config.read(config_file)

conn = sqlite3.connect(config['db'].get('db_file'))

app = Flask(__name__)

def sql_exec(sql, data):
    try:
        with sqlite3.connect(config['db'].get('db_file')) as con:
            cur = con.cursor()
            cur.execute(sql, data)
            con.commit()
            ret = RetMsg(msg="Record successfully added")
    except:
        con.rollback()
        ret = RetMsg(msg="error in insert operation", err=True)

    finally:
        con.close()
    return ret

def _resp(res: RetMsg) -> dict:
    if res.err:
        logging.error(res.msg)
    if res.warn:
        logging.warning(res.msg)
    return res.dict()

@app.post("/ela_insert")
def ela_insert():
    logging.debug(request.json)
    metric = ElaMetric(**request.json)

    sql_prepare = metric.sql_insert('ela_metrics')
    ret = sql_exec(sql_prepare.sql, sql_prepare.data)
    return _resp(ret)

def main():
    url = config['backend'].get('backend_url')
    dsn = dsnparse.parse(url)
    app.run(debug=True, host=dsn.host, port=dsn.port)

if __name__ == '__main__':
    main()
