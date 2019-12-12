import itertools
import time
import queue
from toolz import valmap
from functools import reduce


def union(relation1, relation2):
    return relation1 | relation2


def intersect(relation1, relation2):
    return relation1 & relation2


class PointCalculus:
    def __init__(self, relations, converse, composition):
        self.relations = relations
        # map to binary representation
        self.relationsBinary = list(map(self.relation_to_binary, relations))
        self.converse = {self.relation_to_binary(k): self.relation_to_binary(
            v) for k, v in converse.items()}
        self.composition = {self.relation_to_binary(k):
                            {self.relation_to_binary(k1): reduce(union, map(self.relation_to_binary, v1))
                             for k1, v1 in v.items()}
                            for k, v in composition.items()}

    def __str__(self):
        return 'relations:\n' + str(self.relations) + '\n' + \
            'converse:\n' + str(self.converse) + '\n' + \
            'composition:\n' + str(self.composition) + '\n'

    def compute_composition(self, relation1, relation2):
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

    def compute_converse(self, relation):
        conv = 0
        for rel1 in self.relationsBinary:
            if intersect(relation, rel1):
                conv = union(conv, self.converse[rel1])
        return conv

    def compute_complement(self, relation):
        return intersect(~relation, pow(2, len(self.relations))-1)

    def is_boolean_set_algebra(self):
        """
        In our representation, the property boolean set algebra is implied.
        The set of all possible relations 2^R is not explicitly stated
        """
        return True

    def relation_to_binary(self, relation):
        for idx, value in enumerate(self.relations):
            if value == relation:
                return pow(2, idx)
        print("warning, relation " + relation +
              " does not exist. Returning empty relation..")
        return 0

    def relation_to_string(self, relation):
        rel = []
        for idx, value in enumerate(self.relations):
            if (pow(2, idx) & relation != 0):
                rel.append(value)
        return rel


def insert_relation(calculus, relations, fromR, toR, relation):
    if not(fromR in relations):
        relations[fromR] = dict()
    if not(toR in relations):
        relations[toR] = dict()
    relations[fromR][toR] = relation
    relations[toR][fromR] = calculus.compute_converse(relation)
    return relations


def binary_count_ones(number):
    count = 0
    while number > 0:
        if (number & 0b1) == 1:
            count += 1
        number = number >> 1
    return count


