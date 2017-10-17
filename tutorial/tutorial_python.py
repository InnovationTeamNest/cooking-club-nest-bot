# -*- coding: utf-8 -*-

from tutorial_class import TestClass


def main():
    print("Hello world!")

    i = 0
    while True:
        if i > 3:
            break
        else:
            print(i)
            i = i + 1

    if True and False:
        print("We suck... :(")

    print(range(3))

    for i in range(3):
        print(i)

    a_string = "\nWe are cool! :D"
    print(a_string)

    a_list = [1, 2, 3]
    print(a_list)

    a_dictionary = {"a": 1, "pi": 3.14, "word": "test"}
    print(a_dictionary)
    print(a_dictionary["pi"])
    print(a_dictionary.get("pi"))

    for k, v in a_dictionary.items():
        print("key: {} - value: {}".format(k, v))

    comprehension()

    test_object = TestClass("Gianvito", 42, {"id": 123, "pass": "AlanTuring"})

    test_object.foo()
    print(test_object._private)

    test_object.double()
    print(test_object)

    try:
        print("This awesome tutorial is going to end soon...")
        nooooope = 1 / 0
        print("This line will not be printed due to the previous exception.")
    except ZeroDivisionError as ex:
        print(ex.message)
        print("Sayonara!")
    except IOError as ex:
        print(ex.message)
        print("This exception won't be thrown...")


def comprehension():
    a_list = [x for x in range(5)]
    print(a_list)

    a_list = [x for x in "This is a test sentence".split(" ")]
    print(a_list)

    a_list = [x for x in range(5) if x % 2 == 0]
    print(a_list)

    a_list = [x ** 2 for x in range(5) if x % 2 == 0]
    print(a_list)

    a_dictionary = {x: x ** 2 for x in range(5)}
    print(a_dictionary)


if __name__ == '__main__':
    main()
