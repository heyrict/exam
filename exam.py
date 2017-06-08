import re, pickle, random, os
import pandas as pd
from datetime import datetime
from data_processing import split_wrd, InteractiveAnswer, space_fill, colorit
from dateutil.relativedelta import relativedelta

BOARDER_LENGTH = 40

class Quest():
    def __init__(self,q,sel=None,ta=None,args={}):
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
    def __init__(self,questpattern,qpattern,selpattern=None,tapattern=None,argpattern={}):
        self.questpattern = questpattern
        self.qpattern = qpattern
        self.selpattern = selpattern
        self.tapattern = tapattern
        self.argpattern = dict(argpattern)
        self.is_cached = False

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
            argitem = [(patnam,re.findall(self.argpattern(patnam),quest)) \
                    for patnam in self.argpattern] if self.argpattern else None
            questform = questform.append(Quest(q=qitem,sel=selitem,ta=taitem,args=argitem))
        return questform

    def load(self,queststr):
        qf = self.get_cached_qf()
        if type(qf) != type(None): 
            self.is_cached = True
            return qf

        if 'MainData.data' in os.listdir():
            with open('MainData.data','rb') as f: qf = pickle.load(f)
        else:
            qf = self._load(queststr)
            with open('MainData.data','wb') as f: pickle.dump(qf, f)

        return qf


class QuestFormExcelLoader(QuestFormTextLoader):
    def __init__(self,qcol,selcol=None,tacol=None,argcol={}):
        super(QuestFormExcelLoader,self).__init__(None,qcol,selcol,tacol,argcol)

    def _load(self,questdf):
        if type(questdf) == str: questdf = pd.read_excel(questdf)
        questform = QuestForm()
        for q in range(len(questdf)):
            quest = questdf.ix[q]
            qitem = quest[self.qpattern]
            selitem = quest[self.selpattern] if self.selpattern else None
            taitem = quest[self.tapattern] if self.tapattern else None
            argitem = {pat:quest[self.argpattern[pat]] for pat in self.argpattern} if self.argpattern else {}

            qitem = [qitem] if type(qitem)==str else list(qitem)
            selitem = [selitem] if type(selitem)==str else list(selitem)
            taitem = [taitem] if type(taitem)==str  else list(taitem)

            questform = questform.append(Quest(q=qitem,sel=selitem,ta=taitem,args=argitem))
        return questform


class BeginQuestForm():
    def __init__(self,qf,arrange='qast',no_score=False,input_manner=None,no_filter=False):
        if not no_filter: 
            self.qf = self.selchap(qf)
        else: self.qf = qf
        self.starttime = datetime.now()
        self.correct = self.wrong = 0
        self.length = len(self.qf)
        self.arrange = arrange
        self.no_score = no_score
        self.input_manner = input_manner
        self.arranged_index = list(range(self.length))
        self.status = []

    def selchap(self,qf):
        return qf

    def oninit(self):
        if InteractiveAnswer('Randomize?',yes_or_no=True).get():
            random.shuffle(self.arranged_index)
        print('\n','='*BOARDER_LENGTH,'\n')
        print(space_fill(self.starttime.strftime('%Y-%m-%d %H:%M:%S'),BOARDER_LENGTH))
        print(space_fill('Find %d questions.'%(self.length),BOARDER_LENGTH))
        print(space_fill('start test.',BOARDER_LENGTH))
        print('\n','='*BOARDER_LENGTH,'\n')

    def _report(self):
        print('\n\n','='*BOARDER_LENGTH,'\n')
        usedtime = relativedelta(datetime.now(),self.starttime)
        print(space_fill('Total Time: %d hours, %d minutes, %d seconds'\
                %(usedtime.hours,usedtime.minutes,usedtime.seconds)\
                ,BOARDER_LENGTH))
        if self.no_score: pass
        elif self.correct+self.wrong != 0:
            print('Correct: ',self.correct)
            print('Wrong: ',self.wrong)
            print('Score: %.2f'%(self.correct/(self.correct+self.wrong)*100))
            print('\n','-'*BOARDER_LENGTH,'\n')
            self.show_status(usedtime.hours)
        print('\n','='*BOARDER_LENGTH,'\n')


    def onkill(self):
        print('\n\n','='*BOARDER_LENGTH,'\n')
        print(space_fill('Interrupted',BOARDER_LENGTH))
        self._report()
        self.qf.index = range(len(self.qf))
        with open('Curdata.data','wb') as f:
            pickle.dump(self.qf,f)
        return

    def onfinish(self):
        print('\n\n','='*BOARDER_LENGTH,'\n')
        print(space_fill('Finished',BOARDER_LENGTH))
        self._report()
        if len(self.qf) == 0:
            if 'Curdata.data' in os.listdir(): os.remove('Curdata.data')
        else:
            self.qf.index = range(len(self.qf))
            with open('Curdata.data','wb') as f:
                pickle.dump(self.qf,f)
        return

    def raise_quest(self,quest):
        ans = None
        for a in self.arrange:
            if re.findall('^'+a,'quest'):
                self.raise_q(quest)
            elif re.findall('^'+a,'args'):
                if not quest.args: continue
                for k in quest.args:
                    print(k+':',quest.args[k])
            elif re.findall('^'+a,'selection'):
                self.raise_sel(quest)
            elif re.findall('^'+a,'true_answer'):
                ans = self.get_input(self.input_manner)
                ans = self.check_ans(ans,quest)
                if not ans or self.no_score: self.raise_ta(quest)
        print('\n','-'*BOARDER_LENGTH,'\n')
        return ans

    def get_input(self,input_manner=None):
        if not input_manner:
            return input('Your Answer: ')
        else:
            try: return input_manner.get()
            except AttributeError:
                raise TypeError('`input_manner` should have a `get()` method')
        
    def start(self):
        self.oninit()
        try:
            for quest in self.arranged_index:
                head = datetime.now()
                if self.raise_quest(self.qf[quest]):
                    self.correct += 1
                    self.qf = self.qf.drop(quest)
                    self.status.append((relativedelta(datetime.now(),head).seconds, 1))
                else:
                    self.wrong += 1
                    self.status.append((relativedelta(datetime.now(),head).seconds, 0))
            self.onfinish()
        except (KeyboardInterrupt, EOFError): self.onkill()

    def raise_q(self,quest):
        print('Question %d/%d: '%(self.correct+self.wrong+1,self.length+1),end='')
        print('\n'.join(quest.q))
        return

    def raise_sel(self,quest):
        if quest.sel: print('\n'.join(quest.sel))

    def raise_ta(self,quest):
        if quest.ta: print('True Answer:',' '.join(quest.ta))

    def check_ans(self,ans,quest):
        if self.no_score: return True
        if ans == ''.join(quest.ta):
            print('\033[1;31mCorrect!\033[0m')
            return True
        else:
            print('\033[1;32mWRONG!\033[0m')
            return False

    def show_status(self,hduration):
        result = []
        tempres = [0,0]
        status = self.status
        if hduration == 0:
            inteval = 2 * 60
        if hduration > 0:
            inteval = 5 * hduration * 60

        cursec = 0
        for i in status:
            while i[0]+cursec >= inteval:
                result.append(tempres)
                tempres = [0,0]
                cursec = i[0] + cursec - 60
            cursec += i[0]
            tempres[i[1]] += 1
        result.append(tempres)

        total = inteval
        for i in result:
            print('%dm: '%(total/60),colorit('+'*i[1],'green')+colorit('-'*i[0],'red'))
            total += inteval
        return result
