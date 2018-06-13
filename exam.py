import os
import pickle
import random
import re
from datetime import datetime

from data_processing import (InteractiveAnswer, _in_list, colorit, space_fill,
                             split_wrd)

BOARDER_LENGTH = 40


class Quest():
    def __init__(self, q, sel=None, ta=None, args={}):
        '''
        Class representing a Question.

        Parameters
        ----------
        basic arguments:
            q : question. necessary. list.
            sel : selections. list.
            ta : true answer. list.
        extensable arguments:
            args : dict with sets of {'name': 'value'}.
        '''
        self.q = q
        self.sel = sel
        self.ta = ta
        self.args = args

    def __str__(self):
        '''Visualize the `Quest`.'''
        return '{\n\tq: %s,\n\tsel: %s,\n\tta: %s,\n\targs: %s\n}' % \
            (self.q, self.sel, self.ta, self.args)

    def __eq__(self, value):
        '''Evalue two `Quest`s as equal.'''
        if type(value) != type(self): return False
        for i in ['q', 'sel', 'ta', 'args']:
            if self.__getattribute__(i) != value.__getattribute__(i):
                return False
        return True

    def __hash__(self):
        return (hash('\n'.join(self.q)) + hash('\n'.join(self.sel)) + \
                hash('\n'.join(self.ta)) + hash('\n'.join(self.args))) % int(1e+16)


class QuestForm(list):
    def __init__(self, *args, **kwargs):
        super(QuestForm, self).__init__(*args, **kwargs)

    def __getitem__(self, ind):
        if type(ind) == int:
            return super(QuestForm, self).__getitem__(ind)
        if type(ind) == slice:
            return QuestForm(super(QuestForm, self).__getitem__(ind))
        else:
            returns = QuestForm()
            for i in ind:
                returns.append(self[i])
            return returns

    def append(self, *args, **kwargs):
        super(QuestForm, self).append(*args, **kwargs)
        return self


class QuestFormTextLoader():
    '''QuestForm Loader for text files.'''

    def __init__(self,
                 questpattern,
                 qpattern,
                 selpattern=None,
                 tapattern=None,
                 argpattern={}):
        '''
        Parameters
        ----------
        questpattern : regex pattern for a question. necessary.
        qpattern : regex pattern for question text in a question. necessary.
        selpattern : regex pattern for selections.
                     a question can have several matching selections.
        tapattern : regex pattern for true answer.
        argpattern : dict with {'arg_name' : 'arg_regex'} sets.
        '''
        self.questpattern = questpattern
        self.qpattern = qpattern
        self.selpattern = selpattern
        self.tapattern = tapattern
        self.argpattern = dict(argpattern)
        self.is_cached = False

    def get_cached_qf(self, togo='Curdata.data'):
        '''Load cached QuestForm.'''
        if togo in os.listdir():
            if InteractiveAnswer(
                    'Cached data found.Continue?', yes_or_no=True).get():
                with open(togo, 'rb') as f:
                    return pickle.load(f)
        else:
            datas = ["Create a new data"] + [
                i for i in os.listdir() if re.findall(r'.*\.data$', i)
            ]
            if not datas: return
            print("Cached data not found, listing other datas")
            for i in range(len(datas)):
                print('\t%3s: \t%s' % (i, datas[i]))
            no = InteractiveAnswer(
                'Which one to choose?',
                verify=range(len(datas)),
                serializer=
                lambda x: [int(i) for i in re.findall(r'[0-9]+', x)]).get()[0]
            if no == 0:
                return
            else:
                with open(datas[no], 'rb') as f:
                    return pickle.load(f)

    def _load(self, queststr):
        questform = QuestForm()
        for quest in re.findall(self.questpattern, queststr):
            qitem = re.findall(self.qpattern, quest)
            selitem = re.findall(self.selpattern,
                                 quest) if self.selpattern else None
            taitem = re.findall(self.tapattern,
                                quest) if self.tapattern else None
            argitem = [(patnam,re.findall(self.argpattern(patnam),quest)) \
                    for patnam in self.argpattern] if self.argpattern else {}
            questform = questform.append(
                Quest(q=qitem, sel=selitem, ta=taitem, args=argitem))
        return questform

    def load(self, queststr):
        '''Search queststr, match arguments and returns a QuestForm.'''
        qf = self.get_cached_qf()
        if qf is not None:
            self.is_cached = True
            return qf

        if 'MainData.data' in os.listdir():
            with open('MainData.data', 'rb') as f:
                qf = pickle.load(f)
        else:
            qf = self._load(queststr)
            with open('MainData.data', 'wb') as f:
                pickle.dump(qf, f)

        return qf


