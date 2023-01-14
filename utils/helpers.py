import re
from collections import Counter

def find_module_codes(text: str):
    # regex pattern for module codes: ie PC1101, DSA3101
    module_code_pattern = r1 = r"(([A-Za-z]){2,3}\d{4}([A-Za-z]){0,1})"
    # find all the instances of module codes
    mentions = [x[0] for x in re.findall(module_code_pattern, text)]

    # get counter
    c = Counter(mentions)

    return dict(c)

def more_than_two_codes(text: str):
    
    # get the dict of unique module code counts
    # eg: {"COS1000":4, "pc1201":1}

    c = find_module_codes(text)

    # if the post got more than 2 module codes

    if len(c.values()) >= 2:
        return True
    
    return False

def keyword_in(text: str, keyword: str):

    # returns whether or not the post contains the search keyword

    c = find_module_codes(text)

    if keyword in c:
        return True
    return False
