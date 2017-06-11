import re, pickle, random, os
from datetime import datetime
from data_processing import split_wrd, InteractiveAnswer, space_fill, colorit, _in_list
from dateutil.relativedelta import relativedelta

BOARDER_LENGTH = 40

class Quest():
    def __init__(self,q,sel=None,ta=None,args={}):
        self.q = q
        self.sel = sel
        self.ta = ta
        self.args = args


class QuestForm(list):
    def __init__(self,*args,**kwargs):
        super(QuestForm,self).__init__(*args,**kwargs)

    def __getitem__(self,ind):
        if type(ind) == int:
            return super(QuestForm,self).__getitem__(ind)
        else:
            returns = QuestForm()
            for i in ind: returns.append(self[i])
            return returns
    def append(self,*args,**kwargs):
        super(QuestForm,self).append(*args,**kwargs)
        return self


class QuestFormTextLoader():
    def __init__(self,questpattern,qpattern,selpattern=None,tapattern=None,argpattern={}):
        self.questpattern = questpattern
        self.qpattern = qpattern
        self.selpattern = selpattern
        self.tapattern = tapattern
        self.argpattern = dict(argpattern)
        self.is_cached = False

    def get_cached_qf(self,togo='Curdata.data'):
        if togo in os.listdir():
            if InteractiveAnswer('Cached data found.Continue?',yes_or_no=True).get():
                with open(togo,'rb') as f: return pickle.load(f)
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
        import pandas as pd
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
    def __init__(self,qf,arrange='qast',storage='l|w',no_score=False,input_manner=None,no_filter=False):
        self.qf = qf
        self.starttime = datetime.now()
        self.correct = []
        self.wrong = []
        self.arrange = arrange
        self.storage = storage
        self.no_score = no_score
        self.input_manner = input_manner
        self.status = []
        self.no_filter = no_filter

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
        elif len(self.correct)+len(self.wrong) != 0:
            c = len(self.correct)
            w = len(self.wrong)
            print('Correct: ',c)
            print('Wrong: ',w)
            print('Score: %.2f'%(c/(c+w)*100))
            print('\n','-'*BOARDER_LENGTH,'\n')
            self.show_status(usedtime.hours)
        print('\n','='*BOARDER_LENGTH,'\n')


    def onkill(self):
        print('\n\n','='*BOARDER_LENGTH,'\n')
        print(space_fill('Interrupted',BOARDER_LENGTH))
        self._report()
        self.store_data(level=self.storage)
        return

    def onfinish(self):
        print('\n\n','='*BOARDER_LENGTH,'\n')
        print(space_fill('Finished',BOARDER_LENGTH))
        self._report()
        self.store_data(level=self.storage)
        return

    def store_data(self,togo='Curdata.data',torevise='Wrongdata.data',level='l|w'):
        l = [i for i in range(len(self.qf)) if not (_in_list(i,self.correct) | _in_list(i,self.wrong))]

        togoindex = []
        for i,j in zip('cwl',[self.correct,self.wrong,l]):
            if i in level.split('|')[0]: togoindex += j
        togoindex.sort()
        qf = self.qf[togoindex]
        if len(qf) != 0:
            with open(togo,'wb') as f:
                pickle.dump(qf,f)
        else:
            try: os.remove(togo)
            except: pass
        
        if len(level.split('|')) > 1:
            toreviseindex = []
            for i,j in zip('cwl',[self.correct,self.wrong,l]):
                if i in level.split('|')[1]: toreviseindex += j
            toreviseindex.sort()
            qf = self.qf[toreviseindex]
            if len(qf) != 0:
                if torevise not in os.listdir():
                    with open(torevise,'wb') as f:
                        pickle.dump(qf,f)
                else:
                    with open(torevise,'rb') as f:
                        wrongdata = pickle.load(f)
                    with open(torevise,'wb') as f:
                        wrongdata = wrongdata.append(qf)
                        pickle.dump(wrongdata,f)
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
            else:
                for k in quest.args:
                    if re.findall('^'+a, k):
                        print(k+':',quest.args[k])
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
        try:
            if not self.no_filter: self.qf = self.selchap(self.qf)
            self.length = len(self.qf)
            self.arranged_index = list(range(self.length))
            self.oninit()
            for quest in self.arranged_index:
                if self.raise_quest(self.qf[quest]):
                    self.correct.append(quest)
                    self.status.append(((datetime.now()-self.starttime).seconds, 1))
                else:
                    self.wrong.append(quest)
                    self.status.append(((datetime.now()-self.starttime).seconds, 0))
            self.onfinish()
        except (KeyboardInterrupt, EOFError): self.onkill()

    def raise_q(self,quest):
        print('Question %d/%d: '%(len(self.correct)+len(self.wrong)+1,self.length),end='')
        print('\n'.join(quest.q))
        return

    def raise_sel(self,quest):
        if quest.sel: print('\n'.join(quest.sel))

    def raise_ta(self,quest):
        if quest.ta: print('True Answer:',' '.join(quest.ta))

    def check_ans(self,ans,quest):
        if self.no_score: return True
        if ans == ''.join(quest.ta):
            print(colorit('Correct!','green'))
            return True
        else:
            print(colorit('WRONG!','red'))
            return False

    def show_status(self,hduration):
        result = []
        tempres = [0,0]
        status = self.status
        if hduration == 0:
            inteval = 3 * 60
        if hduration > 0:
            inteval = 5 * hduration * 60

        cursec = inteval
        for i in status:
            while cursec - i[0] <= 0:
                result.append(tempres)
                tempres = [0,0]
                cursec += inteval
            tempres[i[1]] += 1
        result.append(tempres)

        total = inteval
        for i in result:
            print('%3dm:'%(total/60),colorit('+'*i[1],'green')+colorit('-'*i[0],'red'))
            total += inteval
        return result
