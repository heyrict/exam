import re, pickle, random, os
import pandas as pd, numpy as np
from datetime import datetime
from data_processing import split_wrd, InteractiveAnswer, _space_fill

BOARDER_LENGTH = 40

class Quest():
    def __init__(self,q,sel=None,ta=None,args=None):
        self.q = q
        self.sel = sel
        self.ta = ta
        self.args = args


class QuestForm(pd.Series):
    def __init__(self,*args,**kwargs):
        super(QuestForm,self).__init__(*args,**kwargs)

    def append(self,to_append,*args,**kwargs):
        return QuestForm(super(QuestForm,self).append(pd.Series(to_append),ignore_index=True,*args,**kwargs))


class QuestFormTextLoader():
    def __init__(self,questpattern,qpattern,selpattern=None,tapattern=None):
        self.questpattern = questpattern
        self.qpattern = qpattern
        self.selpattern = selpattern
        self.tapattern = tapattern

    def get_cached_qf(self):
        if 'Curdata.data' in os.listdir():
            if InteractiveAnswer('Cached data found.Continue?',yes_or_no=True).get():
                with open('Curdata.data','rb') as f: return pickle.load(f)
        return
                
    def _load(self,queststr):
        questform = QuestForm()
        for quest in re.findall(self.questpattern,queststr):
            qitem = re.findall(self.qpattern,quest)
            selitem = re.findall(self.selpattern,quest) if self.selpattern else None
            taitem = re.findall(self.tapattern,quest) if self.tapattern else None
            questform = questform.append(Quest(q=qitem,sel=selitem,ta=taitem))
        return questform

    def load(self,queststr,args=None):
        '''
        args = [(argblockpattern,argnamepattern)+]
        '''
        qf = self.get_cached_qf()
        if type(qf) != type(None): return qf

        return self._load(queststr)

class BeginQuestForm():
    def __init__(self,qf):
        self.qf = qf
        self.starttime = datetime.now()
        self.correct = self.wrong = 0
        self.length = len(self.qf)
        self.arranged_index = list(range(self.length))

    def oninit(self):
        if InteractiveAnswer('Randomize?',yes_or_no=True).get():
            random.shuffle(self.arranged_index)
        print('\n','='*BOARDER_LENGTH,'\n')
        print(_space_fill(self.starttime.strftime('%Y-%m-%d %H:%M:%S'),BOARDER_LENGTH))
        print(_space_fill('Find %d questions.'%(self.length),BOARDER_LENGTH))
        print(_space_fill('start test.',BOARDER_LENGTH))
        print('\n','='*BOARDER_LENGTH,'\n')

    def onkill(self):
        print('\n\n','='*BOARDER_LENGTH,'\n')
        self.qf.index = range(len(self.qf))
        with open('Curdata.data','wb') as f:
            pickle.dump(self.qf,f)
        return

    def onfinish(self):
        os.remove('Curdata.data')
        return

    def raise_quest(self,quest):
        self.raise_q(quest)
        self.raise_sel(quest)
        ans = self.check_ans(input('Your Answer: '),quest)
        self.raise_ta(quest)
        print('\n','-'*BOARDER_LENGTH,'\n')
        return ans
        
    def loop_raise(self):
        self.oninit()
        try:
            for quest in self.arranged_index:
                if self.raise_quest(self.qf[quest]):
                    self.correct += 1
                    self.qf = self.qf.drop(quest)
                else:
                    self.wrong += 1
        except KeyboardInterrupt:
            self.onkill()

    def raise_q(self,quest):
        print('Question %d/%d: '%(self.correct+self.wrong+1,self.length),end='')
        print('\n'.join(quest.q))
        return

    def raise_sel(self,quest):
        if quest.sel: print('\n'.join(quest.sel))

    def raise_ta(self,quest):
        if quest.ta: print(' '.join(quest.ta))

    def check_ans(self,ans,quest):
        if ans == ''.join(quest.ta):
            print('Correct!')
            return True
        else:
            print('WRONG!')
            return False
