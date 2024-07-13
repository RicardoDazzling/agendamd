

class UserError(Exception):
    pass


class NotLoggedException(UserError):
    pass


class UserNotLoggedException(UserError):
    pass
