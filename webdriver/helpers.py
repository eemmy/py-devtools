# -*- coding: utf-8 -*-


def concat_urls(part_a, part_b):
    if part_a[-1] != '/':
        part_a = part_a + '/'

    if part_b[0] == '/':
        part_b = part_b[1:]

    return part_a + part_b
