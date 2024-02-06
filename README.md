# Анализ бисимуляций рефала

## Входные данные

Входными данными является файл, который содержит функции, разделенные Enter'ом.

*Пример input.txt:*

    F {
        'AA' e.X = (e.X (e.X));
        'A' e.Y = <G e.Y>;
        e.Y = e.X;
    }

    G {
        'AA' e.Y = e.Y e.Y;
        'A' e.X = <F e.X>;
        e.X = e.Y;
    }

Примечание: Epsilon задается пустотой: " = <F 'A'>;"


## Выходные данные

1. Синтаксические деревья фенкций, учитывая:
    - Замену индексов переменных на порядковый номер первого вхождения переменных в правило
    - Замену имен функций на порядковый номер первого вхождения функций в правило
2. Информацию о том, являются ли функции бисимуляцией

*Пример выходных данных:*

    F {
        'AA' e.X = (e.X (e.X));
        'A' e.Y = <G e.Y>;
        e.Y = e.X;
    }
    
    Function(name='F',
            sentences=[Sentence(pattern=[String(expr="'AA'"),
                                        Var(type='e', index=1)],
                                expr=[TermInBrackets(expr=[Var(type='e', index=1),
                                                            TermInBrackets(expr=[Var(type='e',
                                                                                    index=1)])])]),
                        Sentence(pattern=[String(expr="'A'"),
                                        Var(type='e', index=2)],
                                expr=[FuncCall(name='func_1',
                                                expr=[Var(type='e', index=2)])]),
                        Sentence(pattern=[Var(type='e', index=2)],
                                expr=[Var(type='e', index=1)])])





    G {
        'AA' e.Y = e.Y e.Y;
        'A' e.X = <F e.X>;
        e.X = e.Y;
    } 

    Function(name='G',
            sentences=[Sentence(pattern=[String(expr="'AA'"),
                                        Var(type='e', index=1)],
                                expr=[Var(type='e', index=1),
                                    Var(type='e', index=1)]),
                        Sentence(pattern=[String(expr="'A'"),
                                        Var(type='e', index=2)],
                                expr=[FuncCall(name='func_1',
                                                expr=[Var(type='e', index=2)])]),
                        Sentence(pattern=[Var(type='e', index=2)],
                                expr=[Var(type='e', index=1)])])




    Функции не являются бисимуляцией
