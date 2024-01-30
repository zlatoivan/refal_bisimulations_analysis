# from graph import draw_graph
from abc import ABC
from pprint import pprint
import parse as pe
from dataclasses import dataclass
import enum


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


def rename_vars_and_funcs(func: Function):
    varsDict = dict()
    funcDict = dict()

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
        key = str(vType) + '.' + str(vInd)
        if key not in varsDict:
            varsDict[key] = len(varsDict) + 1
        v.index = varsDict[key]
        # print(vType, vInd)

    def visit_funccall(f: FuncCall):
        name = f.name
        if name not in funcDict:
            funcDict[name] = 'func_' + str(len(funcDict) + 1)
        f.name = funcDict[name]
        visit_expr(f.expr)
        # print(name, expr)

    visit_function(func)


def compare(tree1, tree2):
    def visit_function(func1: Function, func2: Function):
        if len(func1.sentences) != len(func2.sentences):
            return False
        ans = True
        for i in range(0, len(func1.sentences)):
            ans = ans and visit_sentence(func1.sentences[i], func2.sentences[i])
        return ans

    def visit_sentence(sent1: Sentence, sent2: Sentence):
        p = visit_pattern(sent1.pattern, sent2.pattern)
        v = visit_expr(sent1.expr, sent2.expr)
        return p and v

    def visit_pattern(tList1: TermList, tList2: TermList):
        if len(tList1) != len(tList2):
            return False
        ans = True
        for i in range(0, len(tList1)):
            tl1 = tList1[i]
            tl2 = tList2[i]
            if type(tl1) == type(tl2) == String:
                ans = ans and visit_string(tl1, tl2)
            if type(tl1) == type(tl2) == Var:
                ans = ans and visit_var(tl1, tl2)
            if type(tl1) == type(tl2) == TermInBrackets:
                ans = ans and visit_pattern(tl1.expr, tl2.expr)
        return ans

    def visit_expr(tList1: TermList, tList2: TermList):
        if len(tList1) != len(tList2):
            return False
        ans = True
        for i in range(0, len(tList1)):
            tl1 = tList1[i]
            tl2 = tList2[i]
            if type(tl1) == type(tl2) == String:
                ans = ans and visit_string(tl1, tl2)
            if type(tl1) == type(tl2) == Var:
                ans = ans and visit_var(tl1, tl2)
            if type(tl1) == type(tl2) == TermInBrackets:
                ans = ans and visit_expr(tl1.expr, tl2.expr)
            if type(tl1) == type(tl2) == FuncCall:
                ans = ans and visit_funccall(tl1, tl2)
        return ans

    def visit_string(s1: String, s2: String):
        str1 = s1.expr
        str2 = s2.expr
        return str1 == str2

    def visit_var(v1: Var, v2: Var):
        vType1 = v1.type
        vInd1 = v1.index
        vType2 = v2.type
        vInd2 = v2.index
        # print(vInd1, vInd2, '\n')
        return (vType1 == vType2 and vInd1 == vInd2)

    def visit_funccall(f1: FuncCall, f2: FuncCall):
        name1 = f1.name
        expr1 = f1.expr
        name2 = f2.name
        expr2 = f2.expr
        # print(name1, name2)
        ans = visit_expr(f1.expr, f2.expr)
        return name1 == name2 and expr1 == expr2 and ans

    return visit_function(tree1, tree2)


def solve():
    p = pe.Parser(NFunction)
    assert p.is_lalr_one()
    p.add_skipped_domain('\\s')

    test_file = 'tests/test_brackets.txt'
    # test_file = 'tests/test_vars_1.txt'
    # test_file = 'tests/test_vars_2.txt'
    # test_file = 'tests/test_eq_cl_1.txt'
    f1, f2 = open(test_file, 'r').read().split('\n---\n')
    
    try:
        tree1 = p.parse(f1)
    except pe.Error as e:
        print(f'Ошибка {e.pos}: {e.message}')

    try:
        tree2 = p.parse(f2)
    except pe.Error as e:
        print(f'Ошибка {e.pos}: {e.message}')

    print()

    rename_vars_and_funcs(tree1)
    rename_vars_and_funcs(tree2)

    print(f1, '\n')
    pprint(tree1)
    print('\n\n\n')

    print(f2, '\n')
    pprint(tree2)
    print('\n\n\n')

    # graph(tree1)

    equal = compare(tree1, tree2)
    
    if equal:
        print('Функции являются бисимуляцией\n')
    else:
        print('Функции не являются бисимуляцией\n')


if __name__ == '__main__':
    solve()



