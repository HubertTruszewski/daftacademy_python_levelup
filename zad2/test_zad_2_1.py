import unittest

from zad2_1 import greetings


class ExampleTest(unittest.TestCase):
    @greetings
    def show_greetings(self):
        return "joe doe"

    def test_result(self):
        self.assertEqual(self.show_greetings(), "Hello Joe Doe")


if __name__ == "__main__":
    unittest.main()
