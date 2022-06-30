# -*- coding: utf-8 -*-


def bind_field(input: str) -> str:
    expressions = input.split('.')
    binded_expressions = []

    for exp in expressions:
        binded_expressions.append(f'`{exp}`')

    result = '.'.join(binded_expressions)

    return result
