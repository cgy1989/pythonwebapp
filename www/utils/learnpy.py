#!/usr/bin/python
# -*- coding: utf8 -*-


class Base(object):
    def __init__(self, name):
        self.name = name


class A(Base):
    def __init__(self, name, age):
        super(A, self).__init__(name)
        self._age = age


class B(Base):
    def __init__(self, name, gender):
        #super(B, self).__init__(name)
        self._gender = gender


class C(A, B):
    def __init__(self, name, age, gender):
        A.__init__(self, name, age)
        B.__init__(self, name, gender)
        self._speak = 'hello python'

    @property
    def speak(self):
        return self._speak


if __name__ == '__main__':
    cc = C('chen', 23, 'male')
    print cc.__dict__
