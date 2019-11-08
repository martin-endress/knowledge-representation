import itertools


def is_boolean_set_algebra(universe, test_set):
    for rel in test_set:
        if not inverse(universe, rel) in test_set:
            return False
    return True


def converse(relation):
    return set([(y, x) for (x, y) in relation])


def inverse(universe, relation):
    universe_relation = set(itertools.product(universe, universe))
    return universe_relation.difference(relation)


universe = {1, 2, 3, 4}

empty = set()
lt = {(1, 2), (1, 3), (1, 4), (2, 3), (2, 4), (3, 4)}
gt = {(4, 3), (4, 2), (4, 1), (3, 2), (3, 1), (2, 1)}
ne = {(1, 2), (1, 3), (1, 4), (2, 1), (2, 3), (2, 4),
      (3, 1), (3, 2), (3, 4), (4, 1), (4, 2), (4, 3)}
let = {(1, 1), (1, 2), (1, 3), (1, 4), (2, 2),
       (2, 3), (2, 4), (3, 3), (3, 4), (4, 4)}
get = {(4, 4), (4, 3), (4, 2), (4, 1), (3, 3),
       (3, 2), (3, 1), (2, 2), (2, 1), (1, 1)}
eq = {(1, 1), (2, 2), (3, 3), (4, 4)}
U = set(itertools.product(universe, universe))

no_bsa = [lt, gt]
bsa = [empty, lt, gt, ne, eq, let, get, U]

print(is_boolean_set_algebra(universe, no_bsa))
print(is_boolean_set_algebra(universe, bsa))
