import itertools


def is_boolean_set_algebra(universe, relations):
    """
    O(n)    for n = |B| (`in` operation has O(1) by using hash table)
    O(n*r)  for r = max(|relation|)
    """
    for rel in relations:
        if not inverse(universe, rel) in relations:
            return False
    return True


def compose(universe_relation, relation1, relation2):
    """
    O(1)    for n = |B|
    O(r^2)  for r = max(|relation|)
        (Improvement possible if z is in a hash table. Relation would be of type table(key -> list))
    """
    return set([(x, z) for (x, y) in relation1 for (t, z) in relation2 if t == y and (x, z) in universe_relation])


def converse(relation):
    """
    O(1)    for n = |B|
    O(r)    for r = |relation|
    """
    return set([(y, x) for (x, y) in relation])


def inverse(universe, relation):
    """
    O(1)    for n = |B|
    O(r)    for r = |relation|
    """
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
