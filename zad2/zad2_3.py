def format_output(*args):
    arguments = []
    multi_arguments = []
    for arg in args:
        splitted_args = arg.split("__")
        if len(splitted_args) > 1:
            multi_arguments.append(tuple(splitted_args))
        else:
            arguments.append(arg)

    def decorator(function):
        def build_dict(*args):
            result = function(*args)
            new_dict = {}
            for key in arguments:
                if key not in result:
                    raise ValueError
                new_dict[key] = result[key]
            for keys in multi_arguments:
                new_key = str()
                new_value = str()
                for key in keys:
                    if key not in result:
                        raise ValueError
                    new_key += key
                    new_key += "__"
                    new_value += result[key]
                    new_value += " "
                new_value = new_value[:-1]
                new_key = new_key[:-2]
                new_dict[new_key] = new_value
            return new_dict
        return build_dict
    return decorator
