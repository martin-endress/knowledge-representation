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


def compose(universe, relation1, relation2):
    """
    O(1)    for n = |B|
    O(r^2)  for r = max(|relation|)
        (Improvement possible if z is in a hash table. Relation would be of type table(key -> list))
    """
    return set([(x, z) for (x, y) in relation1 for (t, z) in relation2 if t == y and (x, z) in universe])


def converse(relation):
    """
    O(1)    for n = |B|
    O(r)    for r = |relation|
    """
    return set([(y, x) for (x, y) in relation])


def inverse(universe_relation, relation):
    """
    O(1)    for n = |B|
    O(r)    for r = |relation|
    """
    return universe_relation.difference(relation)


domain = {1, 2, 3, 4}

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
universe = set(itertools.product(domain, domain))

no_bsa = [lt, gt]
bsa = [empty, lt, gt, ne, eq, let, get, U]

print(is_boolean_set_algebra(universe, no_bsa))
print(is_boolean_set_algebra(universe, bsa))

print("---")

# Task 1.1
# Compute (R^-1 <compose> S) intersect R

rel_R = {('a', 'a'), ('a', 'b'), ('b', 'c'), ('c', 'e')}
rel_S = {('a', 'a'), ('b', 'a'), ('e', 'b'), ('c', 'e')}

universe = {'a', 'b', 'c', 'd', 'e'}
U = set(itertools.product(universe, universe))

compose(U, inverse(U, rel_R), rel_S).intersection(converse(rel_R))

print("---")

# Task 1.2
# Counterexample

universe = {1, 2}
U = set(itertools.product(universe, universe))

rel_R = U
rel_S = {(1, 2)}
rel_T = {(2, 2)}

left = compose(U, rel_R, rel_S.intersection(rel_T))
right = compose(U, rel_R, rel_S).intersection(compose(U, rel_R, rel_T))

print(left)
print(right)
print(left == right)
