import itertools

# def is_boolean_set_algebra(relations):
#    for rel in relations:
#        if not complement(rel) in relations:
#            return False
#    return True


def compose(relation1, relation2):
    """
     °  100 010 001
    100 100 100 111
    010 100 010 001
    001 111 001 001
    """
    composition = [[0b100, 0b100, 0b111],
                   [0b100, 0b010, 0b001],
                   [0b111, 0b001, 0b001]]
    return composition[1][1]


def join(relation1, relation2):
    return relation1 | relation2


def intersect(relation1, relation2):
    return relation1 & relation2


def complement(relation):
    return ~relation


def readFile(fileName):
    with open(fileName, 'r') as relationsFile:
        relationsFile.readline()                # header
        relations = relationsFile.readline().split()
        relationsFile.readline()                # blank line
        relationsFile.readline()                # header
        line = relationsFile.readline().strip()  # converse relations
        converse = dict()
        while line:
            converseParts = line.split()
            if len(converseParts) != 2 or not(all(rel in relations for rel in converseParts)):
                print("illegal converse input")
                quit()
            converse[converseParts[0]] = converseParts[1]
            line = relationsFile.readline().strip()
        relationsFile.readline()                # header
        line = relationsFile.readline().strip()
        composition = dict()
        while line:
            compositionParts = line.split()
            if len(compositionParts) < 3:
                print("illegal composition input len")
                quit()
            # replace brackets in first and last element [2,-1]
            compositionParts[2] = compositionParts[2][1:]
            compositionParts[-1] = compositionParts[-1][:-1]
            if not(all(rel in relations for rel in compositionParts)):
                print("illegal composition input")
                quit()
            if compositionParts[0] not in composition:
                composition[compositionParts[0]] = dict()
            composition[compositionParts[0]][compositionParts[1]] = compositionParts[2:]
            line = relationsFile.readline().strip()

readFile('allen.txt')
