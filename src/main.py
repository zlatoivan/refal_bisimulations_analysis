import copy
import parse as pe
from pprint import pprint
from parse_prepare import Function, Sentence, String, FuncCall, TermInBrackets, Var, String, TermList, getParser
from bijection import checkSentensesPermutation, getIndexesForCheck, isBijection


def rename_vars_and_funcs(func: Function):
    def visit_function(func: Function):
        name = func.name
        for sent in func.sentences:
            visit_sentence(sent)

    def visit_sentence(sent: Sentence):
        varsDict = dict()
        funcDict = dict()
        visit_pattern(sent.pattern, varsDict, funcDict)
        visit_expr(sent.expr, varsDict, funcDict)

    def visit_pattern(tList: TermList, varsDict, funcDict):
        for term in tList:
            if type(term) is String:
                visit_string(term)
            if type(term) is Var:
                visit_var(term, varsDict)
            if type(term) is TermInBrackets:
                visit_pattern(term.expr, varsDict, funcDict)

    def visit_expr(tList: TermList, varsDict, funcDict):
        for term in tList:
            if type(term) is String:
                visit_string(term)
            if type(term) is Var:
                visit_var(term, varsDict)
            if type(term) is TermInBrackets:
                # print('in')
                visit_expr(term.expr, varsDict, funcDict)
            if type(term) is FuncCall:
                visit_funccall(term, varsDict, funcDict)

    def visit_string(s: String):
        str = s.expr

    def visit_var(v: Var, varsDict):
        vType = v.type
        vInd = v.index
        key = str(vType) + '.' + str(vInd)
        if key not in varsDict:
            varsDict[key] = len(varsDict) + 1
        v.index = varsDict[key]
        # print(vType, vInd)

    def visit_funccall(f: FuncCall, varsDict, funcDict):
        name = f.name
        if name not in funcDict:
            funcDict[name] = 'func_' + str(len(funcDict) + 1)
        f.name = funcDict[name]
        # f.name = 'cl_1'
        visit_expr(f.expr, varsDict, funcDict)
        # print(name, expr)

    visit_function(func)

    return func


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
    test_files = [
        'classes',
        'brackets',
        'vars_1',
        'vars_2',
        'eq_cl_0',
        'eq_cl_1',
        'eq_cl_2',
        'perest',
    ]

    # Парсер
    p = getParser()

    funcs = open('tests/test_' + 'eq_cl_0' + '.txt', 'r').read().split('\n\n')
    
    # Построение синтаксических деревьев
    print()
    trees = []
    treesCl = []
    for f in list(funcs):
        try:
            tree = p.parse(f)
            trees.append(tree)
            # Переименовать переменные и функции на порядковый номер первого вхождения в правило
            treeCl = rename_vars_and_funcs(copy.deepcopy(tree))
            treesCl.append(treeCl)
        except pe.Error as e:
            print(f'Ошибка {e.pos}: {e.message}')

    for i in range(len(funcs)):
        print(funcs[i], '\n')
        # pprint(trees[i])
        pprint(treesCl[i])
        print('\n\n\n')

    # Проверить биекцию правил
    sentences1 = treesCl[0].sentences
    sentences2 = treesCl[1].sentences

    if not isBijection(sentences1, sentences2):
        print('Биекции нет\n')
        return
    print('Биекция есть\n')
    
    # Получить правила, которые проверить на перестановочность
    indexesForCheck = getIndexesForCheck(copy.deepcopy(sentences1), copy.deepcopy(sentences2))
    print('Проверить на перестановочность правила под номерами:')
    for i in indexesForCheck:
        print(i[0], i[1])
    print()

    # Проверить перестановочность правил
    ind = checkSentensesPermutation(sentences1, indexesForCheck)
    if ind:
        print('Предложения', ind[0], 'и', ind[1], 'не перестановочны\n')
        return
    print('Перестановочность есть\n')




    
    # Переставить, чтоб было полное соответствие
    # sentences1[0], sentences1[1] = sentences1[1], sentences1[0]

    # for i in range(len(funcs)):
    #     print(funcs[i], '\n')
    #     # pprint(trees[i])
    #     pprint(treesCl[i])
    #     print('\n\n\n')
    
    # Алгоритм разбиения на классы эквивалентности по функциям

    # print(treesCl[0].sentences == treesCl[1].sentences)
    # print(sentences1 == sentences2)
    

    

if __name__ == '__main__':
    solve()



# graph(tree1)

# equal = compare(trees[0], trees[1])
# if equal:
    # print('Функции являются бисимуляцией\n')
# else:
    # print('Функции не являются бисимуляцией\n')
