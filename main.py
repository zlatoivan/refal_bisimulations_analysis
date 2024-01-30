# from graph import draw_graph
from abc import ABC
import enum
from pprint import pprint
import parse as pe
from dataclasses import dataclass


# class Type(enum.Enum):
#     s = 's'
#     t = 't'
#     e = 'e'


class Term(ABC):
    pass
    
@dataclass
class TermList:
    exprs: list[Term]

@dataclass
class String(Term):
    expr: str

@dataclass
class Var(Term):
    type: str
    index: String

@dataclass
class TermInBrackets(Term):
    expr: TermList

@dataclass
class FuncCall(Term):
    name: str
    expr: Term


@dataclass
class Sentence:
    pattern: TermList
    expr: TermList

@dataclass
class Function:
    name: str
    sentences: list[Sentence]


# Нетерминальные символы
s = """Function FuncName Sentences Sentence Pattern Expr Term1 Term2 Symbol Variable Type Index """
NFunction, NFuncName, NSentences, NSentence, NPattern, NExpr, NPatternTerm, NExprTerm, NSymbol, NVariable, NType, NIndex\
    = map(pe.NonTerminal, s.split())


# Терминальные символы
IDENTIFIER = pe.Terminal('IDENTIFIER', '[A-Z][A-Za-z0-9-_]{0,14}', str)
INTEGER = pe.Terminal('INTEGER', '[1-9][0-9]*', str)
STRING = pe.Terminal('STRING', '\'[A-Za-z0-9]+\'', str)
TYPE = pe.Terminal('TYPE', '[s,t,e]{1}', str)

# def make_keyword(image):
#     return pe.Terminal(image, image, lambda name: None, re_flags=re.IGNORECASE, priority=10)

# KW_S, KW_T, KW_E, KW_INTEGER, KW_REAL, KW_BOOLEAN = \
#     map(make_keyword, 's t e integer real boolean'.split())


# Правила грамматики
NFunction |= NFuncName, '{', NSentences, '}', Function
NFuncName |= IDENTIFIER
NSentences |= lambda: []
NSentences |= NSentences, NSentence, ';', lambda xs, x: xs + [x]
NSentence |= NPattern, '=', NExpr, lambda p, e: Sentence(p, e)

NPattern |= lambda: []
NPattern |= NPattern, NPatternTerm, lambda xs, x: xs + [x]
NPatternTerm |= STRING, lambda c: String(c)
NPatternTerm |= NVariable, lambda c: Var(c.type, c.index)
NPatternTerm |= '(', NPattern, ')', lambda c: TermInBrackets(c)

NExpr |= lambda: []
NExpr |= NExpr, NExprTerm, lambda xs, x: xs + [x]
NExprTerm |= STRING, lambda c: String(c)
# NExprTerm |= INTEGER, lambda c: (list(c))
NExprTerm |= NVariable, lambda c: Var(c.type, c.index)
NExprTerm |= '(', NExpr, ')', lambda c: TermInBrackets(c)
NExprTerm |= '<', NFuncName, NExpr, '>', lambda c, q: FuncCall(c, q)

NVariable |= NType, '.', NIndex, lambda t, i: Var(t, i)
NType |= TYPE
NIndex |= IDENTIFIER
NIndex |= INTEGER
# NType |= KW_S, lambda: Type.s
# NType |= KW_T, lambda: Type.t
# NType |= KW_E, lambda: Type.e
# NType |= 'e'


def visit_function(func: Function):
        name = func.name
        for sent in func.sentences:
            visit_sentence(sent)

def visit_sentence(sent: Sentence):
    visit_pattern(sent.pattern)
    visit_expr(sent.expr)

def visit_pattern(tList: TermList):
    for term in tList:
        if type(term) is String:
            visit_string(term)
        if type(term) is Var:
            visit_var(term)
        if type(term) is TermInBrackets:
            visit_pattern(term.expr)

def visit_expr(tList: TermList):
    for term in tList:
        if type(term) is String:
            visit_string(term)
        if type(term) is Var:
            visit_var(term)
        if type(term) is TermInBrackets:
            # print('in')
            visit_expr(term.expr)
        if type(term) is FuncCall:
            visit_funccall(term)

def visit_string(s: String):
    str = s.expr

def visit_var(v: Var):
    vType = v.type
    vInd = v.index
    # print(vType, vInd)

def visit_funccall(f: FuncCall):
    name = f.name
    expr = f.expr
    # print(name, expr)


def solve():
    p = pe.Parser(NFunction)
    assert p.is_lalr_one()
    p.add_skipped_domain('\\s')
    p.add_skipped_domain('(\\(\\*|\\{).*?(\\*\\)|\\})')

    file1 = open('function1.txt', 'r').read()
    file2 = open('function2.txt', 'r').read()
    
    try:
        tree1 = p.parse(file1)
    except pe.Error as e:
        print(f'Ошибка {e.pos}: {e.message}')

    try:
        tree2 = p.parse(file2)
    except pe.Error as e:
        print(f'Ошибка {e.pos}: {e.message}')


    print()

    print(file1, '\n')
    pprint(tree1)
    print('\n\n\n')

    print(file2, '\n')
    pprint(tree2)
    print('\n\n\n')

    print('#')
    visit_function(tree1)
    visit_function(tree2)

    # graph(tree1)


if __name__ == '__main__':
    solve()



