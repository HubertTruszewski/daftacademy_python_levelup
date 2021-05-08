import pytest

from zad2_3 import format_output


@format_output("first_name__last_name", "city")
def first_func():
    return {
        "first_name": "Jan",
        "last_name": "Kowalski",
        "city": "Warszawa",
    }


@format_output("first_name", "age")
def second_func():
    return {
        "first_name": "Jan",
        "last_name": "Kowalski",
        "city": "Warszawa",
    }


def test_1():
    assert first_func() == {"first_name__last_name": "Jan Kowalski", "city": "Warszawa"}


def test_2():
    with pytest.raises(ValueError):
        second_func()
