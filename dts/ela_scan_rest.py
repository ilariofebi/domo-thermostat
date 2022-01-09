from bluepy.btle import Scanner, DefaultDelegate, BTLEDisconnectError
from ela.bluetooth.advertising.TagFactory import Tagfactory
from ela.bluetooth.advertising.TagBase import TagBase
from datetime import datetime
import binascii
import json
import requests
from model.proto import RetMsg
from pathlib import Path
from configparser import ConfigParser

debug = False


def dprint(*x):
    if debug:
        print(x)


def parse(dev):
    if (isinstance(dev.rawData, bytes)):

        out = {}
        data = Tagfactory.getInstance().getTag(dev.rawData).formattedDataSensor
        dprint(dev.rawData)
        if data != 'VOID':
            dt = datetime.now().astimezone().isoformat()
            out = {'dt': dt, 'mac_addr': dev.addr, 'rssi': dev.rssi}

            dprint("Device %s (%s), RSSI=%d dB, Interpreted ELA Data=%s, RawData=%s"
                   % (dev.addr,
                      dev.addrType,
                      dev.rssi,
                      data,
                      binascii.b2a_hex(dev.rawData).decode('ascii'))
                   )
            if 'state=' in data:
                info = int(data.split('=')[-1])
                out['category'] = 'state_count'
                out['value'] = info
                state = info % 2
                count = info // 2
                dprint(f'{datetime.now()} stato:{state}, count:{count}')
            elif 'T=' in data:
                out['category'] = 'temperature'
                out['value'] = float(data.split('=')[-1].strip())

                dprint(f'{datetime.now()} {out["category"]}:{out["value"]}')

            for (adtype, desc, value) in dev.getScanData():
                if adtype == 9:
                    out['cn'] = value  # Complete name
                dprint("[%s]  %s = %s" % (adtype, desc, value))

            return _post('ela_insert', out)


def _read_config():
    config_file = f'./config.ini'
    config = ConfigParser()
    config.read(config_file)
    return config

def _post(path, jdata):
    config = _read_config()
    base_url = config['backend'].get('backend_url')
    r = requests.post(f'{base_url}/{path}', json=jdata)
    if r.status_code == 200:
        ret = r.json()
        return RetMsg(**ret)
    else:
        return RetMsg(err=True, msg='Connection Error')


class ScanDelegate(DefaultDelegate):
    def __init__(self):
        DefaultDelegate.__init__(self)

    def handleDiscovery(self, dev, isNewDev, isNewData):
        if isNewDev or isNewData:
            print(parse(dev))


scanner = Scanner().withDelegate(ScanDelegate())

for _ in range(1):
    # while True:
    print('new scan')
    try:
        scanner.scan(10)
    except BTLEDisconnectError as e:
        print(f'tento reconnect, {e}')
        scanner = Scanner().withDelegate(ScanDelegate())


