import itertools
from functools import reduce
from typing import Any, Callable, Collection, Dict, FrozenSet, Generator, Set, Tuple, Union


def union(relation1, relation2):
    return relation1 | relation2


def intersect(relation1, relation2):
    return relation1 & relation2


class BooleanSetAlgebra:
    def __init__(self, relations: [str], converse: Dict[str, str], composition: Dict[str, Dict[str, str]]):
        self.relations = relations
        # map to binary representation
        self.relationsBinary = list(map(self.relToBinary, relations))
        self.converse = {self.relToBinary(k): self.relToBinary(
            v) for k, v in converse.items()}
        self.composition = {self.relToBinary(k):
                            {self.relToBinary(k1): reduce(union, map(self.relToBinary, v1))
                             for k1, v1 in v.items()}
                            for k, v in composition.items()}

    def __str__(self):
        return 'relations:\n' + str(self.relations) + '\n' + \
            'converse:\n' + str(self.converse) + '\n' + \
            'composition:\n' + str(self.composition) + '\n'

    def compose(self, relation1, relation2):
        """
        union all compositions from both relations using composition table of base relations
        """
        composite = 0
        for rel1 in self.relationsBinary:
            if intersect(relation1, rel1):
                for rel2 in self.relationsBinary:
                    if intersect(relation2, rel2):
                        composite = union(
                            composite, self.composition[rel1][rel2])
        return composite

    def computeConverse(self, relation):
        conv = 0
        for rel1 in self.relationsBinary:
            if intersect(relation, rel1):
                conv = union(conv, self.converse[rel1])
        return conv

    def complement(self, relation):
        return union(~relation, pow(2, len(self.relations))-1)

    def is_boolean_set_algebra(self):
        """
        In our representation, the property boolean set algebra is implied.
        The set of all possible relations 2^R is not explicitly stated
        """
        return True

    def relToBinary(self, relation):
        for idx, value in enumerate(self.relations):
            if value == relation:
                return pow(2, idx)
        print("warning, relation " + relation +
              " does not exist. Returning empty relation..")
        return 0

    def relToString(self, relation):
        rel = []
        for idx, value in enumerate(self.relations):
            if (pow(2, idx) & relation != 0):
                rel.append(value)
        return rel


def insert(relations, fromR, toR, relation):
    if not(fromR in relations):
        relations[fromR] = dict()
    relations[fromR][toR] = relation
    return relations


class PointCalculus:
    def __init__(self, calculus, relations):
        self.calculus = calculus
        self.relations = relations

    def __str__(self):
        return 'Calculus: \n' + str(self.calculus) + 'Relations:\n' + str(self.relations) + '\n'

    def lookup(self, fromR, toR):
        if fromR in self.relations and toR in self.relations[fromR]:
            return self.relations[fromR][toR]
        else:
            return self.calculus.complement(0)
    
    def getNodes(self):
        nodes = set()
        for k1, v in self.relations.items():
            for k2, _ in v.items():
                nodes.add(k2)
            nodes.add(k1)
        return list(nodes)

    def aclosure(self):
        s = True
        while s:
            s = False
            for i, j, k in itertools.product(self.getNodes(), repeat=3):
                cij = self.lookup(i, j)
                cjk = self.lookup(j, k)
                cik = self.lookup(i, k)
                newCik = intersect(cik, self.calculus.compose(cij, cjk))
                if cik != newCik:
                    s = True
                    self.relations = insert(self.relations, i, k, newCik)
                    self.relations = insert(
                        self.relations, k, i, self.calculus.computeConverse(newCik))
                    if newCik == 0:
                        return False
        print(self.relations)


def parseCalculus(fileName):
    with open(fileName, 'r') as calculusFile:
        calculusFile.readline()                    # header
        relations = calculusFile.readline().split()
        calculusFile.readline()                    # blank line
        calculusFile.readline()                    # header
        line = calculusFile.readline().strip()     # converse relations
        converse = dict()
        while line:
            converseParts = line.split()
            if len(converseParts) != 2 or not(all(rel in relations for rel in converseParts)):
                print("illegal converse input")
                quit()
            converse[converseParts[0]] = converseParts[1]
            line = calculusFile.readline().strip()
        calculusFile.readline()                    # header
        line = calculusFile.readline().strip()
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
            composition[compositionParts[0]
                        ][compositionParts[1]] = compositionParts[2:]
            line = calculusFile.readline().strip()
        return BooleanSetAlgebra(relations, converse, composition)


def parsePointRelations(calculus, fileName):
    lines = [line.strip() for line in open(fileName)]
    relations = dict()
    cspInstances = []
    currentRel = []
    for line in lines:
        if line:
            currentRel.append(line)
        else:
            cspInstances.append(currentRel)
            currentRel = []
    for cspInstance in cspInstances:
        for line in cspInstance[1:-1]:
            print(line)
            parts = line.split()
            fromRel = parts[0]
            toRel = parts[1]
            rel = sum(map(calculus.relToBinary, parts[3:-1]))

            relations = insert(relations, fromRel, toRel, rel)
            relations = insert(relations, toRel, fromRel,
                               calculus.computeConverse(rel))
            print(rel)
        return PointCalculus(calculus, relations)  # FIXME


if __name__ == '__main__':
    allen = parseCalculus('allen.txt')
    linear = parseCalculus('linear.txt')

    linearRelations = parsePointRelations(linear, 'pointCalculus.txt')
    print(str(linearRelations))
