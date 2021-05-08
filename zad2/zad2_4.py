def add_instance_method(arg):
    def decorator(func):
        def check_attribute(*args):
            if len(args) < 1:
                raise AttributeError
            return func()

        def func_val(*args):
            return func()
        setattr(arg, func.__name__, check_attribute)
        return func_val
    return decorator


def add_class_method(arg):
    def decorator(func):
        def my_func(*args):
            return func()
        setattr(arg, func.__name__, my_func)
        return my_func
    return decorator
