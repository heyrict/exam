#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from exam import *
from data_processing import split_wrd, _in_list, unsqueeze_numlist
import pandas as pd

CHAP = 'Which chapter to choose(empty to enter search mode)\n'\
        '\t0\t未知\n'\
        '\t1\t骨、骨连接\n'\
        '\t2\t肌\n'\
        '\t3\t内脏学总论\n'\
        '\t4\t消化系统\n'\
        '\t5\t呼吸系统\n'\
        '\t6\t泌尿系统\n'\
        '\t7\t生殖系统\n'\
        '\t8\t腹膜\n'\
        '\t9\t心血管系统\n'\
        '\t10\t淋巴系统\n'\
        '\t11\t感觉器总论\n'\
        '\t12\t视器\n'\
        '\t13\t前庭蜗器\n'\
        '\t16\t中枢神经系统\n'\
        '\t17\t周围神经系统\n'\
        '\t18\t内分泌系统\n'\
        '\t19\t组织胚胎学\n'

class BeginQuestFormSysAna(BeginQuestForm):
    def selchap(self,qf):
        outqf = QuestForm()

        # chapter
        kind = InteractiveAnswer(CHAP+':',accept_empty=True,
                serializer=lambda x: [int(i) for i in split_wrd(x,list(', ，、'))],
                verify=unsqueeze_numlist('0-13,16-19')).get()

        if kind:
            outqf = outqf.append(QuestForm([i for i in qf if _in_list(i.args['Chapter'],kind)]))
            qf = outqf
            outqf = QuestForm()
        else:
            # include
            kind = InteractiveAnswer('Which chapter to include?(empty to include all): ',accept_empty=True,
                    serializer=lambda x:split_wrd(x,list(', ，、'))).get()
            if kind:
                outqf = outqf.append(QuestForm([i for i in qf if _in_list(','.join(i.q+i.sel),kind)]))
                qf = outqf
                outqf = QuestForm()
            # exclude
            kind = InteractiveAnswer('Which chapter to exclude?(empty to skip): ',accept_empty=True,
                    serializer=lambda x:split_wrd(x,list(', ，、'))).get()
            if kind:
                outqf = outqf.append(QuestForm([i for i in qf if not _in_list(','.join(i.q+i.sel),kind)]))
                qf = outqf
                outqf = QuestForm()
        # difficulties
        kind = InteractiveAnswer('Which difficulty(ies) to choose? ',\
                serializer=lambda x:sum([list(i) for i in split_wrd(x,list(', ，、'),ignore_space=True)],[]),\
                verify='1234').get()
        outqf = outqf.append(QuestForm([i for i in qf if _in_list(i.args['Difficulty'],kind)]))
        return outqf

    def raise_sel(self,quest):
        if quest.sel: 
            for s,t in zip(quest.sel,'ABCDE'):
                print(t+'.',s)

    def raise_q(self,quest):
        print('Question %d/%d: '%(self.correct+self.wrong+1,self.length),end='')
        print('\n'.join(quest.q),'' if len(quest.ta[0])==1 else '[多选]')
        return

    def check_ans(self,ans,quest):
        if set(list(split_wrd(ans.upper(),list(', ，、'),''))) == set(list(''.join(quest.ta))):
            print('\033[1;32mCorrect!\033[0m')
            return True
        else:
            print('\033[1;31mWRONG!\033[0m')
            return False


def main():
    t=QuestFormExcelLoader(qcol='question',selcol=['option_'+i for i in 'abcde'],
            tacol='question_answer', argcol={'Difficulty':'question_difclt','Chapter':'question_num'}).load('Data.xlsx')
    BeginQuestFormSysAna(t).start()


if __name__ == '__main__':
    main()
