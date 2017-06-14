#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import optparse, sys
import exam, pickle
from count_words import count_iter
from data_processing import colorit

def main():
    opt = optparse.OptionParser()
    opt.add_option('-n',dest='thresh',help='threshold of the max'\
            'groupby value(default 30)',default=None)
    
    (options, args) = opt.parse_args()

    if options.thresh:
        thresh = int(options.thresh)
    else: thresh = 30

    for i in args:
        print(colorit(i+':','lightcyan'))
        try: 
            with open(i,'rb') as f: data = pickle.load(f)
        except: print('\tNot a data file.'); continue

        print('\tCount of all Questions:',len(data))
        arguments = {}
        for q in data:
            for a in q.args:
                if a not in arguments: arguments[a] = []
                arguments[a].append(q.args[a])

        for a in arguments:
            c = count_iter(arguments[a])
            if len(c) > thresh:
                print('\tCount of %s:'%a,len(arguments[a]))
            else:
                print('\tCount of %s:'%a)
                for item in c.items():
                    print('\t\t',item[0],'\t:\t',item[1],sep='')
    return

main()
