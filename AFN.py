import pydot
import webbrowser
from tokens import (alternative, dot, epsilon, optional, kleene, symbols)
from regEx import regEx
from Node import Node

class AFN:
    def __init__(self):
        # Componentes del AFN
        self.states = None
        self.symbols = None
        self.transitions = {}
        self.initial = None
        self.final = None
        self.stack = []

    def __str__(self):
        return (('-' * 100) +
                '\nAFN:\n' +
                ('-' * 100) +
                '\nstates: {}\nsymbols: {}\ntransitions: {}\ninitial: {}\nfinal: {}\n' +
                ('-' * 100)
                ).format(self.states, self.symbols, self.transitions, self.initial, self.final)

    #/-------------------------------Funciones para manejar el stack de la clase AFN-------------------------------/
    #/-------------------------------Funciones para manejar el stack de la clase AFN-------------------------------/
    #/-------------------------------Funciones para manejar el stack de la clase AFN-------------------------------/
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

    #/-------------------------------Funciones para generar el AFN-------------------------------/
    #/-------------------------------Funciones para generar el AFN-------------------------------/
    #/-------------------------------Funciones para generar el AFN-------------------------------/
    def processTokens(self, symbol, i):
        self.transitions[(i, i+1)] = symbol
        self.push(i)
        return i + 2
    def processOr(self, i):
        second_temp_index = self.pop()
        first_temp_index = self.last()
        keys = list(self.transitions)
        keys.sort(reverse=True)
        for key in keys:
            if key[0] >= first_temp_index:
                self.transitions[key[0] + 1, key[1] +
                                 1] = self.transitions.pop(key)
        self.transitions[(first_temp_index,
                          first_temp_index + 1)] = epsilon
        self.transitions[(first_temp_index,
                          second_temp_index + 1)] = epsilon
        self.transitions[(second_temp_index, i + 1)] = epsilon
        self.transitions[(i, i + 1)] = epsilon
        return i + 2
    # Procesa un nodo dot .
    def conatOP(self, i):
        temp_index = self.pop()
        keys = list(self.transitions)
        keys.sort()
        for key in keys:
            if key[0] >= temp_index:
                self.transitions[key[0] - 1, key[1] -
                                 1] = self.transitions.pop(key)
        return i - 1
    # Procesa un nodo kleene *
    def processKleene(self, i):
        temp_index = self.last()
        keys = list(self.transitions)
        keys.sort(reverse=True)
        for key in keys:
            if key[0] >= temp_index:
                self.transitions[key[0] + 1, key[1] +
                                 1] = self.transitions.pop(key)
        self.transitions[(temp_index, temp_index + 1)] = epsilon
        self.transitions[(temp_index, i + 1)] = epsilon
        self.transitions[(i, temp_index + 1)] = epsilon
        self.transitions[(i, i + 1)] = epsilon
        return i + 2
    def processOptional(self, i):
        return self.processOr(self.processTokens(epsilon, i))

    #/-------------------------------Generar el AFN-------------------------------/
    #/-------------------------------Generar el AFN-------------------------------/
    #/-------------------------------Generar el AFN-------------------------------/
    def genNFA(self, root: Node, i=0):
        if root:
            i = self.genNFA(root.left, i)
            i = self.genNFA(root.right, i)
            # Simbolos (a, b, c, d, etc)
            if root.value in symbols:
                return self.processTokens(root.value, i)
            # OR |
            elif root.value == alternative:
                return self.processOr(i)
            # Concatenation .
            elif root.value == dot:
                return self.conatOP(i)
            # Kleene *
            elif root.value == kleene:
                return self.processKleene(i)
            # Optional ?
            elif root.value == optional:
                return self.processOptional(i)
        return i

    def toNFA(self, expression_tree: regEx):
        '''Genera la AFN a partir de un arbol de una expresión'''
        self.genNFA(expression_tree.tree)
        keys = list(self.transitions)
        keys.sort()
        for key in keys:
            self.transitions[key] = self.transitions.pop(key)
        states = list(dict.fromkeys([item for t in keys for item in t]))
        states.sort()
        newTransitions = {}
        for (i, f), t in self.transitions.items():
            if(i, t) not in newTransitions:
                newTransitions[(i, t)] = [f]
            else:
                newTransitions[(i, t)].append(f)
        self.states = states
        self.symbols = list(dict.fromkeys(self.transitions.values()))
        self.transitions = newTransitions
        self.initial = states[0]
        self.final = states[len(states) - 1]

    def showNFA(self):
        with open('AFN.dot', 'w', encoding='utf-8') as file:
            keys = list(self.transitions)
            file.write('digraph{\n')
            file.write('rankdir=LR\n')
            for state in self.states:
                if state == self.initial:
                    file.write('{} [root=true]\n'.format(state))
                    file.write('fake [style=invisible]\n')
                    file.write('fake -> {} [style=bold]\n'.format(state))
                elif state == self.final:
                    file.write('{} [shape=doublecircle]\n'.format(state))
                else:
                    file.write('{}\n'.format(state))
            for key in keys:
                for t in self.transitions[key]:
                    file.write(
                        '{} -> {} [ label="{}" ]\n'.format(key[0], t, key[1]))
            file.write('}\n')
        (graph,) = pydot.graph_from_dot_file('AFN.dot')
        graph.write_png('AFN.png')
        webbrowser.open('AFN.png')

