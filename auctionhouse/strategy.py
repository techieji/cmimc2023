"""
Edit this file! This is the file you will submit.
"""
import random
from functools import wraps
from math import floor, exp, sqrt, pi, log
from statistics import mean, linear_regression, StatisticsError
import itertools as it
from copy import deepcopy

def linreg(x, y):   # Requires version > 3.10
    B0, B1 = linear_regression(x, y)
    return lambda x: x * B1 + B0

def cap(percent, name):
    def dec(fn):
        def f(wallet, history):
            v = fn(wallet, history)
            if v / wallet < percent:
                return v
            return floor(percent * wallet)
        f.__name__ = name
        globals()[name] = f
        return fn
    return dec

def waiter(amt, name):
    def dec(fn):
        def f(wallet, history):
            if len(history) < amt:
                return 0
            return fn(wallet, history)
        f.__name__ = name
        globals()[name] = f
        return f
    return dec

def op_balance(history):
    return [100 - x for x in it.accumulate(x[0] for x in history)]

# Implement me!
# 2 example strategies to use in your tournament.
@cap(0.5, 'safe_gambler')
def gambler(wallet, history):
    return random.randint(0, wallet)

def gaussian_gambler(wallet, history):
    mean_w  = 2/3
    stdev_w = 1/4
    v = round(random.gauss(wallet * mean_w, wallet * stdev_w))
    return max(0, min(v, wallet))

def villain(wallet, history):
    return max(wallet - 1, 0)

def gauss(wallet, history):
    op_money = op_balance(history)[-1] if history else 100
    x = op_money - wallet
    v = exp(-x**2/2)/sqrt(2*pi)    # idk if this is builtin
    return v * wallet

@cap(0.5, 'safe_copycat')
def copycat(wallet, history):
    if len(history) > 0:
        last_move = history[-1][0]
        if last_move < wallet:
            return last_move
        return 0
    return 0    # change to 2

@cap(0.5, 'safe_avg_copycat')
def avg_copycat(wallet, history):
    if len(history) > 0:
        m = mean(x[0] for x in history)
        v = round(m) + 1
        if v < wallet:
            return v
        return 0
    return 0

@cap(0.5, 'safe_observer')
def observer(wallet, history):
    op_money = op_balance(history)[-1] if history else 0
    x = 12    # Maybe combine with random?
    return min(x, op_money + 1)

@cap(0.5, 'safe_stochastic_observer')
def stochastic_observer(wallet, history):
    op_money = op_balance(history)[-1] if history else 0
    x = random.randint(0, round(wallet))
    return min(x, op_money + 1)

def constant(wallet, history):
    if 12 > wallet:
        return 12
    return wallet

@cap(0.5, 'safe_ruthless_observer')
def ruthless_observer(wallet, history):
    if len(history) < 4:
        return 0
    op_money = op_balance(history)[-1]
    return min(op_money + 1, wallet)

def calculator(wallet, history):
    if len(history) < 3: return 0     # Small amt
    opbalance = op_balance(history)
    y = list(map(lambda y: log(y + 1, 2), opbalance))
    x = range(len(history))
    fn = linreg(x, y)
    op_balance_guess = 2**fn(len(history) + 1) - 1
    op_guess = abs(opbalance[-1] - op_balance_guess)
    if op_guess / wallet > 0.5:     # Threshold can be changed
        return 0
    return round(op_guess) + 1

def calculator2(wallet, history):
    if len(history) < 3: return 0
    try:
        x = op_balance(history)
        y = [x[0] for x in history]
        fn = linreg(x, y)
        op_guess = fn(x[-1])
    except StatisticsError:
        op_guess = x[-1]
    return min(op_guess + 1, x[-1] + 1)

@cap(0.5, 'safe_game_theoretician')
def game_theoretician(wallet, history):
    if len(history) == 0: return 0
    cost = 1 - sum(1 for x in history if x[1] is False)/4
    opm = op_balance(history)[-1]
    return min(opm * cost + 1, wallet)

# Edit me!
def get_strategies():
    """
    Returns a list of strategy functions to use in a tournament.

    In the local tester, all of the strategies will be used as separate bidders in the tournament.
    Note that strategies are tracked by their function name for readability in the results, so 
    adding the same function multiple times will not simulate multiple bidders using the same strategy.

    In the official grader, only the first element of the list will be used as your strategy. 
    """
    waiter(3, 'waiting_observer')(observer)
    waiter(3, 'waiting_safe_gambler')(safe_gambler)
    waiter(3, 'waiting_safe_observer')(safe_observer)
    waiter(3, 'waiting_gauss')(gauss)
    waiter(3, 'waiting_constant')(constant)
    waiter(3, 'waiting_game_theoretician')(game_theoretician)
    strategies = [
        waiting_safe_observer,
        safe_gambler,
        waiting_safe_gambler,
        villain,
        copycat,
        observer,
        safe_observer,
        waiting_observer,
        safe_copycat,
        gauss,
        waiting_gauss,
        gaussian_gambler,
        ruthless_observer,
        safe_ruthless_observer,
        avg_copycat,
        safe_avg_copycat,
        calculator,
        constant,
        waiting_constant,
        calculator2,
        game_theoretician,
        safe_game_theoretician,
        waiting_game_theoretician,
        stochastic_observer,
        safe_stochastic_observer
    ]

    for x in range(10):
        fn = lambda *a: gambler(*a)
        fn.__name__ = f'gambler #{x}'
        strategies.append(fn)

    return strategies
