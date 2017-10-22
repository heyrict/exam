#!/usr/bin/env python3
import sys

from exam import *

sys.path.insert(0, '..')


class QuestFormTextLoaderRevise(QuestFormTextLoader):
    def load(self):
        qf = self.get_cached_qf()
        if type(qf) != type(None): return qf

        filelist = sorted([
            i for i in os.listdir()
            if re.search('\.md$', i) or re.search('\.txt', i)
        ])
        for i in range(len(filelist)):
            print(i, filelist[i])
        no = InteractiveAnswer(
            'Which one to choose?',
            verify=range(len(filelist)),
            serializer=lambda x: [int(i) for i in split_wrd(x, list(' ,，、'))]
        ).get()
        if type(no) == int:
            with open(filelist[no]) as f:
                queststr = f.read()
        else:
            queststr = ''
            qf = QuestForm()
            for i in no:
                with open(filelist[i]) as f:
                    qf.extend(self._load(f.read(), filename=filelist[i]))

        return qf

    def _load(self, queststr, filename=None):
        questform = QuestForm()
        for quest in re.findall(self.questpattern, queststr):
            qitem = [quest[1:].rstrip()]
            selitem = None
            taitem = re.findall(self.tapattern,
                                quest) if self.tapattern else None
            argitem = [(patnam, re.findall(self.argpattern[patnam], quest)) \
                    for patnam in self.argpattern] if self.argpattern else {}
            argitem['chapter'] = filename
            questform = questform.append(
                Quest(q=qitem, sel=selitem, ta=taitem, args=argitem))
        return questform


class BeginBioChemQuestForm(BeginQuestForm):
    def check_ans(self, ans, quest, **kwargs):
        if not quest.ta:
            self.qf[kwargs['qid']].ta = ans
            return 'getans'

        print('True Answer:', ''.join(quest.ta))
        if ans == 'pass':
            print(colorit('Roger!', 'magenta'))
            return 'pass'
        elif set(list(split_wrd(ans.upper(), list(', ，、'), ''))) == set(
                list(''.join(quest.ta))):
            print(colorit('Same!', 'green'))
            return True
        else:
            print(colorit('NotTheSame!', 'lightred'))
            return False

    def raise_q(self, quest, **kwargs):
        if quest.ta is None:
            print(colorit("No True Answer", "red"))
        super(BeginBioChemQuestForm, self).raise_q(quest, **kwargs)

    def raise_ta(self, quest, **kwargs):
        return


def main():
    qf = QuestFormTextLoaderRevise(
        questpattern='[ABCDE]?\d+\.[\s\S]+?(?<=\n\n)',
        qpattern='(?=\d+\.).*',
        tapattern='^[ABCDE]').load()
    BeginBioChemQuestForm(
        qf, input_manner=InteractiveAnswer("Your Answer:"),
        arrange="qst",
        storage='l|wo').start()


if __name__ == '__main__':
    main()
