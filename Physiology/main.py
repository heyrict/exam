#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys

import pandas as pd

from data_processing import _in_list, colorit, split_wrd, unsqueeze_numlist
from exam import *

sys.path.insert(0, '..')


CHAP = 'Which chapter to choose(empty to enter search mode)\n'\
        '\t1\t绪论\n'\
        '\t2\t细胞的基本功能\n'\
        '\t3\t血液\n'\
        '\t4\t循环系统\n'\
        '\t5\t呼吸系统\n'\
        '\t6\t消化系统\n'\
        '\t7\t能量代谢与体温调节\n'\
        '\t8\t泌尿系统\n'\
        '\t9\t感觉器官\n'\
        '\t10\t神经系统的功能\n'\
        '\t11\t内分泌与生殖系统\n'


class BeginPhysioQuestForm(BeginQuestForm):
    def selchap(self, qf):
        # chapter
        kind = InteractiveAnswer(
            CHAP + ':',
            accept_empty=True,
            serializer=lambda x: [int(i) for i in split_wrd(x, list(', ，、'))],
            verify=unsqueeze_numlist('1-11')).get()

        if kind:
            qf = QuestForm(
                [i for i in qf if _in_list(i.args['Chapter'], kind)])
        else:  # include
            kind = InteractiveAnswer(
                'Which chapter to include?(empty to include all): ',
                accept_empty=True,
                serializer=lambda x: split_wrd(x, list(', ，、'))).get()
            if kind:
                qf = QuestForm(
                    [i for i in qf if _in_list(str(i.q + i.sel), kind)])
        return qf

    def raise_q(self, quest, **kwargs):
        if quest.ta is None:
            print(colorit("No True Answer", "red"))
        super(BeginPhysioQuestForm, self).raise_q(quest, **kwargs)

    def raise_ta(self, quest, **kwargs):
        return

    def check_ans(self, ans, quest, **kwargs):
        if ans == 'pass':
            print(colorit('Roger!', 'magenta'))
            return 'pass'
        elif quest.ta is None:
            self.qf[kwargs['qid']].ta = ans
            return False
        elif set(list(split_wrd(ans.upper(), list(', ，、'), ''))) == set(
                list(''.join(quest.ta))):
            print(colorit('Same!', 'green'))
            return True
        else:
            print(colorit('NotTheSame!', 'lightred'))
            return False

    def raise_sel(self, quest, **kwargs):
        if quest.sel:
            for sel, no in zip(quest.sel, 'ABCDE'):
                print(no + '.', sel)


def main():
    t = QuestFormExcelLoader(
        qcol='题干',
        selcol=['选项' + i for i in 'ABCDE'],
        tacol='Answer',
        argcol={'Chapter': '章节'})
    BeginPhysioQuestForm(
        t.load('Data.xlsx'),
        no_filter=t.is_cached,
        storage='l|wo').start()


if __name__ == '__main__':
    main()
