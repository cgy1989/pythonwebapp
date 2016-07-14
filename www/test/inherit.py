#!/usr/bin/python
# -*- coding: utf8 -*-


class A(object):
    def __init__(self, arg1):
        print "init func in A, with arg1 '%s'" % arg1
        super(A, self).__init__(arg1)


class B(object):
    def __init__(self, arg1, arg2):
        print "init func in B, with arg1'%s', arg2 '%s'" % (arg1, arg2)
        super(B, self).__init__()


class C(A, B):
    def __init__(self, arg1, arg2):
        print "init func in C, with arg1'%s', arg2 '%s'" % (arg1, arg2)
        super(C, self).__init__(arg1)
        print C.__mro__


if __name__ == '__main__':
    cc = C('chen', 23)

