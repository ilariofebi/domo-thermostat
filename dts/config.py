from pathlib import Path
from configparser import ConfigParser

config_file = f'./config.ini'

if not Path(config_file).is_file():
    config = ConfigParser()
    config['backend'] = {
        'backend_url': 'http://127.0.0.1:5000/',
    }
    config['db'] = {
        'db_file': './db.sqlite',
    }
    with open(config_file, 'w') as output_file:
        config.write(output_file)