#!/usr/bin/env python3

from exam import *
from data_processing import split_wrd
import pandas as pd

class BeginQuestFormSysAna(BeginQuestForm):
    def raise_sel(self,quest):
        if quest.sel: 
            for s,t in zip(quest.sel,'ABCDE'):
                print(t+':',s)

    def check_ans(self,ans,quest):
        if set(list(split_wrd(ans.upper(),list(', ，、'),''))) == set(list(''.join(quest.ta))):
            print('Correct!')
            return True
        else:
            print('WRONG!')
            return False


def main():
    df = pd.read_excel('./Data.xlsx')
    t=QuestFormExcelLoader(qcol='question',selcol=['option_'+i for i in 'abcde'],tacol='question_answer').load(df)
    BeginQuestFormSysAna(t).start()

if __name__ == '__main__':
    main()
