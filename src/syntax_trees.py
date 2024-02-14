from dataclasses import dataclass
from abc import ABC
import parser_edsl as pe
from pprint import pprint


class Term(ABC):
    pass
    
@dataclass
class TermList:
    exprs: list[Term]

@dataclass
class String(Term):
    expr: str

@dataclass
class Identifier(Term):
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
class Condition(Term):
    expr: TermList
    pattern: TermList

@dataclass
class Sentence:
    pattern: TermList
    conditions: TermList
    expr: TermList

@dataclass
class Function:
    name: str
    sentences: list[Sentence]

@dataclass
class Program:
    funcs: list[Function]


# Нетерминальные символы
s = """Program Function FuncName Sentences Sentence Pattern Conditions Expr Term1 Term2 Symbol Variable Type Index """
NProgram, NFunction, NFuncName, NSentences, NSentence, NPattern, NConditions, NExpr, NPatternTerm, NExprTerm, NSymbol, NVariable, NType, NIndex\
    = map(pe.NonTerminal, s.split())


# Терминальные символы
FUNC_IDENTIFIER = pe.Terminal('FUNC_IDENTIFIER', '[A-Z][A-Za-z0-9-_!]{0,32}', str)
STRING = pe.Terminal('STRING', '\'[A-Za-z0-9]+\'|[0-9a-df-ru-z]+|[ste][a-z0-9]+', str)
TYPE = pe.Terminal('TYPE', '[ste]{1}', str)
VAR_IDENTIFIER = pe.Terminal('VAR_IDENTIFIER', '[.][A-Za-z0-9][A-Za-z0-9-_]{0,32}', str)
# INTEGER = pe.Terminal('INTEGER', '[1-9][0-9]*', str)


# Правила грамматики
NProgram |= NFunction, lambda x: x
NProgram |= NProgram, NFunction, lambda xs, x: xs + x
# NProgram |= NProgram, COMMENT , lambda x, c: [x]

NFunction |= '$ENTRY', NFuncName, '{', NSentences, '}', lambda n, s: []
NFunction |= NFuncName, '{', NSentences, '}', lambda n, s: [Function(n, s)]
NFuncName |= FUNC_IDENTIFIER
NSentences |= NSentence, ';', lambda x: [x]
NSentences |= NSentences, NSentence, ';', lambda xs, x: xs + [x]
NSentences |= NSentences, NSentence, lambda xs, x: xs + [x]
NSentence |= NPattern, NConditions, '=', NExpr, lambda p, c, e: Sentence(p, c, e)
NConditions |= lambda: []
NConditions |= NConditions, ',', NExpr, ':', NPattern, lambda conds, ex, pat: conds + [Condition(ex, pat)]

NPattern |= lambda: []
NPattern |= NPattern, NPatternTerm, lambda xs, x: xs + [x]
NPatternTerm |= STRING, lambda c: String(c)
NPatternTerm |= FUNC_IDENTIFIER, lambda c: String(c)
NPatternTerm |= '"', FUNC_IDENTIFIER, '"', lambda c: String(c)
NPatternTerm |= NVariable, lambda c: Var(c.type, c.index)
NPatternTerm |= '(', NPattern, ')', lambda c: TermInBrackets(c)
NPatternTerm |= ',', 

NExpr |= lambda: []
NExpr |= NExpr, NExprTerm, lambda xs, x: xs + [x]
NExprTerm |= STRING, lambda c: String(c)
NExprTerm |= FUNC_IDENTIFIER, lambda c: String(c)
NExprTerm |= '"', FUNC_IDENTIFIER, '"', lambda c: String(c)
# NExprTerm |= INTEGER, lambda c: (list(c))
NExprTerm |= NVariable, lambda c: Var(c.type, c.index)
NExprTerm |= '(', NExpr, ')', lambda c: TermInBrackets(c)
NExprTerm |= '<', NFuncName, NExpr, '>', lambda c, q: FuncCall(c, q)

NVariable |= NType, NIndex, lambda t, i: Var(t, i)
NType |= TYPE
NIndex |= VAR_IDENTIFIER


def splitStringToChar(func: Function):
    def visit_function(func: Function):
        for sent in func.sentences:
            visit_pattern(sent.pattern)
            visit_expr(sent.expr)

    def visit_pattern(tList: TermList):
        i = 0
        while i < len(tList):
            term = tList[i]
            if type(tList[i]) == String:
                j = i
                sNew = '\''
                while j < len(tList) - 1 and type(tList[j]) == type(tList[j + 1]) == String and tList[j].expr[0] == tList[j].expr[-1] == tList[j + 1].expr[0] == tList[j + 1].expr[-1]:
                    sNew += tList[j].expr.replace('\'', '')
                    j += 1
                sNew += tList[j].expr.replace('\'', '') + '\''
                # print(i, j, sNew)
                for _ in range(i, j + 1):
                    tList.pop(i)
                tList.insert(i, String(sNew))
            if type(term) is TermInBrackets:
                visit_pattern(term.expr)
            i += 1

    def visit_expr(tList: TermList):
        i = 0
        while i < len(tList):
            term = tList[i]
            if type(tList[i]) == String:
                j = i
                sNew = '\''
                while j < len(tList) - 1 and type(tList[j]) == type(tList[j + 1]) == String and tList[j].expr[0] == tList[j].expr[-1] == tList[j + 1].expr[0] == tList[j + 1].expr[-1]:
                    sNew += tList[j].expr.replace('\'', '')
                    j += 1
                sNew += tList[j].expr.replace('\'', '') + '\''
                # print(i, j, sNew)
                for _ in range(i, j + 1):
                    tList.pop(i)
                tList.insert(i, String(sNew))
            # Можно было так разбить строку на массив чаров, но так возиться дольше
            # if type(term) == String and len(term.expr) > 3 and term.expr[0] == term.expr[-1] == '\'':
            #     sNew = term.expr.replace('\'', '')
            #     sNew = ['\'' + st + '\'' for st in [*sNew]]
            #     sNew = [String(st) for st in sNew]                
            #     # print('@@@', term.expr, ' -> ', sNew)
            #     tList.pop(i)
            #     for ch in sNew[::-1]:
            #         tList.insert(i, ch)
            if type(term) is TermInBrackets:
                visit_expr(term.expr)
            if type(term) is FuncCall:
                visit_funccall(term)
            i += 1

    def visit_funccall(f: FuncCall):
        visit_expr(f.expr)

    visit_function(func)

    return func


def getParser():
    p = pe.Parser(NProgram)
    # assert p.is_lalr_one()  # Не вып. из-за conditions :(
    p.add_skipped_domain('\\s')
    # p.add_skipped_domain('/\*[^/]\*/')
    p.add_skipped_domain('\*.*?\n|/\*(.|\n)*?\*/')
    return p


def getSyntaxTrees(file):
    p = getParser()

    # # Вывести токены:
    # try:
    #     for token in p.tokenize(file):
    #         print(token.pos, token)
    # except pe.Error as e:
    #     print(f'Ошибка {e.pos}: {e.message}')
    # print('\n---------------------------------------------\n')


    trees = []
    try:
        trees = p.parse(file)
    except pe.Error as e:
        print(f'Ошибка {e.pos}: {e.message}\n')
        return False
    
    for t in trees:
        splitStringToChar(t)
    
    # print(file, '\n')
    pprint(trees)

    return trees
