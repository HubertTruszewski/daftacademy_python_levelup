def is_palindrome(function):

    def return_value(*args):

        sentence = function(*args)
        lower_sentence = ''.join([x.lower() for x in sentence if x.isalnum()])

        if lower_sentence == lower_sentence[::-1]:
            return sentence + " - is palindrome"
        else:
            return sentence + " - is not palindrome"

    return return_value
