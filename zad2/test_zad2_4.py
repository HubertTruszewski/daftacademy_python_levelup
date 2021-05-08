from zad2_4 import add_class_method, add_instance_method


class A:
    pass


@add_class_method(A)
def foo():
    return "Hello!"


@add_instance_method(A)
def bar():
    return "Hello again!"


def test_1():
    assert A.foo() == "Hello!"
    assert A().foo() == "Hello!"
    assert A().bar() == "Hello again!"
    assert bar() == "Hello!"
