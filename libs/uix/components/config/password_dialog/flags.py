__all__ = ['PasswordDialogErrorFlag', 'EmptyFieldsException', 'PasswordException',
           'TooLongPasswordException', 'PasswordDoNotMatchException', 'PasswordExceptionFlagType']

from typing import Union, Type

from globals import (translator as _)


class PasswordDialogErrorFlag(ValueError):
    message: str = 'A password error flag has been set.'


class EmptyFieldsException(PasswordDialogErrorFlag):
    message: str = _('All fields are required.')


class PasswordException(PasswordDialogErrorFlag):
    message: str = _('Incorrect current password.')


class TooLongPasswordException(PasswordDialogErrorFlag):
    message: str = _('The new password or the confirmation are too long.')


class PasswordDoNotMatchException(PasswordDialogErrorFlag):
    message: str = _('Passwords do not match.')


def update_static_message_variables():
    EmptyFieldsException.message = _('All fields are required.')
    PasswordException.message = _('Incorrect current password.')
    TooLongPasswordException.message = _('The new password or the confirmation are too long.')
    PasswordDoNotMatchException.message = _('Passwords do not match.')


PasswordExceptionFlagType = Union[
    Type[EmptyFieldsException],
    Type[PasswordException],
    Type[TooLongPasswordException],
    Type[PasswordDoNotMatchException]
]
_.bind(update_static_message_variables)
