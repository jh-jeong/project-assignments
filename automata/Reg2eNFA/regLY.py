# -*- coding:utf-8 -*-
'''
Created on 2014. 11. 25.

@author: biscuit
'''


tokens = (
          "EMPTY",
          "SYMBOLS",
          "PLUS",
          "STAR",
          "LPAREN",
          "RPAREN",
          )

t_EMPTY = r"_phi"
t_SYMBOLS = r"[a-zA-Z0-9]|_e"
t_PLUS = r"\+"
t_STAR = r"\*"
t_LPAREN = r"\("
t_RPAREN = r"\)"

t_ignore  = ' \t'
# Define a rule so we can track line numbers
def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value) 
# Error handling rule
def t_error(t):
    print "Illegal character '%s'" % t.value[0]
    t.lexer.skip(1)
    
def p_exp_plus(p):
    'exp : exp PLUS exp'
    p[0] = ('plus',p[1],p[3])
    
def p_exp_paren(p):
    'exp : LPAREN exp RPAREN'
    p[0] = ('paren', p[2])

def p_exp_star(p):
    'exp : exp STAR'
    p[0] = ('star', p[1])

def p_exp_concat(p):
    'exp : exp exp %prec CONC'
    p[0] = ('concat', p[1], p[2])

def p_exp_sym(p):
    'exp : SYMBOLS'
    p[0] = ('symbols', p[1])

def p_exp_empty(p):
    'exp : EMPTY'
    p[0] = ('empty', p[1])

def p_error(p):
    print "Syntax error in input!"
    
precedence = (
              ('left', 'PLUS'),
              ('left', 'CONC'),
              ('left', 'LPAREN', 'RPAREN'),
              ('left', 'STAR'),
              ('left', 'SYMBOLS')
              )
    