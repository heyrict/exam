import re, pickle, random, os
import pandas as pd, numpy as np
from datetime import datetime
from data_processing import split_wrd, InteractiveAnswer
from dateutil.relativedelta import relativedelta
from txtform import _space_fill

BOARDER_LENGTH = 40

class Quest():
    def __init__(self,q,sel=None,ta=None,args=[]):
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
    def __init__(self,questpattern,qpattern,selpattern=None,tapattern=None,argpattern=[]):
        self.questpattern = questpattern
        self.qpattern = qpattern
        self.selpattern = selpattern
        self.tapattern = tapattern
        self.argpattern = [argpattern] if type(argpattern) == str else argpattern

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
            argitem = [re.findall(pat,quest) for pat in self.argpattern] if self.argpattern else None
            questform = questform.append(Quest(q=qitem,sel=selitem,ta=taitem,args=argitem))
        return questform

    def load(self,queststr,args=None):
        '''
        args = [(argblockpattern,argnamepattern)+]
        '''
        qf = self.get_cached_qf()
        if type(qf) != type(None): return qf

        return self._load(queststr)


class QuestFormExcelLoader(QuestFormTextLoader):
    def __init__(self,qcol,selcol=None,tacol=None,argcol=[]):
        super(QuestFormExcelLoader,self).__init__(None,qcol,selcol,tacol,argcol)

    def _load(self,questdf):
        questform = QuestForm()
        for q in range(len(questdf)):
            quest = questdf.ix[q]
            qitem = quest[self.qpattern]
            selitem = quest[self.selpattern] if self.selpattern else None
            taitem = quest[self.tapattern] if self.tapattern else None
            argitem = [quest[pat] for pat in self.argpattern] if self.argpattern else None

            qitem = [qitem] if type(qitem)==str else\
                (None if type(qitem)==type(None) else list(qitem))
            selitem = [selitem] if type(selitem)==str else\
                (None if type(selitem)==type(None) else list(selitem))
            taitem = [taitem] if type(taitem)==str else\
                (None if type(taitem)==type(None) else list(taitem))
            argitem = [argitem] if type(argitem)==str else\
                (None if type(argitem)==type(None) else list(argitem))
            questform = questform.append(Quest(q=qitem,sel=selitem,ta=taitem,args=argitem))
        return questform


class BeginQuestForm():
    def __init__(self,qf,arrange='qast'):
        self.qf = qf
        self.starttime = datetime.now()
        self.correct = self.wrong = 0
        self.length = len(self.qf)
        self.arrange = arrange
        self.arranged_index = list(range(self.length))

    def oninit(self):
        if InteractiveAnswer('Randomize?',yes_or_no=True).get():
            random.shuffle(self.arranged_index)
        print('\n','='*BOARDER_LENGTH,'\n')
        print(_space_fill(self.starttime.strftime('%Y-%m-%d %H:%M:%S'),BOARDER_LENGTH))
        print(_space_fill('Find %d questions.'%(self.length),BOARDER_LENGTH))
        print(_space_fill('start test.',BOARDER_LENGTH))
        print('\n','='*BOARDER_LENGTH,'\n')

    def _report(self):
        print('\n\n','='*BOARDER_LENGTH,'\n')
        usedtime = relativedelta(datetime.now(),self.starttime)
        print(_space_fill('Total Time: %d hours, %d minutes, %d seconds'%(usedtime.hours,\
                        usedtime.minutes,usedtime.seconds),BOARDER_LENGTH))
        if self.correct+self.wrong != 0:
            print('Correct: ',self.correct)
            print('Wrong: ',self.wrong)
            print('Score: %.2f'%(self.correct/(self.correct+self.wrong)*100))
        print('\n','='*BOARDER_LENGTH,'\n')


    def onkill(self):
        print('\n\n','='*BOARDER_LENGTH,'\n')
        print(_space_fill('Interrupted',BOARDER_LENGTH))
        self._report()
        self.qf.index = range(len(self.qf))
        with open('Curdata.data','wb') as f:
            pickle.dump(self.qf,f)
        return

    def onfinish(self):
        print('\n\n','='*BOARDER_LENGTH,'\n')
        print(_space_fill('Finished',BOARDER_LENGTH))
        self._report()
        os.remove('Curdata.data')
        return

    def raise_quest(self,quest):
        ans = None
        for a in self.arrange:
            if re.findall('^'+a,'quest'):
                self.raise_q(quest)
            elif re.findall('^'+a,'args'):
                if not quest.args: continue
                for arg in quest.args:
                    if type(arg) == str:
                        print(arg)
                    else:
                        print(': '.join([str(i) for i in arg]))
            elif re.findall('^'+a,'selection'):
                self.raise_sel(quest)
            elif re.findall('^'+a,'true_answer'):
                ans = input('Your Answer: ')
                ans = self.check_ans(ans,quest)
                if not ans: self.raise_ta(quest)
        print('\n','-'*BOARDER_LENGTH,'\n')
        return ans
        
    def start(self):
        self.oninit()
        try:
            for quest in self.arranged_index:
                if self.raise_quest(self.qf[quest]):
                    self.correct += 1
                    self.qf = self.qf.drop(quest)
                else:
                    self.wrong += 1
            self.onfinish()
        except KeyboardInterrupt:
            self.onkill()

    def raise_q(self,quest):
        print('Question %d/%d: '%(self.correct+self.wrong+1,self.length),end='')
        print('\n'.join(quest.q))
        return

    def raise_sel(self,quest):
        if quest.sel: print('\n'.join(quest.sel))

    def raise_ta(self,quest):
        if quest.ta: print('True Answer:',' '.join(quest.ta))

    def check_ans(self,ans,quest):
        if ans == ''.join(quest.ta):
            print('Correct!')
            return True
        else:
            print('WRONG!')
            return False
