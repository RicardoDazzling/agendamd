import os
import logging
from time import mktime

import numpy as np

from typing import Optional, Union, Literal
from datetime import datetime, timedelta, date

from Cryptodome.Cipher import AES
from Cryptodome.Hash import MD5


def read_numpy(path):
    if os.path.exists(path):
        with open(path, 'rb') as file:
            return np.load(file)  # ['name', 'email', 'password']
    return None


def md5_hash(string: str) -> bytes:
    return MD5.new(string.encode("utf-8")).digest()


def encrypt(filepath: str, key: bytes, iv: bytes, remove_npy: bool = True) -> str:
    __enfile = filepath + ".amc"
    __aes = AES.new(key, AES.MODE_CFB, iv=iv)

    with open(filepath, 'rb') as file:
        __file_val = file.read()
    if remove_npy:
        os.remove(filepath)

    __enfile_val = __aes.encrypt(__file_val)

    with open(__enfile, 'wb') as file:
        file.write(__enfile_val)

    return __enfile


def decrypt(en_filepath: str, key: bytes, iv: bytes, remove_amc: bool = False) -> str:
    __file = en_filepath.replace('.amc', '')
    __aes = AES.new(key, AES.MODE_CFB, iv=iv)

    with open(en_filepath, 'rb') as file:
        __enfile_val = file.read()
    if remove_amc:
        os.remove(en_filepath)

    __file_val = __aes.decrypt(__enfile_val)

    with open(__file, 'wb') as file:
        file.write(__file_val)

    return __file


def log(self, message: str, log_type: Literal['error', 'info', 'warning'] = 'error'):
    name = self if isinstance(self, str) else self.__class__.__name__
    if log_type == 'error':
        logging.error(f'{name}: {message}', exc_info=True)
    elif log_type == 'info':
        logging.info(f'{name}: {message}')
    elif log_type == 'warning':
        logging.warning(f'{name}: {message}')


def array_size(integer: int) -> Literal["B", "H", "I", "L"]:
    if integer < 0:
        raise ValueError("Integer out of range for unsigned numpy data type.")
    elif integer < 256:
        return "B"
    elif integer < 65_536:
        return "H"
    elif integer < 4_294_967_295:
        return "I"
    elif integer < 18_446_744_073_709_551_615:
        return "L"
    else:
        raise ValueError("Too longer integer.")


def get_datestamp_from_date(date_object: date) -> int:
    return int(mktime(date_object.timetuple())) // 86400


def get_date_from_datestamp(datestamp: int) -> date:
    return date.fromtimestamp(datestamp * 86400)


def get_timestamp(datetime_var: Optional[datetime] = None) -> int:
    if datetime_var is None:
        datetime_var = datetime.now()
    _1970 = datetime(1970, 1, 1, 0, 0, 0)
    td = datetime_var - _1970
    days = td.days
    minutes, second = divmod(td.seconds, 60)
    timestamp = days * 1440 + minutes
    return int(timestamp)


def get_datetime(timestamp: int) -> datetime:
    days, remainder = divmod(timestamp, 1440)
    hours, minutes = divmod(remainder, 60)
    td = timedelta(days=int(days), hours=int(hours), minutes=int(minutes))
    _1970 = datetime(1970, 1, 1, 0, 0, 0)
    dt = _1970 + td
    return dt


def get_datestamp(date_var: Optional[Union[datetime, date]] = None) -> int:
    if date_var is None:
        date_var = date.today()
    elif isinstance(date_var, datetime):
        date_var = date_var.date()
    _1970 = date(1970, 1, 1)
    td = date_var - _1970
    return td.days


def get_date(datestamp: int) -> date:
    td = timedelta(days=int(datestamp))
    _1970 = date(1970, 1, 1)
    d = _1970 + td
    return d


def set_var(instance, value):
    instance = value
    return instance
