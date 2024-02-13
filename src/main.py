from eq_classes import getConstFuncClasses, getEqClasses, showEqClassesAndConstFuncs
from sent_permut import sentencesPermutation
from syntax_trees import getSyntaxTrees


def bisimulation():
    print()

    # Входные данные
    file = open('tests/main_test.ref', 'r').read()

    # Построение синтаксических деревьев
    trees = getSyntaxTrees(file)
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
