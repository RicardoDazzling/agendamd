

class LoginException(Exception):
    pass


class EMailException(LoginException):
    pass


class PasswordException(LoginException):
    pass


class NameException(LoginException):
    pass


class UserNotExistException(LoginException):
    pass


class EmptyFieldException(LoginException):
    pass
