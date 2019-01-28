from typing import Iterable, TypeVar, Callable, Iterator, Tuple, List, Union


def identical(x):
    return x


T = TypeVar("T")
K = TypeVar("K")


class UnknownKey:
    def __init__(self, value):
        self.value = value

    def copy(self):
        return self.value


class StageGroupby:
    def __init__(self, iterable: Iterable[T], *stages: K, key: Callable[[T], K] = None):
        if key is None:
            key = lambda x: x
        self.keyfunc = key
        self.it = iter(iterable)
        self.stages = list(stages)
        self.currkey = self.currvalue = object()
        self.tgtkey = UnknownKey(self.currkey)

    def __iter__(self):
        return self

    def __next__(self) -> Tuple[Union[K, List[K]], Iterator[T]]:
        self.id = object()
        # skip previous _grouper if the value of group is ignored.
        while self._stage_accepted(self.tgtkey):
            self.currvalue = next(self.it)  # Exit on StopIteration
            self.currkey = self.keyfunc(self.currvalue)
        self.tgtkey = UnknownKey(self.currkey) if self.currkey not in self.stages else self.stages[
                                                                                       self.stages.index(self.currkey):]
        return self.tgtkey.copy(), self._grouper(self.tgtkey, self.id)

    def _stage_accepted(self, target_stages: List[K]):
        if isinstance(target_stages, UnknownKey):
            return target_stages.value == self.currkey
        while len(target_stages) >= 1:
            if self.currkey == target_stages[0]:
                return True
            else:
                del target_stages[0]
        return False

    def _grouper(self, tgtkey: List[K], id):
        while self.id is id and self._stage_accepted(tgtkey):
            yield self.currvalue
            try:
                self.currvalue = next(self.it)
            except StopIteration:
                return
            self.currkey = self.keyfunc(self.currvalue)


