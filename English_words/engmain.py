#!/usr/bin/env python3

from exam import *

def main():
    with open('English_words.md') as f: data = f.read()
    t=QuestFormTextLoader(questpattern='###[^#]*\n\n',qpattern='(?<=\n)[^\n]+',tapattern='(?<=### )[^\n]+').load(data)
    BeginQuestForm(t).start()

if __name__ == '__main__':
    main()
