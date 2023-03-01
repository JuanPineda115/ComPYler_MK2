from tokens import (alternative, closingGroup, closingIteration,
                           closingOption, dot, epsilon,
                           openingGroup, openingIteration, openingOption,
                           optional, kleene, symbols)
from Node import Node

class regEx:
    def __init__(self, regex):
        self.regex = regex
        self.tree = None
        self.nodes = {}
        self.postfix = []
        self.lastChar = None
        # Precedencias de los operadores
        self.precedence = {
            alternative: 1,
            dot: 2,
            optional: 3,
            kleene: 3
        }
        # Funciones calculadas a partir del árbol sintáctico
        self.nullable = {}
        self.firstpos = {}
        self.lastpos = {}
        self.nextpos = {}
        # Stack del AFN
        self.stack = []
    
    #/-------------------------------Funciones para manejar el stack de la clase-------------------------------/
    #/-------------------------------Funciones para manejar el stack de la clase-------------------------------/
    #/-------------------------------Funciones para manejar el stack de la clase-------------------------------/
    def is_empty(self):
        return len(self.stack) == 0
    def last(self):
        return self.stack[-1]
    def pop(self):
        if not self.is_empty():
            return self.stack.pop()
        else:
            BaseException("Error")
    def push(self, op):
        self.stack.append(op)

    #/------------------------------- Balanceo de la expresion regular -------------------------------/
    #/------------------------------- Balanceo de la expresion regular -------------------------------/
    #/------------------------------- Balanceo de la expresion regular -------------------------------/
    def checkExpression(self):
        operators = {'*', '+', '?', '|', '^'}
        stack = []
        for i, token in enumerate(self.regex):
            if token in '([{':
                stack.append((token, i))
            elif token in ')]}':
                if not stack:
                    raise ValueError(f"Unbalanced {token} at position {i}")
                opening_token, opening_index = stack.pop()
                if (opening_token == '(' and token != ')') or \
                    (opening_token == '[' and token != ']') or \
                        (opening_token == '{' and token != '}'):
                    raise ValueError(
                        f"Mismatched {opening_token} and {token} at positions {opening_index} and {i}")
            elif token in operators-{'|'}:
                if i == 0 or self.regex[i - 1] in operators.union({'(', '[', '{', '|'}):
                    raise ValueError(f"Invalid use of {token} at position {i}")
                elif token == '^' and i != 1:
                    raise ValueError(f"Invalid use of {token} at position {i}")
                elif token == '*' and self.regex[i - 1] in operators.union({'('}) and self.regex[i - 1] != '|':
                    raise ValueError(f"Invalid use of {token} at position {i}")
                elif token == '+' and self.regex[i - 1] in operators.union({'('}) and self.regex[i - 1] != '|':
                    raise ValueError(f"Invalid use of {token} at position {i}")
                elif token == '?' and self.regex[i - 1] in operators.union({'('}) and self.regex[i - 1] != '|':
                    raise ValueError(f"Invalid use of {token} at position {i}")
            elif token == '|':
                if i == 0 or i == len(self.regex) - 1:
                    raise ValueError(f"Invalid use of {token} at position {i}")
                elif self.regex[i - 1] in operators.union({'|', '('})-{'*', '?'}:
                    raise ValueError(f"Invalid use of {token} at position {i}")
                elif self.regex[i + 1] in operators.union({')', '|'}):
                    raise ValueError(f"Invalid use of {token} at position {i}")
        if stack:
            opening_token, opening_index = stack.pop()
            raise ValueError(
                f"Unbalanced {opening_token} at position {opening_index}")
        else:
            return True

    #/------------------------------- Generacion del postfix -------------------------------/
    #/------------------------------- Generacion del postfix -------------------------------/
    #/------------------------------- Generacion del postfix -------------------------------/
    # Revisa la precedencia entre dos operadores
    def getPrecedence(self, i):
        try:
            return self.precedence[i] <= self.precedence[self.last()]
        except:
            BaseException("Error")
    # Procesa la concatenacion (dot) 
    def conatOP(self, c):
        # Si el siguiente caracter es algun simbolo o un ( o { o [
        # y el anterior simbolo fue algun simbolo o un ) o } o ] o ? o *
        if (c in [*symbols, openingGroup, openingIteration, openingOption] and
                self.lastChar in [*symbols, closingGroup, closingIteration, closingOption, optional, kleene]):
            self.processToken(dot)
    def processOper(self, c):
        # Se agrega a postfix hasta que haya un operador con menor jerarquía en el stack
        while (not self.is_empty() and self.getPrecedence(c)):
            self.postfix.append(self.pop())
        self.push(c)
    def processToken(self, c):
        # Si es algun simbolo o un ( o { o [ se extraen todos los operadores de un solo simbolo ? o *
        if c in [*symbols, openingGroup, openingIteration, openingOption]:
            while (not self.is_empty() and self.last() in [optional, kleene]):
                self.postfix.append(self.pop())
        if c in symbols:
            self.postfix.append(c)
        elif c in [openingGroup, openingIteration, openingOption]:
            self.push(c)
        elif c == closingGroup:
            while not self.is_empty() and self.last() != openingGroup:
                a = self.pop()
                self.postfix.append(a)
            if self.is_empty() or self.last() != openingGroup:
                BaseException("Error")
            else:
                self.pop()
        elif c == closingIteration:
            while not self.is_empty() and self.last() != openingIteration:
                a = self.pop()
                self.postfix.append(a)
            if self.is_empty() and self.last() != openingIteration:
                BaseException("Error")
            else:
                self.pop()
                self.processOper(kleene)
        elif c == closingOption:
            while not self.is_empty() and self.last() != openingOption:
                a = self.pop()
                self.postfix.append(a)
            if self.is_empty() and self.last() != openingOption:
                BaseException("Error")
            else:
                self.pop()
                self.processOper(optional)
        else:
            self.processOper(c)
        self.lastChar = c

    def toPostfix(self):
        self.lastChar = None
        for c in self.regex:
            self.conatOP(c)
            self.processToken(c)
        while not self.is_empty():
            self.postfix.append(self.pop())

    #/------------------------------- Generacion del arbol -------------------------------/
    #/------------------------------- Generacion del arbol -------------------------------/
    #/------------------------------- Generacion del arbol -------------------------------/
    def genTree(self, node: Node, i=0):
        if node:
            i = self.genTree(node.left, i)
            i = self.genTree(node.right, i)
            node.id = i
            self.nodes[i] = node.value
            # Se calcula el valor de nullable(n), firstpos(n) y lastpos(n)
            if node.value == epsilon:
                self.nullable[node.id] = True
                self.firstpos[node.id] = []
                self.lastpos[node.id] = []
            elif node.value in symbols:
                self.nullable[node.id] = False
                self.firstpos[node.id] = [node.id]
                self.lastpos[node.id] = [node.id]
            elif node.value == alternative:
                self.nullable[node.id] = self.nullable[node.left.id] or self.nullable[node.right.id]
                self.firstpos[node.id] = [
                    *self.firstpos[node.left.id], *self.firstpos[node.right.id]]
                self.lastpos[node.id] = [
                    *self.lastpos[node.left.id], *self.lastpos[node.right.id]]
            elif node.value == dot:
                self.nullable[node.id] = self.nullable[node.left.id] and self.nullable[node.right.id]
                self.firstpos[node.id] = [*self.firstpos[node.left.id], *self.firstpos[node.right.id]] if self.nullable[node.left.id] else self.firstpos[node.left.id]
                self.lastpos[node.id] = [*self.lastpos[node.left.id], *self.lastpos[node.right.id]] if self.nullable[node.right.id] else self.lastpos[node.right.id]
            elif node.value in [kleene, optional]:
                self.nullable[node.id] = True
                self.firstpos[node.id] = self.firstpos[node.left.id]
                self.lastpos[node.id] = self.lastpos[node.left.id]
            # Se calcula el valor de nextpos(n)
            if node.value == dot:
                for lastpos in self.lastpos[node.left.id]:
                    if lastpos in self.nextpos.keys():
                        self.nextpos[lastpos] = list(dict.fromkeys([
                            *self.nextpos[lastpos], *self.firstpos[node.right.id]]))
                    else:
                        self.nextpos[lastpos] = self.firstpos[node.right.id]
                    self.nextpos[lastpos].sort()
            elif node.value == kleene:
                for lastpos in self.lastpos[node.left.id]:
                    if lastpos in self.nextpos.keys():
                        self.nextpos[lastpos] = list(dict.fromkeys([
                            *self.nextpos[lastpos], *self.firstpos[node.left.id]]))
                    else:
                        self.nextpos[lastpos] = self.firstpos[node.left.id]
                    self.nextpos[lastpos].sort()
            return i + 1
        return i

    #/------------------------------- Funciones -------------------------------/
    #/------------------------------- Funciones -------------------------------/
    #/------------------------------- Funciones -------------------------------/
    def getTree(self):
        for c in self.postfix:
            if c in symbols:
                self.push(Node(c))
            else:
                op = Node(c)
                if c in [optional, kleene]:
                    x = self.pop()
                else:
                    y = self.pop()
                    x = self.pop()
                    op.right = y
                op.left = x
                self.push(op)
        self.tree = self.pop()
        self.genTree(self.tree)

    def search_by_id(self, id):
        if id in self.nodes.keys():
            return self.nodes[id]
        return None
