import ply.lex as lex
from ply.yacc import yacc
import math

# ------------------
# Analisador Léxico
# ------------------

tokens = (
    'NUM',
)

literals = '.;[]+-'

t_ignore = ' \t\n'

def t_NUM(t):
    r'(\+|-)?\d+(\.\d+)?'
    t.value = float(t.value)
    return t

def t_error(t):
    print(f"Carácter ilegal {t.value[0]}")
    t.lexer.skip(1)

lexer = lex.lex()

data = '+ [-1.5 ; +2] [3 ; +4.7] .'

def debug_lexer():
    lexer.input(data)
    while tok := lexer.token():
        print(tok)

# debug_lexer()

# ---------------------
# Analisador Sintático
# ---------------------

state = {
    'sentido': None,
    'anterior': None,
    'error': False,
    'intervals': 0,
    'min_range': None,
    'max_range': None
}

def p_sentence(t):
    "Sentence : Signal Intervals '.'"

    if state['error']:
        print("Disappointment! You can't even make a valid sequence!!!")
    else:
        print('Number of intervals: ', state['intervals'])
        print('Range: ', abs(state['max_range'] - state['min_range']))

def p_signal_plus(t):
    "Signal : '+'"
    state['sentido'] = 1
    state['anterior'] = -math.inf

def p_signal_minus(t):
    "Signal : '-'"
    state['sentido'] = -1
    state['anterior'] = math.inf

def p_intervals(t):
    "Intervals : Interval RemainingIntervals"

def p_remaining_intervals_empty(t):
    "RemainingIntervals :"

def p_remaining_intervals(t):
    "RemainingIntervals : Interval RemainingIntervals"

def p_interval(t):
    "Interval : '[' NUM ';' NUM ']'"

    if state['sentido'] == 1:
        CC1 = t[4] > t[2]
        CC2 = t[2] >= state['anterior']

        state['error'] = not (CC1 and CC2)
    else:
        CC1 = t[4] < t[2]
        CC2 = t[2] <= state['anterior']

        state['error'] = not (CC1 and CC2)

    state['anterior'] = t[4]
    state['intervals'] += 1

    if state['intervals'] == 1:
        state['min_range'] = t[2]
    state['max_range'] = t[4]

def p_error(t):
    print(f"Syntax error at '{t.value}'")

parser = yacc()



parser.parse(data)