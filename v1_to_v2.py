#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import optparse, pickle, exam

def main():
    opt = optparse.OptionParser()
    opt.add_option('-t',dest='test',action='store_true',default=False)
    (options, args) = opt.parse_args()

    maxlen = max([len(i) for i in args])
    for i in args:
        isv2 = False
        try:
            with open(i,'rb') as f: data = pickle.load(f)
        except:
            print(i.ljust(maxlen),':','not a data file')
            continue

        isv2 = type(data) == exam.QuestForm
        data = exam.QuestForm(data)
        if options.test: print(i.ljust(maxlen),':','v2' if isv2 else 'v1')
        else:
            if isv2:
                print(i.ljust(maxlen),':','v2. Skipping...')
            else:
                with open('v2.'.join(i.split('.')),'wb') as f: pickle.dump(data,f)
    return


main()
