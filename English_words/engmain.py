#!/usr/bin/env python3

import sys
sys.path.insert(0, '..')

from exam import *

class QuestFormTextLoaderRevise(QuestFormTextLoader):
    def load(self):
        qf = self.get_cached_qf()
        if type(qf) != type(None): return qf

        filelist = [i for i in os.listdir() if re.search('\.md$',i) or re.search('\.txt',i)]
        for i in range(len(filelist)): print(i,filelist[i])
        no = InteractiveAnswer('Which one to choose?',verify=range(len(filelist)),
                serializer=lambda x: [int(i) for i in split_wrd(x,list(' ,，、'))]).get()
        if type(no) == int:
            with open(filelist[no]) as f: queststr = f.read()
        else:
            queststr = ''
            for i in no: 
                with open(filelist[i]) as f: queststr += f.read() + '\n\n'

        return self._load(queststr)


class BeginQuestFormEngMain(BeginQuestForm):
    def check_ans(self,ans,quest):
        return ans

    def raise_q(self,quest):
        super(BeginQuestFormEngMain,self).raise_q(quest)
        input('Your Answer: ')
        return

    def raise_sel(self,quest):
        if quest.sel: print('True Answer:',' '.join(quest.sel))

#def main():
#    qf = QuestFormTextLoaderRevise(questpattern='\d+\.[\s\S]+?(?<=\n\n)',qpattern='(?=\d+\.).*',
#            tapattern='\n(?! *\d).*').load()
#    BeginQuestForm(qf,no_score=True).start()
    

def main():
    reverse=InteractiveAnswer('Eng -> Chinese?',yes_or_no=True).get()
    if reverse:
        t=QuestFormTextLoaderRevise(questpattern='###[^#]*\n\n',qpattern='(?<=### )[^\n]+',selpattern='(?<=\n)[^\n]+').load()
        BeginQuestFormEngMain(t,no_score=True,input_manner=InteractiveAnswer('Acknowledged?',yes_or_no=True),arrange='qst').start()
    else:
        t=QuestFormTextLoaderRevise(questpattern='###[^#]*\n\n',qpattern='(?<=\n)[^\n]+',selpattern='(?<=### )[^\n]+').load()
        BeginQuestFormEngMain(t,no_score=True,input_manner=InteractiveAnswer('Acknowledged?',yes_or_no=True),arrange='qst').start()

if __name__ == '__main__':
    main()
