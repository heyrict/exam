from string import ascii_letters as letters

def count_iter(it):
    '''
    count item in a given iterator.

    Parameters
    ----------
    string : iterable

    Examples
    --------
    >>> count_iter([1,1,2,2,2,3])
    {1: 2, 2: 3, 3: 1}
    
    >>> count_iter(['a','a','b','b','b','c'])
    {'a': 2, 'c': 1, 'b': 3}

    '''
    d = dict()
    allitems = set(it)
    for i in allitems:
        d[i] = it.count(i)
    return d


def count_alpha(string):
    '''
    count all alphabets in a string.
    
    Parameters
    ----------
    string : str

    Examples
    --------
    >>> count_alpha('I am a string. Am I?')
    {'a': 3, 'g': 1, 'i': 3, 'm': 2, 'n': 1, 's': 1, 'r': 1, 't': 1}

    '''
    return count_iter([i for i in string.lower() if i in letters])


def count_words(string,sep=list(' ,./><?!`~;:\'\"][{}=+-_)(*&^%$#@|\\\n\r\t')):
    '''
    count words in string separated by given symbols.

    Parameters
    ----------
    string : str
    sep    : str or list of str

    Example
    -------
    >>> count_words(w)
    {'i': 2, 'a': 1, 'am': 2, 'string': 1}

    '''
    return count_iter(split_wrd(string.lower(),sep))
