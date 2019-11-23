import itertools
from functools import reduce
from typing import Any, Callable, Collection, Dict, FrozenSet, Generator, Set, Tuple, Union


def join(relation1, relation2):
    return relation1 | relation2


def intersect(relation1, relation2):
    return relation1 & relation2


class QualitativeCalculi:
    def __init__(self, relations: [str], converse: Dict[str, str], composition: Dict[str, Dict[str, str]]):
        self.relations = relations
        self.relationsBinary = list(map(self.relToBinary, relations))
        self.converse = {self.relToBinary(k): self.relToBinary(
            v) for k, v in converse.items()}
        self.composition = {self.relToBinary(k):
                            {self.relToBinary(k1): reduce(join, map(self.relToBinary, v1))
                             for k1, v1 in v.items()}
                            for k, v in composition.items()}

    def __str__(self):
        return 'relations:\n' + str(self.relations) + '\n' + \
            'converse:\n' + str(self.converse) + '\n' + \
            'composition:\n' + str(self.composition)

    def compose(self, relation1, relation2):
        """
        join all compositions from both relations using composition table of base relations
        """
        composite = 0
        for rel1 in self.relationsBinary:
            for rel2 in self.relationsBinary:
                if intersect(relation1, rel1):
                    if intersect(relation2, rel2):
                        composite = join(
                            composite, self.composition[rel1][rel2])
        return composite

    def complement(self, relation):
        return join(~relation, pow(2, len(self.relations))-1)

    def is_boolean_set_algebra(self):
        """
        TODO implement
        """
        return False

    def relToBinary(self, relation):
        rel = 0
        for idx, value in enumerate(self.relations):
            if value in relation:
                rel = rel | pow(2, idx)
        return rel

    def relToString(self, relation):
        rel = []
        for idx, value in enumerate(self.relations):
            if (pow(2, idx) & relation != 0):
                rel.append(value)
        return rel


def parseFile(fileName):
    with open(fileName, 'r') as relationsFile:
        relationsFile.readline()                    # header
        relations = relationsFile.readline().split()
        relationsFile.readline()                    # blank line
        relationsFile.readline()                    # header
        line = relationsFile.readline().strip()     # converse relations
        converse = dict()
        while line:
            converseParts = line.split()
            if len(converseParts) != 2 or not(all(rel in relations for rel in converseParts)):
                print("illegal converse input")
                quit()
            converse[converseParts[0]] = converseParts[1]
            line = relationsFile.readline().strip()
        relationsFile.readline()                    # header
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
            composition[compositionParts[0]
                        ][compositionParts[1]] = compositionParts[2:]
            line = relationsFile.readline().strip()
        return QualitativeCalculi(relations, converse, composition)


if __name__ == '__main__':
    # allen = parseFile('allen.txt')
    # print(allen)
    linear = parseFile('linear.txt')
    print(linear)
