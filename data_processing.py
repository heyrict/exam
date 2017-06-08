# coding: utf-8
import sys, re

def flip_dict(dict_to_flip):
    '''
    flip a dict.

    Parameters
    ----------
    dict_to_flip : dict

    Examples
    --------
    >>> flip_dict({'a': 2, 'b': 3, 'c': 4})
    {2: 'a', 3: 'b', 4: 'c'}

    Notes that duplicated data will be automaticly dropped
    >>> flip_dict({'a': 3, 'b': 3, 'c': 4})
    {3: 'a', 4: 'c'}

    See Also
    --------
    flip_dict_full
    '''
    return dict([i[::-1] for i in dict_to_flip.items()])


def split_wrd(string,sep,rep=None,ignore_space=False):
    '''
    split a string with given condition

    Parameters
    ----------
    string : str
        string to process
    sep : str or iterable
        for each item in sep, call string.split() method
    rep : None or str or iterable, default None
        - None : return a list containing all items seprated by sep
        - str : return a string with all items in sep replaced by rep
        - iterable : return a string with all sep[i] replaced by rep[i]
    ignore_space : bool
        - whether to call strip() at each element

    See Also
    --------
    split_at
    '''
    if type(sep) == str:
        sep = [sep]
    if rep == None:
        string = [string]
        for j in sep:
            ts = []
            for i in string:
                ts += i.split(j)
            string = ts
        if ignore_space: return [i.strip() for i in string if i.strip()]
        else: return [i for i in string if i]
    else:
        if type(rep)==str:
            for i in sep:
                string = rep.join(string.split(i))
            return string
        else:
            for i,j in zip(sep,rep):
                string = j.join(string.split(i))
            return string


def split_at(string,sep,ignore_space=False):
    '''
    split a string at given condition

    Parameters
    ----------
    string : str
        string to process
    sep : str or iterable
        for each item in sep, call string.split() method
    ignore_space : bool
        - whether to call strip() at each element

    See Also
    --------
    split_wrd
    '''
    if type(sep) == str:
        sep = [sep]
    string = [string]
    for i in sep:
        ts = []
        for j in string:
            ts += [s+i for s in j.split(i)]
            ts[-1] = ts[-1][:-1]
        if ignore_space: string = [s for s in ts if s.strip()]
        else: string = ts
    return string

def flip_dict_full(dict_to_flip):
    '''
    flip a dict with no data loss
    
    Parameters
    ----------
    dict_to_flip : dict

    See Also
    --------
    flit_dict

    Examples
    --------
    >>> flip_dict_full({'a': 1, 'b': 2, 'c': 3})
    {1: ['a'], 2: ['b'], 3: ['c']}
    >>> flip_dict_full({'a': 3, 'b': 3, 'c': 4})
    {3: ['a', 'b'], 4: ['c']}
    '''
    t = [i[::-1] for i in dict_to_flip.items()]
    tp = dict()
    for i in t:
        if i[0] in tp:
            tp[i[0]] = tp[i[0]] + [i[1]] if type(tp[i[0]])==list else [tp[i[0]]] + [i[1]]
        else: tp[i[0]] = [i[1]]
    return tp


def transfer_datatype(data):
    '''
    call eval(data) if data is valid
    '''
    if type(data) == list or not data: return data
    else:
        try: return eval(data)
        except: return data


def _in_list(x,ls,how='find'):
    '''
    check if x match rules in ls
    parameters:
        x : str-like or numeric variable
        ls : iterable containing rules
        how : str
            functions only if type of x is str
            - 'find' : call x.find(rule)
            - 're' : call re.find(rule,x)
            - 'fullmatch' : x == rule
    '''
    if type(x) == str:
        if how == 'find':
            for item in ls:
                if x.find(item) >= 0: return True
        elif how == 're':
            for item in ls:
                if re.findall(item,x): return True
        elif how == 'fullmatch':
            for item in ls:
                item = str(item).strip()
                if item == x: return True
        return False
    else:
        x = int(x)
        ls = [int(i) for i in ls]
        for item in ls:
            if x == item: return True
        return False
   
 
def be_subset(sub,main):
    '''
    return True if sub is a subset of main.
    '''
    res = True
    for i in sub:
        res &= (i in main)
    return res
        

