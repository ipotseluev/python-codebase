#!/usr/bin/python

class Test:
    def __new__(cls):
        if not hasattr(cls, "_instans"):
            print("__new__: allocate!")
            cls._instans = object.__new__(cls)
        else:
            print("__new__: already created!")
        return cls._instans

    def __init__(self):
        print("__init__")
        # usage of hasattr forbids declaration of _instans
test1 = Test()
test2 = Test()
