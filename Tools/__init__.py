def catch_exception (exceptionType=Exception, onFail=bool):
    """This decorator calls the onFail functor if exception 
       exceptionType is raised.
    """
    def decorator (function):
        def wrapper (*__args, **__kw):
            try:
                return function (*__args, **__kw)
            except exceptionType:
                return onFail ()
        wrapper.__name__ = function.__name__
        return wrapper
    return decorator
