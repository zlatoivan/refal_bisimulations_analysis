from parse_prepare import Function, Sentence, String, FuncCall, TermInBrackets, Var, String, TermList, getParser


def isBijection(s1, s2):
    if len(s1) != len(s2):
        return False

    for i in range(len(s1)):
        if s1[i] not in s2:
            return False
    
    return True


def getIndexesForCheck(s1, s2):
    sentencesForCheck = []
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
                sentencesForCheck.append([order[i], order[j]])
                j -= 1
        else:
            while i > j:
                sentencesForCheck.append([order[i], order[j]])
                j += 1

        # Ставим i на место j, остальное сдвигается влево
        i, j = intervals[0]
        s1.insert(j, s1.pop(i))
        order.insert(j, order.pop(i))
        intervals.pop(0)

        # print(order)
        # print(s1)
        # print(s2, '\n---------------\n')

    return sentencesForCheck


def checkPatternsPermutation(p1, p2):
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
            pref2 = p[0]
        # TermInBrackets vs Var
        elif type(p2[0]) == Var:
            pref2 = p[0]
        # TermInBrackets vs TermInBrackers
        elif type(p2[0]) == TermInBrackets:
            okPref = checkPatternsPermutation(p1[0].expr, p2[0].expr)
            okSuf = checkPatternsPermutation(p1[0].expr[::-1], p2[0].expr[::-1])
            if not okPref and not okSuf:
                pref2 = pref1
    

    # print(pref1, '|', pref2)
    
    if pref1 != pref2:
        return True

    return False


def checkSentensesPermutation(sentences, indexes):
    for ind in indexes:
        s1 = sentences[ind[0]]
        s2 = sentences[ind[1]]

        okPref = checkPatternsPermutation(s1.pattern, s2.pattern)
        okSuf = checkPatternsPermutation(s1.pattern[::-1], s2.pattern[::-1])
        if not okPref and not okSuf:
            return ind

    return None


