import itertools
import time
import queue
from toolz import valmap
from functools import reduce


def union(relation1, relation2):
    return relation1 | relation2


def intersect(relation1, relation2):
    return relation1 & relation2


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
    while number:
        count += number & 1
        number >>= 1
    return count

priority_mapping = {0:0, 1:1, 2:2, 4:2, 8:3, 16:3, 32:3, 64:3, 128:3, 256:3, 512:3, 1024:3, 2048:3, 4096:3}

class Calculus:
    def __init__(self, relations, converse, composition):
        self.relations = relations
        self.relationsBinary = list(map(self.relation_to_binary, relations))
        self.converse = {self.relation_to_binary(k): self.relation_to_binary(
            v) for k, v in converse.items()}
        self.composition = {self.relation_to_binary(k):
                            {self.relation_to_binary(k1): reduce(union, map(self.relation_to_binary, v1))
                             for k1, v1 in v.items()}
                            for k, v in composition.items()}
        self.universe = (2 ** len(relations)) - 1

    def __str__(self):
        return 'relations:\n' + str(self.relations) + '\n' + \
            'converse:\n' + str(self.converse) + '\n' + \
            'composition:\n' + str(self.composition) + '\n'

    def compute_composition(self, relation1, relation2):
        """
        union all compositions from both relations using composition table of base relations
        """
        if relation1 == 0 or relation2 == 0:
            return 0
        if relation1 == self.universe or relation2 == self.universe:
            return self.universe
        composite = 0
        for rel1 in self.get_base_relations(relation1):
            for rel2 in self.get_base_relations(relation2):
                composite = union(composite, self.composition[rel1][rel2])
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
        return str(rel)

    def get_base_relations(self, relation):
        if binary_count_ones(relation) == 1:
            return [relation]
        rel = []
        for baseRel in self.relationsBinary:
            if intersect(baseRel, relation):
                rel.append(baseRel)
        return rel
    
    def calculate_priority(self, relation):
        priority = 0
        for r in self.get_base_relations(relation):
            priority += priority_mapping[r]
        return priority



class ConstraintSatisfactionProblem:
    def __init__(self, calculus, relations, additional_info, consistent_info):
        self.calculus = calculus
        self.relations = relations
        self.additional_info = additional_info
        self.consistent_info = consistent_info

    def __str__(self):
        printable_relations = valmap(lambda v: valmap(
            self.calculus.relation_to_string, v), self.relations)
        return self.additional_info + '\nCalculus: \n' + str(self.calculus) + 'Relations:\n' + str(printable_relations) + '\n'

    def lookup(self, fromR, toR):
        if fromR in self.relations and toR in self.relations[fromR]:
            return self.relations[fromR][toR]
        else:
            return self.calculus.compute_complement(0)

    def clone_relations(self):
        out = dict()
        for k, v in self.relations.items():
            out[k] = v.copy()
        return out

    def getNodes(self):
        nodes = set()
        for k1, v in self.relations.items():
            for k2, _ in v.items():
                nodes.add(k2)
            nodes.add(k1)
        return list(nodes)

    def aclosure_time(self, version):
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
        consistend_info = self.additional_info.split(':')[-1].strip()
        if consistend_info == "consistent":
            expected = True
        elif consistend_info == "not consistent":
            expected = False
        else:
            print("No information...")
            expected = result
        if result == expected:
            print(self.additional_info.split(':')[
                  0] + " result = " + str(result))
        else:
            print(self.additional_info.split(':')[0] + " expected = " +
                  str(expected) + " result " + str(result))
        #print(time.time() * 1_000_000 - start)
        #print("Result = " + str(result))
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
                edges.put((binary_count_ones(cij), (i, j)))
        while not(edges.empty()):
            edge = edges.get()[1]
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
                    edges.put((binary_count_ones(newCik), (i, k)))
                if ckj != newCkj:
                    if newCkj == 0:
                        return False
                    self.relations = insert_relation(self.calculus,
                                                     self.relations, k, j, newCkj)
                    edges.put((binary_count_ones(newCkj), (k, j)))
        return True

    def contains_only_base_relations(self):
        for _, to_rel in self.relations.items():
            for _, relation in to_rel.items():
                if binary_count_ones(relation) != 1:
                    return False
        return True

    def refinement_search1(self):
        if not(self.aclosure2()):
            return False
        if self.contains_only_base_relations():
            return True
        for from_rel, to_rel in self.relations.items():
            for to, relation in to_rel.items():
                if binary_count_ones(relation) != 1:
                    for rel in self.calculus.get_base_relations(relation):
                        tmp_csp = ConstraintSatisfactionProblem(
                            self.calculus, self.clone_relations(), self.additional_info, "")
                        tmp_csp.relations[from_rel][to] = rel
                        tmp_csp.relations[to][from_rel] = self.calculus.compute_converse(
                            rel)
                        if tmp_csp.refinement_search1():
                            return True
                    return False
        return False

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
        return Calculus(relations, converse, composition)


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
        consistent_info = additional_info.split(
            ':')[-1].strip() == "consistent"
        for line in cspInstance[1:]:
            parts = line.split()
            fromRel = parts[0]
            toRel = parts[1]
            # remove brackets
            # FIX IN INPUT format = "FROM TO ( r1 rn )"
            # construct combined relation
            rel = sum(map(calculus.relation_to_binary, parts[3:-1]))
            # insert relation
            relations = insert_relation(
                calculus, relations, fromRel, toRel, rel)
        qcsps.append(ConstraintSatisfactionProblem(
            calculus, relations, additional_info, consistent_info))
    return qcsps


def reason_with_csp_file(csp_file):
    allen_calculus = parseCalculus('allen.txt')

    for csp in parse_csp(allen_calculus, csp_file):
        print(csp.additional_info)
        closed = csp.refinement_search1()
        correct = csp.consistent_info == closed
        if not correct:
            print("expected = " + str(csp.consistent_info))
            print("actual   = " + str(closed))
    return

if __name__ == '__main__':
    reason_with_csp_file('allen_csps.txt')
    reason_with_csp_file('ia_test_instances_10.txt')

