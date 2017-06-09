#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
sys.path.insert(0, '..')

from exam import *
from data_processing import split_wrd, _in_list, unsqueeze_numlist, colorit
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
        # chapter
        kind = InteractiveAnswer(CHAP+':',accept_empty=True,
                serializer=lambda x: [int(i) for i in split_wrd(x,list(', ，、'))],
                verify=unsqueeze_numlist('0-13,16-19')).get()

        if kind:
            qf = QuestForm([i for i in qf if _in_list(i.args['Chapter'],kind)])
        else:
            # include
            kind = InteractiveAnswer('Which chapter to include?(empty to include all): ',accept_empty=True,
                    serializer=lambda x:split_wrd(x,list(', ，、'))).get()
            if kind:
                qf = QuestForm([i for i in qf if _in_list(','.join(i.q+i.sel),kind)])
            # exclude
            kind = InteractiveAnswer('Which chapter to exclude?(empty to skip): ',accept_empty=True,
                    serializer=lambda x:split_wrd(x,list(', ，、'))).get()
            if kind:
                qf = QuestForm([i for i in qf if not _in_list(','.join(i.q+i.sel),kind)])
        # difficulties
        kind = InteractiveAnswer('Which difficulty(ies) to choose? ',\
                serializer=lambda x:sum([list(i) for i in split_wrd(x,list(', ，、'),ignore_space=True)],[]),\
                verify='1234').get()
        outqf = QuestForm([i for i in qf if _in_list(i.args['Difficulty'],kind)])
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
            print(colorit('Correct!','green'))
            return True
        else:
            print(colorit('WRONG!','red'))
            return False

    def onkill(self):
        print('\n\n','='*BOARDER_LENGTH,'\n')
        print(space_fill('Interrupted',BOARDER_LENGTH))
        self._report()
        self.qf.index = range(len(self.qf))

        with open('Curdata.data','wb') as f:
            qf = self.qf[self.wrong:].copy()
            qf.index = range(len(qf))
            pickle.dump(qf,f)

        if self.wrong > 0:
            if 'Wrongdata.data' not in os.listdir():
                with open('Wrongdata.data','wb') as f:
                    qf = self.qf[:self.wrong].copy()
                    qf.index = range(len(qf))
                    pickle.dump(self.qf[:self.wrong],f)
            else:
                with open('Wrongdata.data','rb') as f:
                    wrongdata = pickle.load(f)
                with open('Wrongdata.data','wb') as f:
                    wrongdata = wrongdata.append(self.qf[:self.wrong])
                    pickle.dump(wrongdata,f)
        return


def main():
    t=QuestFormExcelLoader(qcol='question',selcol=['option_'+i for i in 'abcde'],
            tacol='question_answer', argcol={'Difficulty':'question_difclt','Chapter':'question_num'})
    BeginQuestFormSysAna(t.load('Data.xlsx'),no_filter=t.is_cached).start()


if __name__ == '__main__':
    main()
