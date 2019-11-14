import itertools


def is_boolean_set_algebra(relations):
    for rel in relations:
        if not inverse(rel) in relations:
            return False
    return True


def compose(relation1, relation2):
    """
     °  100 010 001
    100 100 100 111
    010 100 010 001
    001 111 001 001
    """
    indeces = dict([(0b100, 0), (0b010, 1), (0b001)])  # Super ugly, please fix
    composition = [[0b100, 0b100, 0b111],
                   [0b100, 0b010, 0b001],
                   [0b111, 0b001, 0b001]]
    return composition[indeces.get(relation1)][indeces.get(relation2)]


def join(relation1, relation2):
    return relation1 | relation2


def intersect(relation1, relation2):
    return relation1 & relation2

# do we have to define converse manually?
# def converse(relation):
#    return relation


def inverse(relation):
    return relation ^ 0b111


domain = {1, 2, 3}

"""
    <=>
u = 111
< = 100
= = 010
> = 001

"""
