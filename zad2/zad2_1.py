def greetings(to_wrap):
    string = to_wrap(None)

    def wrapped(*args):
        nonlocal string
        string = string.title()
        string = 'Hello '+string
        return string
    return wrapped
