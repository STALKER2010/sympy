from __future__ import print_function, division

from sympy.core import Mul, Pow
from sympy.core.basic import preorder_traversal
from sympy.core.function import count_ops
from sympy.functions.combinatorial.factorials import (binomial,
    CombinatorialFunction, factorial)
from sympy.functions import gamma

from sympy.utilities.timeutils import timethis
from sympy.utilities.exceptions import SymPyDeprecationWarning


@timethis('combsimp')
def combsimp(expr):
    r"""
    Simplify combinatorial expressions.

    This function takes as input an expression containing factorials,
    binomials, Pochhammer symbol and other "combinatorial" functions,
    and tries to minimize the number of those functions and reduce
    the size of their arguments.

    The algorithm works by rewriting all combinatorial functions as
    gamma functions and applying gammasimp() except simplification
    steps that may make an integer argument non-integer. See docstring
    of gammasimp for more information.

    Then it rewrites expression in terms of factorials and binomials by
    rewriting gammas as factorials and converting (a+b)!/a!b! into
    binomials.

    If expression has gamma functions or combinatorial functions
    with non-integer argument, it is automatically passed to gammasimp.

    Examples
    ========

    >>> from sympy.simplify import combsimp
    >>> from sympy import factorial, binomial, symbols
    >>> n, k = symbols('n k', integer = True)

    >>> combsimp(factorial(n)/factorial(n - 3))
    n*(n - 2)*(n - 1)
    >>> combsimp(binomial(n+1, k+1)/binomial(n, k))
    (n + 1)/(k + 1)

    """

    from .gammasimp import gammasimp, _gammasimp

    expr = expr.rewrite(gamma)
    if any(isinstance(node, gamma) and not node.args[0].is_integer
        for node in preorder_traversal(expr)):
        return gammasimp(expr);

    expr = _gammasimp(expr, as_comb = True)
    expr = _gamma_as_comb(expr)
    return expr


def _gamma_as_comb(expr):
    """
    Helper function for combsimp.

    Rewrites expression in terms of factorials and binomials
    """

    expr = expr.rewrite(factorial)

    from .simplify import bottom_up

    def f(rv):
        n, d = rv.as_numer_denom()

        n_args = []
        n_fact_args = []
        if isinstance(n, (Mul, Pow, factorial)):
            for factor, exp in n.as_powers_dict().items():
                try:
                    n_args.extend([factor]*exp)
                    if isinstance(factor, factorial):
                        n_fact_args.extend([factor.args[0]]*exp)
                except TypeError:
                    n_args.append(factor**exp)
        if not n_args or not n_fact_args:
            return rv

        d_args = []
        if isinstance(d, (Mul, Pow, factorial)):
            for factor, exp in d.as_powers_dict().items():
                try:
                    d_args.extend([factor]*exp)
                except TypeError:
                    n_args.append(factor**exp)
        else:
            return rv

        hit = False
        for i in range(len(d_args)):
            ai = d_args[i]
            if not isinstance(ai, factorial):
                continue

            for j in range(i + 1, len(d_args)):
                aj = d_args[j]
                if not isinstance(aj, factorial):
                    continue

                sum = ai.args[0] + aj.args[0]
                if sum in n_fact_args:
                    n_args.remove(factorial(sum))
                    n_fact_args.remove(sum)
                    n_args.append(binomial(sum, ai.args[0] if count_ops(
                    ai.args[0]) < count_ops(aj.args[0]) else aj.args[0]))

                    d_args[i] = None
                    d_args[j] = None
                    hit = True
                    break

        if hit:
            n = Mul(*[_arg for _arg in n_args if _arg])
            d = Mul(*[_arg for _arg in d_args if _arg])
            return n/d
        return rv

    return bottom_up(expr, f)
