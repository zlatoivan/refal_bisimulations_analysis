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
FUNC_IDENTIFIER = pe.Terminal('FUNC_IDENTIFIER', '[A-Z][A-Za-z0-9-_]{0,14}', str)
STRING = pe.Terminal('STRING', '\'[A-Za-z0-9]+\'', str)
TYPE = pe.Terminal('TYPE', '[ste]{1}', str)
VAR_IDENTIFIER = pe.Terminal('VAR_IDENTIFIER', '[.][A-Za-z0-9][A-Za-z0-9-_]{0,14}', str)
# INTEGER = pe.Terminal('INTEGER', '[1-9][0-9]*', str)


# Правила грамматики
NFunction |= NFuncName, '{', NSentences, '}', Function
NFuncName |= FUNC_IDENTIFIER
NSentences |= NSentence, ';', lambda x: [x]
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

NVariable |= NType, NIndex, lambda t, i: Var(t, i)
NType |= TYPE
NIndex |= VAR_IDENTIFIER


def getParser():
    p = pe.Parser(NFunction)
    assert p.is_lalr_one()
    p.add_skipped_domain('\\s')
    return p


def getSyntaxTrees(funcs):
    p = getParser()

    # # Вывести токены:
    # try:
    #     for token in p.tokenize(funcs[0]):
    #         print(token.pos, token)
    # except pe.Error as e:
    #     print(f'Ошибка {e.pos}: {e.message}')
    # print('\n---------------------------------------------\n')


    trees = []
    for f in list(funcs):
        try:
            tree = p.parse(f)
            trees.append(tree)
        except pe.Error as e:
            print(f'Ошибка {e.pos}: {e.message}\n')
            return False

    for i in range(len(funcs)):
        print(funcs[i], '\n')
        # pprint(trees[i])
        # print('\n\n\n')
    print()

    return trees
