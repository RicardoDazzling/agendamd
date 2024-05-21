from typing import Optional, Union, Literal
from datetime import datetime, timedelta, date
import logging


def log(self, message: str, log_type: Literal['error', 'info', 'warning'] = 'error'):
    name = self if isinstance(self, str) else self.__class__.__name__
    if log_type == 'error':
        logging.error(f'{name}: {message}', exc_info=True)
    elif log_type == 'info':
        logging.info(f'{name}: {message}')
    elif log_type == 'warning':
        logging.warning(f'{name}: {message}')


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
