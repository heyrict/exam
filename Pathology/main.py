#!/usr/bin/env python3
import sys

from exam import *

sys.path.insert(0, '..')


class QuestFormTextLoaderRevise(QuestFormTextLoader):
    def load(self):
        qf = self.get_cached_qf()
        if type(qf) != type(None): return qf

        filename = './Pathology.md'
        with open(filename) as f:
            queststr = f.read()

        splits = re.split(r'## ', queststr)[1:]
        splits = [i.split('\n', 1) for i in splits]
        for i, d in enumerate(splits):
            print(i, d[0])
        no = InteractiveAnswer(
            'Which one to choose?',
            verify=range(len(splits)),
            serializer=lambda x: [int(i) for i in split_wrd(x, list(' ,，、'))]
        ).get()
        qf = QuestForm()
        for i in no:
            qf.extend(self._load(splits[i][1], chapter=splits[i][0]))

        return qf

    def _load(self, queststr, chapter=None):
        questform = QuestForm()
        for quest in re.findall(self.questpattern, queststr):
            qitem = re.findall(self.qpattern, quest)
            selitem = None
            taitem = re.findall(self.tapattern,
                                quest) if self.tapattern else None
            argitem = [(patnam, re.findall(self.argpattern[patnam], quest)) \
                    for patnam in self.argpattern] if self.argpattern else {}
            argitem['chapter'] = chapter
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
        elif ans == 'drop':
            print(colorit('Roger!', 'magenta'))
            return True
        elif split_wrd(ans.upper(), list(', ，、'),
                       '') == ''.join(quest.ta).upper():
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
        questpattern=r'第[0-9\-]+题[\s\S]+?(?<=\n\n)',
        qpattern=r'[\s\S]+(?=正确答案：)',
        tapattern=r'(?<=正确答案：)[A-E]+').load()
    BeginBioChemQuestForm(
        qf,
        input_manner=InteractiveAnswer("Your Answer:"),
        arrange="qst",
        storage='l|wo').start()


if __name__ == '__main__':
    main()
