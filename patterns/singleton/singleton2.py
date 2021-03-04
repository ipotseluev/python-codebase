#!/usr/bin/python

class Test:
    _instance = None
    _inited = False

    def __new__(cls):
        if not Test._instance:
            print("__new__: allocate!")
            cls._instance = object.__new__(cls)
        else:
            print("__new__: already created!")
        return cls._instance

    def __init__(self):
        if not Test._inited:
            print("__init__: initialize!")
            Test._inited = True
        else:
            print("__init__: skip")

test1 = Test()
test2 = Test()