class QuestFormExcelLoader(QuestFormTextLoader):
    '''QuestForm Loader for excel files. Requires `pandas` module.'''

    def __init__(self, qcol, selcol=None, tacol=None, argcol={}):
        '''
        Parameters
        ----------
        questpattern : regex pattern for a question. necessary.
        qpattern : regex pattern for question text in a question. necessary.
        selpattern : regex pattern for selections.
                     a question can have several matching selections.
        tapattern : regex pattern for true answer.
        argpattern : dict with {'arg_name' : 'arg_regex'} sets.
        '''
        super(QuestFormExcelLoader, self).__init__(None, qcol, selcol, tacol,
                                                   argcol)

    def _load(self, questdf):
        import pandas as pd
        if type(questdf) == str: questdf = pd.read_excel(questdf)
        questform = QuestForm()
        for q in range(len(questdf)):
            quest = questdf.ix[q]
            qitem = quest[self.qpattern]
            selitem = quest[self.selpattern] if self.selpattern else None
            taitem = quest[self.tapattern] if self.tapattern else None
            argitem = {
                pat: quest[self.argpattern[pat]]
                for pat in self.argpattern
            } if self.argpattern else {}

            qitem = None if qitem is None else ([qitem] if isinstance(
                qitem, str) else list(qitem))
            selitem = None if selitem is None else ([selitem] if isinstance(
                selitem, str) else list(selitem))
            taitem = None if taitem is None else ([taitem] if isinstance(
                taitem, str) else list(taitem))

            questform = questform.append(
                Quest(q=qitem, sel=selitem, ta=taitem, args=argitem))
        return questform


