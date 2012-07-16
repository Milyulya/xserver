#all of these need better return messages, but they at least catch the right stuff. 
import re

def strip_comments(code):
    codeLines = code.splitlines()
    newCode = ''
    for line in codeLines:
        com = line.find('#')
        if com >= 0: line = line[:com]
        newCode = newCode + line + "\n"
    return newCode

def check_booleans(code):
    code = strip_comments(code)
    regex = re.search('==\s*True|==\s*False', code)
    return "Comparison to boolean found at " + str(regex.start())

def check_docstring(code):
    code = strip_comments(code)
    code = code.splitlines()
    # find bracketed expressions
    code_iter = code.__iter__()
    for line in code_iter:
        if line.find('def')>=0:
            try:
                line = code_iter.next()
            except StopIteration:
                break
            if not line.find("\"\"\"")>=0:
                return "No docstring found at "+ line
    return False

def count_leading_whitespace(line):
    indent_size = 0
    for char in line:
        if char.isspace():
            indent_size += 1
        else:
            break
    return indent_size

def check_changing_collection(code):
    altering_methods = [".append", ".extend", ".insert", ".remove", ".pop", ".sort"]
    code = strip_comments(code)
    code = code.splitlines()
    code_iter = code.__iter__()
    line = code_iter.next()
    while True:
        if 'for' in line and 'in' in line:
            collection_name = line[ line.find('in') + 2 : -1] #cut off the colon
            try:
                line = code_iter.next()
                indent_size = count_leading_whitespace(line)
                while count_leading_whitespace(line) >= indent_size:
                    collection_reference_location = line.find(collection_name)
                    if collection_reference_location >= 0:
                        for method in altering_methods:
                            method_start = collection_reference_location + len(collection_name)
                            if line [method_start : method_start + len(method)] == method:
                                return "Collection "+collection_name+" altered in loop over self"
                    line = code_iter.next()
            except StopIteration:
                break
        else:
            try:
                line = code_iter.next()
            except StopIteration:
                break
    return False


def check_super_usage(code):
    code = strip_comments(code)
    code = code.splitlines()
    classes = []
    super_classes = {}
    classes_init = {}
    code_iter = code.__iter__()
    for line in code_iter:
        classStart = line.find('class')
        parenStart = line.find('(')
        parenEnd = line.find(')')
        if classStart < 0 or parenStart < 0 or parenEnd < 0:
            continue
        
        className = line[classStart+5 : parenStart].replace(' ','')
        classes.append(className)
        if parenStart + 1 < parenEnd:
            parents = line [parenStart+1 : parenEnd].split(',')
            try:
                parents.remove('object')
            except ValueError:
                pass
            super_classes[className] = parents
        else:
            super_classes[className]=[]
        try:
            line = code_iter.next()
            indent_size = count_leading_whitespace(line)
            while count_leading_whitespace(line) >= indent_size:
                if '__init__' in line:
                    line = code_iter.next()
                    classes_init[className] = ""
                    init_func_indent = count_leading_whitespace(line)
                    while count_leading_whitespace(line) >= init_func_indent:
                        classes_init[className] += '\n'+line
                        line = code_iter.next()
                else:
                    line = code_iter.next()
        except StopIteration:
            pass
    for user_class in classes:
        for super_class in super_classes[user_class]:
            if classes_init[super_class] in classes_init[user_class]:
                return user_class+" should call the constructor of "+super_class+" in its constructor"
    return False

def check_static_style_guide(code):
    ans = False
    ans = ans or check_booleans(code)
    ans = ans or check_docsring(code)
    ans = ans or check_changing_collection(code)
    ans = ans or check_super_usage(code)
    return ans

answer = """
def calc_payments(balance, interest):
    \"\"\"
    contains a docstring
    \"\"\"
    payment = 0
    monthly_interest = interest/(12.0)
    calced_balance = balance
    while calced_balance > 0:
        calced_balance = balance
        payment += 10
        for i in range(12):
            calced_balance -= payment
            calced_balance *= 1+monthly_interest
    return payment
        
""" 
if check_docstring(answer):
    print "error! 1"

my_test_string = "if a == False:   return 7"
if not isinstance(check_booleans(my_test_string), str):
    print "error! 2"


if check_changing_collection(answer):
    print "error! 3"

answer = """
def calc_payments(balance, interest):
    \"\"\"
    contains a docstring
    \"\"\"
    elems = [1,2,3]
    for e in elems:
        print e
        elems.remove(e)
    return elems
""" 

if not isinstance( check_changing_collection(answer), str):
    print "error! 4"

answer = """
def calc_payments(balance, interest):
    \"\"\"
    contains a docstring
    \"\"\"
    elems = [1,2,3]
    for e in elems:
        print e
        elems.index(e)
    return elems
""" 

if check_changing_collection(answer):
    print "error! 5"

incorrect_inheritance = """
class SimpleVirus(object):
    def __init__(self, maxBirthProb, clearProb):
        self.maxBirthProb = maxBirthProb
        self.clearProb = clearProb

class ResistantVirus(SimpleVirus):
    def __init__(self, maxBirthProb, clearProb, resistances, mutProb):
        self.maxBirthProb = maxBirthProb
        self.clearProb = clearProb
        self.resistances = resistances
        self.mutProb = mutProb
"""

correct_inheritance = """
class SimpleVirus(object):
    def __init__(self, maxBirthProb, clearProb):
        self.maxBirthProb = maxBirthProb
        self.clearProb = clearProb

class ResistantVirus(SimpleVirus):
    def __init__(self, maxBirthProb, clearProb, resistances, mutProb):
        SimpleVirus.__init__(self, maxBirthProb, clearProb)
        self.resistances = resistances
        self.mutProb = mutProb
"""

if check_super_usage(correct_inheritance):
    print "error! 6"
if not isinstance(check_super_usage(incorrect_inheritance), str):
    print "error! 7"
