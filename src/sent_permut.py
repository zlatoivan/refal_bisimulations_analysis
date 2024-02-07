import copy
from syntax_trees import Function, Sentence, String, FuncCall, TermInBrackets, Var, String, TermList, getParser


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


def isPatternsPermutation(p1, p2):
    pref1 = None
    pref2 = None

    # Epsilon
    if len(p1) == 0:
        pref1 = None
        # Epsilon vs Epsilon
        if len(p2) == 0:
            pref2 = None
        # Epsilon vs String
        elif type(p2[0]) == String:
            pref2 = p2[0]
        # Epsilon vs TermInBrackets
        elif type(p2[0]) == TermInBrackets:
            pref2 = p2[0]
        # Epsilon vs Var
        elif type(p2[0]) == Var:
            pref2 = None
            for p in p2:
                if type(p) == Var and p.type != 'e':
                    pref2 = p

    # String
    elif type(p1[0]) == String:
        pref1 = p1[0].expr
        # String vs Epsilon
        if len(p2) == 0:
            pref2 = None
        # String vs String
        elif type(p2[0]) == String:
            pref2 = p2[0].expr
            if len(p1[0].expr) != len(p2[0].expr):
                # Делаем prf1 < prf2
                if len(p1[0].expr) > len(p2[0].expr):
                    p1, p2 = p2, p1
                # Если за меньшим префиксом есть e.X, то суффиксы не перестановочны (равны)
                if len(p1) > 1 and type(p1[1]) == Var and p1[1].type == 'e':
                    pref1 = pref2
        # String vs Var
        elif type(p2[0]) == Var:
            pref2 = p2[0]
            if p2[0].type == 'e' \
                    or (p2[0].type == 't' and len(pref1.replace('\'', '')) == 1) \
                    or (p2[0].type == 's' and len(pref1.replace('\'', '')) == 1):
                pref2 = pref1
        # String vs TermInBrackets
        elif type(p2[0]) == TermInBrackets:
            pref2 = p2[0]
    
    # Var
    elif type(p1[0]) == Var:
        pref1 = p1[0]
        # Var vs Epsilon
        if len(p2) == 0:
            pref2 = None
        # Var vs String
        elif type(p2[0]) == String:
            pref2 = p2[0].expr
            if p1[0].type == 'e' \
                    or (p1[0].type == 't' and len(pref2.replace('\'', '')) == 1) \
                    or (p1[0].type == 's' and len(pref2.replace('\'', '')) == 1):
                pref2 = pref1
        # Var vs Var
        elif type(p2[0]) == Var:
            pref2 = p2[0]
        # Var vs TermInBrackets
        elif type(p2[0]) == TermInBrackets:
            pref2 = p2[0]

    
    # TermInBrackets
    elif type(p1[0]) == TermInBrackets:
        pref1 = p1[0]
        # TermInBrackets vs Epsilon
        if len(p2) == 0:
            pref2 = None
        # TermInBrackets vs String
        elif type(p2[0]) == String:
            pref2 = p2[0]
        # TermInBrackets vs Var
        elif type(p2[0]) == Var:
            pref2 = p2[0]
        # TermInBrackets vs TermInBrackers
        elif type(p2[0]) == TermInBrackets:
            okPref = isPatternsPermutation(p1[0].expr, p2[0].expr)
            okSuf = isPatternsPermutation(p1[0].expr[::-1], p2[0].expr[::-1])
            if not okPref and not okSuf:
                pref2 = pref1
    

    # print(pref1, '|', pref2)
    
    if pref1 != pref2:
        return True

    return False


def isSentensesPermutation(sentences, i, j):
    s1 = sentences[i]
    s2 = sentences[j]

    okPref = isPatternsPermutation(s1.pattern, s2.pattern)
    okSuf = isPatternsPermutation(s1.pattern[::-1], s2.pattern[::-1])
    if not okPref and not okSuf:
        return False

    return True


def isBijection(s1, s2):
    if len(s1) != len(s2):
        return False

    for i in range(len(s1)):
        if s1[i] not in s2:
            return False
    
    return True


def checkSentencesPermutation(s1, s2):
    indexesForCheck = []
    order = list(range(len(s1)))

    # print(order)
    # print(s1)
    # print(s2, '\n')

    while True:
        intervals = []

        # Строим биекцию
        for i in range(len(s1)):
            j = s2.index(s1[i])
            new = [i, j]
            if i != j and (new[::-1] not in intervals):
                intervals.append(new)

        if len(intervals) == 0:
            break

        # Сортируем правила по удаленности друг от друга по убыванию
        intervals = sorted(intervals, key = lambda sub: abs(sub[1] - sub[0]))[::-1]
        # for i in intervals:
        #     print(i)
        # print()

        # Запоминаем правила, которые надо проверить на перестановочность
        i, j = intervals[0]
        if i < j:
            while i < j:
                indexesForCheck.append([order[i], order[j]])
                j -= 1
        else:
            while i > j:
                indexesForCheck.append([order[i], order[j]])
                j += 1

        # Ставим i на место j, остальное сдвигается влево
        i, j = intervals[0]
        s1.insert(j, s1.pop(i))
        order.insert(j, order.pop(i))
        intervals.pop(0)

        # print(order)
        # print(s1)
        # print(s2, '\n---------------\n')

    return indexesForCheck, order


def sentencesPermutation(trees):
    # Переименовать переменные и функции на порядковый номер первого вхождения в правило
    treesRenamed = []
    for t in trees:
        treeCl = rename_vars_and_funcs(copy.deepcopy(t))
        treesRenamed.append(treeCl)

    for i in range(len(treesRenamed)):
        for j in range(i, len(treesRenamed)):
            sentences1 = treesRenamed[i].sentences
            sentences2 = treesRenamed[j].sentences

            # Проверка биекции
            if not isBijection(sentences1, sentences2):
                continue
            
            # Получить правила, которые проверить на перестановочность
            indexesForCheck, order = checkSentencesPermutation(sentences1, sentences2)
            if len(indexesForCheck) == 0:
                continue

            # Проверить перестановочность правил
            print('Биекция у ' + trees[i].name + ' и ' + trees[j].name + ' есть. У функции ' + treesRenamed[i].name + ' предложения')
            okPerm = True
            for ifc in indexesForCheck:
                okPerm = isSentensesPermutation(sentences1, ifc[0], ifc[1])
                if not okPerm:
                    print(i, j, '\n')
            
            if not okPerm:
                print('не перестановочны\n\n')
                continue
            
            for ifc in indexesForCheck:
                print(ifc[0], ifc[1])
            print('перестановочны\n')

            # Переставить правила
            sp = trees[i].sentences
            spOld = copy.deepcopy(sp)
            for ind in range(len(order)):
                sp[order[ind]] = spOld[ind]
    