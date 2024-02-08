from eq_classes import getConstFuncClasses, getEqClasses, showEqClassesAndConstFuncs
from sent_permut import sentencesPermutation
from syntax_trees import getSyntaxTrees


def bisimulation():
    print()

    # Входные данные
    funcs = open('tests/test_' + 'eq_cl_1' + '.txt', 'r').read().split('\n\n')

    # Построение синтаксических деревьев
    trees = getSyntaxTrees(funcs)
    if not trees: return
    
    # Переставить правила, чтоб биекция была прямой
    sentencesPermutation(trees)

    # Алгоритм разбиения на классы эквивалентности по функциям
    eqClasses = getEqClasses(trees)

    # Выявить константные функции
    constFuncClasses = getConstFuncClasses(trees)
    
    # Вывести классы эквивалентности и константные функции
    showEqClassesAndConstFuncs(eqClasses, constFuncClasses)

    print()


if __name__ == '__main__':
    bisimulation()