class BeginQuestForm():
    '''Class for rendering the exam.'''

    def __init__(self,
                 qf,
                 arrange='qast',
                 no_score=False,
                 input_manner=None,
                 no_filter=False,
                 storage='l|w',
                 filenames=['Curdata.data', 'Wrongdata.data']):
        '''
        Parameters
        ----------
        qf : QuestForm. The QuestForm that test on.
        storage : str with several units separated by `|`.
                each unit contains one or more of `twol`.
                `t` indicates Quests that marked as true.
                `w` indicates Quests that marked as false.
                `o` indicates Quests that marked as others.
                `l` indicates Quests that isn't marked.
        filenames : list with each element indicates the filename of
                the output of `storage` option.
        arrange : iterable. each element should be one argument in a `Quest` object.
                `question` indicates the question text.
                `args` indicates all args.
                `selections` indicates the question text.
                `trueanswer` indicates the trueanswer text.
                `label` may indicate the `lable` keyword in `args` child in `Quest`.
                If not ambiguous, you can use `q` or `que` to indicate `question`,
                or `a` to indicate `answer`.
        no_filter : determines whether to record the True/False/others score.
        input_manner : a class with a .get() method returns input text.
                    designed for `InteractiveAnswer` class.
        no_filter : determines whether to filter the qf by `self.sel_chap`.
        '''
        self.qf = qf
        self.starttime = datetime.now()
        self.correct = []
        self.wrong = []
        self.other = []
        self.arrange = arrange
        self.storage = storage
        self.store_filenames = filenames
        self.no_score = no_score
        self.input_manner = input_manner
        self.status = []
        self.no_filter = no_filter

    def selchap(self, qf):
        '''
        Dummy function to select chapters (or filtering the QuestForm).
        Override this funtion to make it work.
        '''
        return qf

    def oninit(self):
        '''Things done on initialize'''
        if InteractiveAnswer('Randomize?', yes_or_no=True).get():
            random.shuffle(self.arranged_index)
        print('\n', '=' * BOARDER_LENGTH, '\n')
        print(
            space_fill(
                self.starttime.strftime('%Y-%m-%d %H:%M:%S'), BOARDER_LENGTH))
        print(space_fill('Find %d questions.' % (self.length), BOARDER_LENGTH))
        print(space_fill('start test.', BOARDER_LENGTH))
        print('\n', '=' * BOARDER_LENGTH, '\n')

    def _report(self):
        ''' Report prints.'''
        print('\n\n', '=' * BOARDER_LENGTH, '\n')
        usedtime = (datetime.now() - self.starttime).seconds
        (usedtime, s) = divmod(usedtime, 60)
        (h, m) = divmod(usedtime, 60)
        print(space_fill('Total Time: %d hours, %d minutes, %d seconds'\
                %(h, m, s) ,BOARDER_LENGTH))
        if self.no_score: pass
        elif len(self.correct) + len(self.wrong) != 0:
            c = len(self.correct)
            w = len(self.wrong)
            print('Correct: ', c)
            print('Wrong: ', w)
            print('Score: %.2f' % (c / (c + w) * 100))
            print('\n', '-' * BOARDER_LENGTH, '\n')
            self.show_status(h)
        print('\n', '=' * BOARDER_LENGTH, '\n')

    def onkill(self):
        ''' Things done on kill/interrupt.'''
        print('\n\n', '=' * BOARDER_LENGTH, '\n')
        print(space_fill('Interrupted', BOARDER_LENGTH))
        self._report()
        self.store_data(level=self.storage, filenames=self.store_filenames)
        return

    def onfinish(self):
        ''' Things done on finishing exam.'''
        print('\n\n', '=' * BOARDER_LENGTH, '\n')
        print(space_fill('Finished', BOARDER_LENGTH))
        self._report()
        self.store_data(level=self.storage, filenames=self.store_filenames)
        return

    def store_data(self,
                   filenames=['Curdata.data', 'Wrongdata.data'],
                   level='l|w'):
        ''' Stores data.'''
        # get left quests
        l = [
            i for i in range(len(self.qf))
            if not (_in_list(i, self.correct) | _in_list(i, self.wrong)
                    | _in_list(i, self.other))
        ]

        _level = level.split('|')
        for fn, lv in zip(filenames, range(len(_level))):
            index = []
            # add required quests to index
            for i, j in zip('cwol', [self.correct, self.wrong, self.other, l]):
                if i in _level[lv]: index += j
            index.sort()
            qf = self.qf[index]
            # TODO: duplicated. add append/write method as an option
            if fn == 'Curdata.data':
                if len(qf) != 0:
                    with open(fn, 'wb') as f:
                        pickle.dump(qf, f)
                else:
                    try:
                        os.remove(fn)
                    except:
                        pass
            else:
                if fn not in os.listdir():
                    with open(fn, 'wb') as f:
                        pickle.dump(qf, f)
                else:
                    with open(fn, 'rb') as f:
                        data = pickle.load(f)
                    data = QuestForm(data + qf)
                    with open(fn, 'wb') as f:
                        pickle.dump(data, f)

    def raise_quest(self, quest, **kwargs):
        '''Loop to raise a `Quest` according to `self.arrange`.'''
        ans = None
        for a in self.arrange:
            if re.findall('^' + a, 'quest'):
                self.raise_q(quest, **kwargs)
            elif re.findall('^' + a, 'args'):
                if not quest.args: continue
                for k in quest.args:
                    print(k + ':', quest.args[k])
            elif re.findall('^' + a, 'selection'):
                self.raise_sel(quest, **kwargs)
            elif re.findall('^' + a, 'true_answer'):
                ans = self.get_input(self.input_manner)
                ans = self.check_ans(ans, quest, **kwargs)
                if ans is not True or self.no_score:
                    self.raise_ta(quest, **kwargs)
            else:
                for k in quest.args:
                    if re.findall('^' + a, k):
                        print(k + ':', quest.args[k])
        print('\n', '-' * BOARDER_LENGTH, '\n')
        return ans

    def get_input(self, input_manner=None):
        '''Get user input if input_manner is not given.'''
        if input_manner is None:
            return input('Your Answer: ')
        else:
            try:
                return input_manner.get()
            except AttributeError:
                raise TypeError('`input_manner` should have a `get()` method')

    def start(self):
        '''Starting point.'''
        try:
            if not self.no_filter: self.qf = self.selchap(self.qf)
            self.length = len(self.qf)
            self.arranged_index = list(range(self.length))
            self.oninit()
            for quest in self.arranged_index:
                tof = self.raise_quest(self.qf[quest], qid=quest)
                if tof is True:
                    self.correct.append(quest)
                    self.status.append(
                        ((datetime.now() - self.starttime).seconds, 1))
                elif tof is False:
                    self.wrong.append(quest)
                    self.status.append(
                        ((datetime.now() - self.starttime).seconds, 0))
                else:
                    self.other.append(quest)
                    self.status.append(
                        ((datetime.now() - self.starttime).seconds, 2))
            self.onfinish()
        except (KeyboardInterrupt, EOFError):
            self.onkill()

    def raise_q(self, quest, **kwargs):
        '''Raises question in a `Quest`. You may want to overwrite it'''
        print(
            'Question %d/%d: ' %
            (len(self.other) + len(self.correct) + len(self.wrong) + 1,
             self.length),
            end='')
        print('\n'.join(quest.q))
        return

    def raise_sel(self, quest, **kwargs):
        '''Raises selections in a `Quest`. You may want to overwrite it'''
        if quest.sel: print('\n'.join(quest.sel))

    def raise_ta(self, quest, **kwargs):
        '''Raises true answer in a `Quest`. You may want to overwrite it'''
        if quest.ta: print('True Answer:', ' '.join(quest.ta))

    def check_ans(self, ans, quest, **kwargs):
        '''
        Check answer. returns True or False or other to your convenience.
        You may want to overwrite it.
        '''
        if self.no_score: return True
        if ans == ''.join(quest.ta):
            print(colorit('Correct!', 'green'))
            return True
        else:
            print(colorit('WRONG!', 'red'))
            return False

    def show_status(self, hduration):
        ''' Show statistics before exit.  '''
        result = []
        tempres = [0, 0, 0]
        status = self.status
        if hduration == 0:
            inteval = 3 * 60
        if hduration > 0:
            inteval = 5 * hduration * 60

        cursec = inteval
        for i in status:
            while cursec - i[0] <= 0:
                result.append(tempres)
                tempres = [0, 0, 0]
                cursec += inteval
            tempres[i[1]] += 1
        result.append(tempres)

        total = inteval
        for i in result:
            print('%3dm:' % (total / 60),
                  colorit('+' * i[1], 'green') + colorit('-' * i[0], 'red'))
            total += inteval
        return result
