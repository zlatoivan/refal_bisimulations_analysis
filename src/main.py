import copy
from sent_permut import sentencesPermutation
from pprint import pprint
from syntax_trees import Function, Sentence, String, FuncCall, TermInBrackets, Var, String, TermList, getParser, getSyntaxTrees


def rename_funcs_to_new_eq_cl(func: Function, eqClasses):
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

    def visit_funccall(f: FuncCall):
        f.name = 'cl_' + str(eqClasses[f.name])
        visit_expr(f.expr)

    visit_function(func)

    return func



def bisimilar():
    # Построение синтаксических деревьев
    funcs = open('tests/test_' + 'eq_cl_0' + '.txt', 'r').read().split('\n\n')
    trees = getSyntaxTrees(funcs)
    print()
    for i in range(len(funcs)):
        print(funcs[i], '\n')
        # pprint(trees[i])
        # print('\n\n\n')
    
    # Переставить правила, чтоб биекция была прямая
    sentencesPermutation(trees)

    # Алгоритм разбиения на классы эквивалентности по функциям
    eqClasses = dict()
    for t in trees:
        eqClasses[t.name] = 1
    while True:
        # Переименование функций в новые классы
        treesCl = []
        for t in trees:
            treeCl = rename_funcs_to_new_eq_cl(copy.deepcopy(t), eqClasses)
            treesCl.append(treeCl)

        # Обновление словаря классов эквивалентности
        treesClSet = [t.sentences for t in treesCl]
        for t in treesClSet:
            while treesClSet.count(t) != 1:
                treesClSet.remove(t)

        # for t in treesClSet:
        #     pprint(t)
        #     print()

        eqClOld = copy.deepcopy(eqClasses)
        for t in treesCl:
            eqClasses[t.name] = treesClSet.index(t.sentences)
        # print(eqClasses)

        if eqClasses == eqClOld:
            break

    # Вывести классы эквивалентности
    eqClassesAns = dict()
    for func, cl in eqClasses.items():
        if cl not in eqClassesAns.keys():
            eqClassesAns[cl] = []
        eqClassesAns[cl].append(func)

    for cl, funcs in eqClassesAns.items():
        print('Класс ' + str(cl) + ':', funcs)



if __name__ == '__main__':
    bisimilar()
