import copy
from syntax_trees import Function, Sentence, String, FuncCall, TermInBrackets, Var, String, TermList, getParser, getSyntaxTrees


def rename_vars__to_its_first_and_funcs_to_eq_cl(func: Function, eqClasses):
    def visit_function(func: Function):
        for sent in func.sentences:
            visit_sentence(sent)

    def visit_sentence(sent: Sentence):
        varsDict = dict()
        visit_pattern(sent.pattern, varsDict)
        visit_expr(sent.expr, varsDict)

    def visit_pattern(tList: TermList, varsDict):
        for term in tList:
            if type(term) is Var:
                visit_var(term, varsDict)
            if type(term) is TermInBrackets:
                visit_pattern(term.expr, varsDict)

    def visit_expr(tList: TermList, varsDict):
        for term in tList:
            if type(term) is Var:
                visit_var(term, varsDict)
            if type(term) is TermInBrackets:
                visit_expr(term.expr, varsDict)
            if type(term) is FuncCall:
                visit_funccall(term, varsDict)

    def visit_var(v: Var, varsDict):
        vType = v.type
        vInd = v.index
        key = str(vType) + str(vInd).lower()
        if key not in varsDict:
            varsDict[key] = len(varsDict) + 1
        v.index = varsDict[key]

    def visit_funccall(f: FuncCall, varsDict):
        f.name = 'cl_' + str(eqClasses[f.name])
        visit_expr(f.expr, varsDict)

    visit_function(func)

    return func


def exprTreeToStr(expr):
    def visit_expr(tList: TermList):
        dop = ''
        for term in tList:
            if type(term) is String:
                dop += term.expr
            if type(term) is Var:
                dop += visit_var(term)
            if type(term) is TermInBrackets:
                dop += '(' + visit_expr(term.expr) + ')'
            if type(term) is FuncCall:
                dop += visit_funccall(term)
        return dop + ' '

    def visit_var(v: Var):
        return str(v.type) + str(v.index)

    def visit_funccall(f: FuncCall):
        e = visit_expr(f.expr)
        return '<' + f.name + ' ' + e + '>'

    ans = visit_expr(expr)
    ans = ans.replace(' >', '>').replace(' )', ')')
    ans = ans[:-1]

    return ans


def getReturnedVals(func: Function):
    returnedVals = []

    def visit_expr(tList: TermList, funcCallVisited):
        if not funcCallVisited:
            if len(tList) == 0:
                if len(returnedVals) == 0:
                    returnedVals.append(String('eps'))
                return False

        if len(tList) == 1:
            term = tList[0]

            if type(term) is String:
                # Проверка того, что возвращаемые константы одинаковые
                if not funcCallVisited:
                    for ret in returnedVals:
                        if type(ret) is String and ret != term:
                            return False
                    if term not in returnedVals:
                        returnedVals.append(term)

            # Проверка того, что переменные не могут возвращаться в конст. функции
            if type(term) is Var:
                if not funcCallVisited:
                    return False
            
            if type(term) is TermInBrackets:
                visit_expr(term.expr, True)

            if type(term) is FuncCall:
                if not funcCallVisited:
                    returnedVals.append(term)
                okConst = visit_expr(term.expr, True)
                if not okConst:
                    return False

        # Проверка того, что ничего не приписывается
        if len(tList) > 1:
            return False
        
        return True
    
    for sent in func.sentences:
        okConst = visit_expr(sent.expr, False)
        if not okConst:
            return None
        
    for i in range(len(returnedVals)):
        returnedVals[i] = exprTreeToStr([returnedVals[i]])

    return returnedVals


def getConstFuncClasses(trees):
    constFuncClasses = dict()
    for t in trees:
        constFuncClasses[t.name] = getReturnedVals(t)
    
    # for k, v in constFuncClasses.items():
    #     print(k)
    #     if v != None:
    #         for ttt in v:
    #             print(ttt)
    #     print()

    return constFuncClasses


def getEqClasses(trees):
    eqClasses = dict()
    for t in trees:
        eqClasses[t.name] = 1
    while True:
        # Переименование функций в новые классы
        treesCl = []
        for t in trees:
            treeCl = rename_vars__to_its_first_and_funcs_to_eq_cl(copy.deepcopy(t), eqClasses)
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

    return eqClasses


def showEqClassesAndConstFuncs(eqClasses, constFuncClasses):
    print('-------------------------\n\n')
    print('Классы эквивалентности:')
    eqClassesAns = dict()
    for func, cl in eqClasses.items():
        if cl not in eqClassesAns.keys():
            eqClassesAns[cl] = []
        eqClassesAns[cl].append(func)

    for cl, funcs in enumerate(eqClassesAns.values()):
        print('    Класс ' + str(cl) + ':', funcs)
    print('\n')

    print('Константные функции и их возвращаемые значения:')
    for funcs in eqClassesAns.values():
        consts = constFuncClasses[funcs[0]]
        if consts == None:
            continue
        print('   ', funcs, '->', consts)