class InteractiveAnswer():
    '''
    an enhanced version for input.

    Parameters
    ----------
    hint : str
        hint string that will be printed before reading an input.
    verify : list-like
        a list that confines the user's input.
    serializer : function
        serialize function that will preprocess user's input.
    encode : dict
        (experimental) replace exact input in keys by values.
        suggest using it only if `verify` is set.
    yes_or_no : bool
        a preset value that will get yes or no questions.

    Examples
    --------
    >>> InteractiveAnswer('Continue?',yes_or_no=True).get()
    Continue?(y/n)
    Continue?(y/n)y
    True

    >>> InteractiveAnswer("What's your name?",serializer=lambda x:x.title()).get()
    What's your name?eric xie
    'Eric Xie'

    >>> InteractiveAnswer("Which level to choose?",verify='12345',serializer=lambda x:x.split()).get()
    Which level to choose?(1-5)1 2
    ['1', '2']

    >>> InteractiveAnswer('How old are you?',verify=range(1,126),serializer=int).get()
    How old are you?(1-125)120
    120
    '''
    def __init__(self,hint='',verify=None,serializer=lambda x:x,encode=None,yes_or_no=False,accept_empty=False):
        if yes_or_no:
            self._verify = 'yn'
            self._serializer = lambda x: x.lower()[0]
            self._encode = {'y':True,'n':False}
            self._accept_empty = False
        else:
            self._verify = verify
            self._serializer = serializer
            self._encode = encode
            self._accept_empty = accept_empty
        self._hint = hint
        if self._verify: 
            try: self._hint += '(' + squeeze_numlist(self._verify) + ')'
            except: self._hint += '('+'/'.join([i for i in list(self._verify)])+')'

    def process(self,get):
        if not self._accept_empty:
            if not get: return

        try:
            get = self._serializer(get)
            get_is_list = type(get) == list
            if self._verify:
                get = get if get_is_list else [get]
                if not be_subset(get,self._verify): return
            if self._encode: get = [self._encode[i] for i in get]
            return get[0] if not get_is_list and len(get) == 1 else get
        except: return

    def get(self):
        while 1:
            get = self.process(input(self._hint).strip())
            if get != None: return get


def space_fill(string,length,align='c',uwidth=2,spcwidth=1):
    '''
    fill spaces to a certain length.

    Parameters
    ----------
    string : str
    length : int
    align : char
        - `c` : centered
        - 'l' : left-aligned
        - 'r' : right-aligned
    uwidth : int
        relative width of utf8 characters with latin characters
    '''
    string = str(string)
    delta = uwidth - 1
    ulen = (len(string.encode('utf-8')) - len(string))//2
    strlen = int(len(string) + delta * ulen)

    if length < strlen: length = strlen
    if align[0] == 'c':
        leftspc = (length-strlen)//2
        rightspc = length-strlen-leftspc
    elif align[0] == 'l':
        leftspc = 0
        rightspc = length-strlen
    elif align[0] == 'r':
        rightspc = 0
        leftspc = length-strlen
    else:
        raise ValueError('align not in [`c`,`l`,`r`]')
    leftspc = int(leftspc/spcwidth)
    rightspc = int(rightspc/spcwidth)
    return ' '*leftspc+string+' '*rightspc


def cstrcmp(str1, str2):
    '''
    compare two strings (or iterables).
    returns the index where str1 is different from str2

    Examples
    --------
    >>> cstrcmp('compare','compulsory')
    -4
    >>> cstrcmp('compulsory','compare')
    4
    >>> cstrcmp('compute','computer')
    -7

    >>> cstrcmp([1,2,3,4,5],[1,2,4,5,6])
    -2
    '''
    i = 0
    while i < min(len(str1),len(str2)):
        try: diff = str1[i] - str2[i] # numeric data support
        except: diff = ord(str(str1[i])) - ord(str(str2[i]))
        if diff: return diff // abs(diff) * i
        i += 1
    return (len(str1) - len(str2)) * min(len(str1),len(str2))


def squeeze_numlist(numlist,sort=False):
    '''
    squeeze a numlist.
    '''
    if sort: numlist = sorted([int(i) for i in numlist])
    length = len(numlist)
    out = []
    while length > 1:
        comp = range(int(numlist[0]),int(numlist[0])+length)
        ind = abs(cstrcmp(numlist,comp))
        if ind == 1: out.append(comp[0])
        else: out.append('%d-%d'%(comp[0],comp[ind-1]))
        
        if ind == 0: break
        numlist = numlist[ind:]
        length = len(numlist)
    return ','.join(out)


def unsqueeze_numlist(numlist):
    '''
    unsqueeze a numlist squeezed by function squeeze_numlist().
    '''
    numlist = [i.split('-') for i in split_wrd(numlist,',')]
    out = []
    for i in numlist:
        if len(i)==1: out.append([int(i[0])])
        else: out.append(list(range(int(i[0]),int(i[1])+1)))
    return sum(out,[])

def colorit(string,color):
    colors = ['black','red','green','yellow','blue','magenta',\
            'cyan','white','gray','lightred','lightgreen','lightyellow',\
            'lightblue','lightmagenta','lightcyan']
    if type(color) == str:
        if color not in colors:
            raise ValueError('Given color',color,'not supported')
        color = colors.index(color)
    else:
        if color not in range(256):
            raise ValueError(color,'is not a 256-color index')
    
    return '\033[38;5;%dm%s\033[0m'%(color,string)
