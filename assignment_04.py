import itertools
from functools import lru_cache
from pprint import pprint
from typing import Any, Collection, Dict, FrozenSet, Generator, Set, Tuple, Union

BaseType = Any
RelationValue = Tuple[BaseType, BaseType]
# TODO: infinite relations (maybe Union[..., Generator] for infinite relations ?)
RelationValues = Union[FrozenSet[RelationValue], Set[RelationValue]]
Relation = Dict[str, RelationValues]


# noinspection PyMethodMayBeStatic,PyShadowingNames
class BSA:
    def __init__(self, domain: Collection, relations: Relation):
        self.domain = domain
        self.relations = relations
        for rel in relations:
            if not self.inverse(rel) in relations:
                raise ValueError("Given algebra is not a boolean set algebra")

    @lru_cache(maxsize=1)
    def universe(self):
        return frozenset(itertools.product(self.domain, self.domain))

    def cup(self, lr: str, rr: str):
        return self.relations[lr].union(self.relations[rr])

    def cap(self, lr: str, rr: str):
        return self.relations[lr].intersection(self.relations[rr])

    def inverse(self, rel: str):
        return self.universe().difference(self.relations[rel])

    def converse(self, rel: str):
        return set((y, x) for (x, y) in self.relations[rel] if (y, x) in self.universe())

    def compose(self, lr: str, rl: str):
        return set((x, z) for (x, y1) in self.relations[lr] for (y2, z) in self.relations[rl] if
                   y1 == y2 and (x, z) in self.universe())

    def evaluate(self, term):
        raise NotImplementedError

    def __str__(self):
        print(f"Domain: {self.domain}")
        print(f"Relations: {self.relations}")


if __name__ == '__main__':
    domain = [1, 2, 3, 4]

    lt = frozenset([(1, 2), (1, 3), (1, 4), (2, 3), (2, 4), (3, 4)])
    gt = frozenset([(4, 3), (4, 2), (4, 1), (3, 2), (3, 1), (2, 1)])
    ne = frozenset([(1, 2), (1, 3), (1, 4), (2, 1), (2, 3), (2, 4), (3, 1), (3, 2), (3, 4), (4, 1), (4, 2), (4, 3)])
    leq = frozenset([(1, 1), (1, 2), (1, 3), (1, 4), (2, 2), (2, 3), (2, 4), (3, 3), (3, 4), (4, 4)])
    geq = frozenset([(4, 4), (4, 3), (4, 2), (4, 1), (3, 3), (3, 2), (3, 1), (2, 2), (2, 1), (1, 1)])
    eq = frozenset([(1, 1), (2, 2), (3, 3), (4, 4)])

    input_relations = {
        '<': lt,
        '>': gt,
        '=': eq,
        '>=': geq,
        '<=': leq,
        '!=': ne
    }
    bsa = BSA(domain, input_relations)

    pprint(bsa.compose('<', '>'))

    # assert(bsa.evaluate('1<4'))
