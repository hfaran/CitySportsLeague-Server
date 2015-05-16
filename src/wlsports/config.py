from collections import namedtuple


Config = namedtuple(
    'Config',
    ['port', 'db_file', 'session_timeout_days', 'cookie_secret', 'debug']
)
