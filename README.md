exam
====

A class to generate customized exam program.

Requirements
-----------
- Python 3 
- pandas (recommended)

Contents
--------
### class Quest
This is a class that stores every Question.

### class QuestForm
This is a class derived from class list that stores all `Quest`s

### class QuestFormTextLoader
This is a class that loads a structured text file containing a 
list of questions by the regular expression provided.

This class will also try to load cached data if exists.

### class QuestFormExcelLoader
This is a class similar to QuestFormTextLoader
that loads a list of questions from an excel file rather than a text file.

*YOU SHOULD MAKE SURE `PANDAS` IS INSTALLED IN YOUR PYTHON3*

### class BeginQuestForm
This is a class that runs a questionnaire if method `start` is called.

Usage
-----
### Simple usage

1. Prepare a document(text or excel file) containing a bunch of questions.

2. If your document is a text file, figure out the pattern of `the whole question`,
    `question`, and in most case, `selections` and `answer`, or may be other
    patterns for other arguments.

    if your document is an excel file, then figure out the column name for
    `question`, and in most case, `selections` and `answer`, or may be other
    column names for other arguments.

3. Implement a class (QuestFormTextLoader or QuestFormExcelLoader) with
    questpattern=`the whole question`, qpattern=`question`,
    selpattern=`selections`, answerpattern=`answer`,
    and argpattern={'name':'pattern',['name2':'pattern2'[..]]}

4. Call `load` method of the class you implemented in step 3 and stores the
    returned value in a variable, say **qf**.

    the `load` method of QuestFormTextLoader accepts a string that contains the whole data of your text file.
    
    the `load` method of QuestFormExcelLoader accepts the name of you excel file
    or pandas.DataFrame object if you are capable of pandas module.

5. Call BeginQuestForm(**qf**).start(). This will generate a questionnaire that
    gives a default performance.

### Advanced

Please refer to the help documents.
