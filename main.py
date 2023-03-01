# import toNFA 
from regEx import *
from AFN import *

# ask for the regular expression
while True:
    regex = regEx(input("Enter the regular expression: "))
    if(regex.checkExpression()):
        regex.toPostfix()
        print("Postfix expression", ''.join(regex.postfix))
        regex.getTree()
        afn = AFN()
        afn.toNFA(regex)
        print(afn)
        afn.showNFA()
    else:
        break