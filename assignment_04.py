import itertools
from functools import lru_cache
from pprint import pprint
from typing import Any, Callable, Collection, Dict, FrozenSet, Generator, Set, Tuple, Union
from time import sleep
from random import shuffle

# Notes:
# * We assume generators are infinite, since we really can't distinguish otherwise (apart from the user telling us)
# * We assume arity of 2 for all relations
# * Some functions are needlessly eager TODO: lazify
# * TODO: Better (more convoluted) infinite universe generation
# * TODO: reset-able relation generators

BaseType = Any
DomainType = Union[Collection[BaseType], Generator[BaseType, BaseType, None]]
RelationValue = Tuple[BaseType, BaseType]
RelationValues = Union[FrozenSet[RelationValue], Set[RelationValue], Generator[RelationValue, RelationValue, None]]
Relations = Dict[str, RelationValues]


# noinspection PyMethodMayBeStatic,PyShadowingNames
class BSA:
    """
    Implements a Boolean Set Algebra and operations thereon.
    """

    def __init__(self, domain: DomainType,
                 # allow dynamically (with universe) generated relation sets/generators
                 relations: Dict[str, Union[RelationValues, Callable[[RelationValues], RelationValues]]]):
        self.domain = domain
        # instantiate dynamically generated generators
        for name, val in relations.items():
            if isinstance(val, Callable):
                relations[name] = val(self.universe) if isinstance(domain, Generator) else set(val(self.universe))
        self.relations = relations
        self.finite = not (isinstance(domain, Generator) or any(isinstance(rel, Generator) for rel in relations))
        if not self.finite:
            print("Init Warning: Operations on non-finite relations may not terminate!")
        elif not self.is_bsa:
            raise ValueError("Given finite Algebra is not a Boolean Set Algebra.")

    @property
    @lru_cache(maxsize=1)
    def is_bsa(self) -> bool:
        DEBUG_BSA = False
        if DEBUG_BSA:
            print("==== START BSA Test ====")
        for rel in self.relations:
            rel_inverse = self.inverse(rel)
            if isinstance(rel_inverse, Generator):
                rel_inverse = set(rel_inverse)
            found = False
            for other_rel_name, other_rel in self.relations.items():
                if isinstance(other_rel, Generator):
                    other_rel = set(other_rel)
                if rel_inverse == other_rel:
                    if DEBUG_BSA:
                        print(f"'{rel}^(-1)': {rel_inverse} == {other_rel} :'{other_rel_name}'")
                    found = True
                    break
            if not found:
                print(f"'{rel}^(-1)': {rel_inverse} ∉ R")
                return False
        if DEBUG_BSA:
            print("==== END BSA Test ====")
        return True

    @property
    def universe(self) -> RelationValues:
        """"
        Future version supporting higher arities:
        ```
        it = itertools.product(self.domain, repeat=2)
        while True:
            try:
                yield next(it)
            except StopIteration:
                return
        ```
        """
        return ((x, y) for x in self.domain for y in self.domain)

    def relation(self, rel: str):
        return self.relations[rel]

    def cup(self, left: str, right: str) -> RelationValues:
        lr, rr = self.relations[left], self.relations[right]
        if isinstance(lr, Generator) or isinstance(rr, Generator):
            def generator():
                while True:
                    yield next(lr)
                    yield next(rr)
            return generator()
        else:
            return lr.union(rr)

    def cap(self, left: str, right: str) -> RelationValues:
        lr, rr = self.relations[left], self.relations[right]
        if isinstance(lr, Generator) or isinstance(rr, Generator):
            return (lv for lv in lr for rv in rr if lv == rv)
        else:
            return lr.intersection(rr)

    def inverse(self, relation: str) -> RelationValues:
        rel = self.relations[relation]
        if isinstance(self.universe, Generator):
            def generator():
                for uv in self.universe:
                    if uv not in rel:
                        yield uv
            return generator()
        else:
            return self.universe.difference(rel)

    def converse(self, relation: str) -> RelationValues:
        return ((y, x) for (x, y) in self.relations[relation])

    def compose(self, left: str, right: str) -> RelationValues:
        lr, rr = self.relations[left], self.relations[right]
        return ((x, z) for (x, y1) in lr for (y2, z) in rr if y1 == y2)  # and (x, z) in self.universe)

    def evaluate(self, term):
        raise NotImplementedError

    def print(self):
        if self.finite:
            print(f"Domain: {self.domain}")
            print("Relations:")
            for name, rel in self.relations.items():
                print(f"'{name}': ", end='')
                print(rel)
        else:
            print("Domain: ", end='')
            lazy_print(self.domain)
            print("Relations:")
            for name, gen in self.relations.items():
                print(f"'{name}': ", end='')
                lazy_print(gen)


def positive_integers():
    num = 0
    while True:
        yield num
        num += 1


def lazy_print(stuff: RelationValues, depth=100):
    if isinstance(stuff, Generator):
        try:
            print('{', end='')
            for values in stuff:
                print(values, end=', ')
                depth -= 1
                if depth <= 0:
                    print('…', end='')
                    break
        except KeyboardInterrupt:
            print('[INTERRUPTED]', end='')
            return
        finally:
            print('}')
    else:
        print(stuff)


if __name__ == '__main__':
    domain = [1, 2, 3, 4]

    lt = frozenset([(1, 2), (1, 3), (1, 4), (2, 3), (2, 4), (3, 4)])
    gt = frozenset([(4, 3), (4, 2), (4, 1), (3, 2), (3, 1), (2, 1)])
    ne = frozenset([(1, 2), (1, 3), (1, 4), (2, 1), (2, 3), (2, 4), (3, 1), (3, 2), (3, 4), (4, 1), (4, 2), (4, 3)])
    leq = frozenset([(1, 1), (1, 2), (1, 3), (1, 4), (2, 2), (2, 3), (2, 4), (3, 3), (3, 4), (4, 4)])
    geq = frozenset([(4, 4), (4, 3), (4, 2), (4, 1), (3, 3), (3, 2), (3, 1), (2, 2), (2, 1), (1, 1)])
    eq = frozenset([(1, 1), (2, 2), (3, 3), (4, 4)])

    relations = {
        '<': lt,
        '>': gt,
        '=': eq,
        '>=': geq,
        '<=': leq,
        '!=': ne
    }
    bsa = BSA(domain, relations)

    lazy_print(bsa.cup('>', '='))
    lazy_print(bsa.cap('>=', '>'))
    lazy_print(bsa.converse('>='))
    lazy_print(bsa.compose('<', '>'))

    #domain = positive_integers()  # With this, some relations never return due to one-branch depth-first universe generation
    domain = range(1, 5)
    relations = {
        '<': lambda universe: ((x, y) for x, y in universe if x < y),
        '>': lambda universe: ((x, y) for x, y in universe if x > y),
        '=': lambda universe: ((x, y) for x, y in universe if x == y),
        '<=': lambda universe: ((x, y) for x, y in universe if x <= y),
        '>=': lambda universe: ((x, y) for x, y in universe if x >= y),
        '!=': lambda universe: ((x, y) for x, y in universe if x != y),
    }

    sleep(.5)
    print()

    bsa = BSA(domain, relations)
    #bsa.print()

    lazy_print(bsa.cup('>', '='))
    lazy_print(bsa.cap('>=', '>'))
    lazy_print(bsa.converse('>='))
    c = bsa.compose('<', '>')  # When working on an infinite domain, splitting up method calls like
    lazy_print(c)              # this may be necessary for correct evaluation

    # assert(bsa.evaluate('1<4'))
