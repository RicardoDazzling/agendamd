from functools import wraps


def ignore_args(func):
    @wraps(func)
    def ignore_args_wrapper_func(*args):
        if args:
            pass
        __search = getattr(args[0], func.__name__, None)
        __return = func() if __search is None else func(args[0])
        if __return:
            return __return
    return ignore_args_wrapper_func


def ignore_kwargs(func):
    @wraps(func)
    def ignore_kwargs_wrapper_func(self=None, **kwargs):
        if kwargs:
            pass
        __return = func() if self is None else func(self)
        if __return:
            return __return
    return ignore_kwargs_wrapper_func


def ignore_args_and_kwargs(func):
    @wraps(func)
    def ignore_args_and_kwargs_wrapper_func(*args, **kwargs):
        if kwargs or args:
            pass
        __search = getattr(args[0], func.__name__, None)
        __return = func() if __search is None else func(args[0])
        if __return:
            return __return
    return ignore_args_and_kwargs_wrapper_func


def ignore_instance(func):
    @wraps(func)
    def ignore_instance_wrapper_func(*args):
        __search = getattr(args[0], func.__name__, None)
        args = list(args)
        args.pop(0) if __search is None or len(args) <= 2 else args.pop(1)
        __return = func(*args)
        if __return is not None:
            return __return
    return ignore_instance_wrapper_func


def only_the_instance(func):
    @wraps(func)
    def only_the_instance_wrapper_func(*args):
        __search = getattr(args[0], func.__name__, None)
        args = [args[0]] if __search is None else args[:2]
        __return = func(*args)
        if __return is not None:
            return __return
    return only_the_instance_wrapper_func
