# -*- coding: utf-8 -*-


class TestClass:
    def __init__(self, name, number, private):
        self.name = name
        self.number = number
        self._private = private

    def __repr__(self):
        return "Name {}, Number {}".format(self.name, self.number)

    def foo(self):
        print("My name is {}. My number is {}.".format(self.name, self.number))

    def double(self):
        self.number = self.number * 2
