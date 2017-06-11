#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import optparse, pickle, exam

def main():
    opt = optparse.OptionParser()
    (options, args) = opt.parse_args()

    for i in args:
        with open(i,'rb') as f: data = pickle.load(f)
        data = exam.QuestForm(data)
        with open('v3.'.join(i.split('.')),'wb') as f: pickle.dump(data,f)
    return


main()
