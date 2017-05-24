#!/usr/bin/env python3

from exam import *
from data_processing import split_wrd, _in_list
import pandas as pd

class BeginQuestFormSysAna(BeginQuestForm):
    def selchap(self,qf):
        outqf = QuestForm()
        kind = split_wrd(input('Which chapter to include?(empty to include all): '),list(', ，、'))
        if kind:
            outqf = outqf.append(QuestForm([i for i in qf if _in_list(','.join(i.q+i.sel),kind)]))
            qf = outqf
            outqf = QuestForm()
        kind = InteractiveAnswer('Which difficulty(ies) to choose? ',\
                serializer=lambda x:split_wrd(x,list(', ，、'),ignore_space=True),\
                varify='1234').get()
        outqf = outqf.append(QuestForm([i for i in qf if _in_list(i.args['Difficulty'],kind)]))
        return outqf

    def raise_sel(self,quest):
        if quest.sel: 
            for s,t in zip(quest.sel,'ABCDE'):
                print(t+':',s)

    def raise_q(self,quest):
        print('Question %d/%d: '%(self.correct+self.wrong+1,self.length),end='')
        print('\n'.join(quest.q),'' if len(quest.ta[0])==1 else '[多选]')
        return

    def check_ans(self,ans,quest):
        if set(list(split_wrd(ans.upper(),list(', ，、'),''))) == set(list(''.join(quest.ta))):
            print('Correct!')
            return True
        else:
            print('WRONG!')
            return False


def main():
    df = pd.read_excel('./Data.xlsx')
    t=QuestFormExcelLoader(qcol='question',selcol=['option_'+i for i in 'abcde'],tacol='question_answer',\
            argcol={'Difficulty':'question_difclt'}).load(df)
    BeginQuestFormSysAna(t).start()

if __name__ == '__main__':
    main()
