from eq_classes import getConstFuncClasses, getEqClasses, showEqClassesAndConstFuncs
from sent_permut import sentencesPermutation
from syntax_trees import getSyntaxTrees
import sys

def bisimulation():
    print()

    # Входные данные
    filename = sys.argv[1]
    # filename = 'tests/main_test.ref'
    data = open(filename, 'r').read()

    # Построение синтаксических деревьев
    trees = getSyntaxTrees(data)
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