class ConstraintSatisfactionProblem:
    def __init__(self, calculus, relations, additional_info):
        self.calculus = calculus
        self.relations = relations
        self.additional_info = additional_info

    def __str__(self):
        printable_relations = valmap(lambda v: valmap(
            self.calculus.relation_to_string, v), self.relations)
        return self.additional_info + '\nCalculus: \n' + str(self.calculus) + 'Relations:\n' + str(printable_relations) + '\n'

    def lookup(self, fromR, toR):
        if fromR in self.relations and toR in self.relations[fromR]:
            return self.relations[fromR][toR]
        else:
            return self.calculus.compute_complement(0)

    def getNodes(self):
        nodes = set()
        for k1, v in self.relations.items():
            for k2, _ in v.items():
                nodes.add(k2)
            nodes.add(k1)
        return list(nodes)

    def aclosure_time(self, version):
        print(self.additional_info)
        start = time.time() * 1_000_000
        if version == 1:
            result = self.aclosure1()
        elif version == 15:
            result = self.aclosure15()
        elif version == 2:
            result = self.aclosure2()
        else:
            print("invalid version " + str(version))
            return -1
        if self.additional_info.endswith("consistent"):
            if result != self.additional_info.endswith("not consistent"):
                print("correct")
            else:
                print("NOT CORRECT!!!")
        print(time.time() * 1_000_000 - start)
        print("Result = " + str(result))
        return result

    def aclosure1(self):
        s = True
        while s:
            s = False
            for i, j, k in itertools.product(self.getNodes(), repeat=3):
                if i == j or j == k or i == k:
                    continue
                cij = self.lookup(i, j)
                cjk = self.lookup(j, k)
                cik = self.lookup(i, k)
                newCik = intersect(
                    cik, self.calculus.compute_composition(cij, cjk))
                if cik != newCik:
                    s = True
                    self.relations = insert_relation(self.calculus,
                                                     self.relations, i, k, newCik)
                    if newCik == 0:
                        return False
        return True

    def aclosure15(self):
        edges = queue.SimpleQueue()
        for i, j in itertools.product(self.getNodes(), repeat=2):
            if i != j:
                edges.put((i, j))
        while not(edges.empty()):
            edge = edges.get()
            i = edge[0]
            j = edge[1]
            for k in [k for k in self.getNodes() if (k != i and k != j)]:
                # lookup
                cij = self.lookup(i, j)
                cjk = self.lookup(j, k)
                cik = self.lookup(i, k)
                ckj = self.lookup(k, j)
                cki = self.lookup(k, i)

                # calculate possible refinement
                newCik = intersect(
                    cik, self.calculus.compute_composition(cij, cjk))
                newCkj = intersect(
                    ckj, self.calculus.compute_composition(cki, cij))

                # update
                if cik != newCik:
                    if newCik == 0:
                        return False
                    self.relations = insert_relation(self.calculus,
                                                     self.relations, i, k, newCik)
                    edges.put((i, k))
                if ckj != newCkj:
                    self.relations = insert_relation(self.calculus,
                                                     self.relations, k, j, newCkj)
                    edges.put((k, j))
                    if newCkj == 0:
                        return False
        return True

    def aclosure2(self):
        edges = queue.PriorityQueue()
        for i, j in itertools.product(self.getNodes(), repeat=2):
            if i != j:
                cij = self.lookup(i, j)
                edges.put((binary_count_ones(self.lookup(i, j)), (i, j)))
        while not(edges.empty()):
            edge = edges.get()
            i = edge[0]
            j = edge[1]
            for k in [k for k in self.getNodes() if (k != i and k != j)]:
                # lookup
                cij = self.lookup(i, j)
                cjk = self.lookup(j, k)
                cik = self.lookup(i, k)
                ckj = self.lookup(k, j)
                cki = self.lookup(k, i)

                # calculate possible refinement
                newCik = intersect(
                    cik, self.calculus.compute_composition(cij, cjk))
                newCkj = intersect(
                    ckj, self.calculus.compute_composition(cki, cij))

                # update
                if cik != newCik:
                    if newCik == 0:
                        return False
                    self.relations = insert_relation(self.calculus,
                                                     self.relations, i, k, newCik)
                    edges.put((i, k))
                    edges.put((binary_count_ones(newCik), (i, k)))
                if ckj != newCkj:
                    self.relations = insert_relation(self.calculus,
                                                     self.relations, k, j, newCkj)
                    edges.put((k, j))
                    edges.put((binary_count_ones(newCkj), (k, j)))
                    if newCkj == 0:
                        return False
        return True


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
        return PointCalculus(relations, converse, composition)


def parse_csp(calculus, fileName):
    lines = [line.strip() for line in open(fileName)]
    cspInstances = []
    current_csp = []
    for line in lines:
        if line != ".":
            current_csp.append(line)
        else:
            cspInstances.append(current_csp)
            current_csp = []
    qcsps = []
    for cspInstance in cspInstances:
        relations = dict()
        additional_info = cspInstance[0]
        for line in cspInstance[1:]:
            parts = line.split()
            fromRel = parts[0]
            toRel = parts[1]
            # remove brackets
            parts[2] = parts[2][1:]
            parts[-1] = parts[-1][:-1]
            # construct combined relation
            rel = sum(map(calculus.relation_to_binary, parts[2:]))
            # insert relation
            relations = insert_relation(
                calculus, relations, fromRel, toRel, rel)
        qcsps.append(ConstraintSatisfactionProblem(
            calculus, relations, additional_info))
    return qcsps


def point_calculus_test(version):
    allen_calculus = parseCalculus('allen.txt')

    print("Aclosure with version " + str(version) + ":")
    for csp in parse_csp(allen_calculus, 'allen_csps.txt'):
        csp.aclosure_time(version)
        print()


if __name__ == '__main__':
    point_calculus_test(1)
    point_calculus_test(15)
    #allen_calculus = parseCalculus('allen.txt')
    #allen_csps = parse_csp(allen_calculus, '30x500_m_3_allen_eq1.csp')
    #csp = allen_csps[0]
    # csp.aclosure15()
    #homework = parse_csp(allen_calculus, "closure_interval_relations.csp")[0]
    # homework.aclosure_time(2)
