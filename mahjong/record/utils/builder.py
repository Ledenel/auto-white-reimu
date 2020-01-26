from typing import List


class TransferDict:
    def __init__(self, nested_dict, parent=None, parent_key=None):
        self.parent: TransferDict = parent
        self.parent_key = parent_key
        self.nested_dict = {
            k: TransferDict(v, self, k) if isinstance(v, dict) else v
            for k, v in nested_dict.items()
        }

    def __getattr__(self, item):
        return getattr(self.nested_dict, item)

    def _readonly(self, *args, **kwards):
        raise NotImplemented

    __setattr__ = __setitem__ = __delattr__ = pop = update = popitem = _readonly

    def set(self, key, value):
        modified = TransferDict({
            **self,
            key: value
        })
        return self.parent.set(
            self.parent_key, modified
        ) if self.parent is not None else modified

    def drop(self, key):
        dict_cpy = self.nested_dict.copy()
        del dict_cpy[key]
        modified = TransferDict(dict_cpy)
        return self.parent.set(
            self.parent_key, modified
        ) if self.parent is not None else modified

    def setdefault(self, key, default):
        if key not in self:
            return self.set(key, default)
        else:
            return self


class StackedDict:
    def __init__(self, initial):
        self.stack_dicts = [initial]

    @property
    def merged_dict(self):
        m_dict = {}
        for dic in self.stack_dicts:
            m_dict.update(dic)
        return m_dict

    def __getattr__(self, item):
        return getattr(self.merged_dict, item)


class ContextStacker:
    def __init__(self, stack, item):
        self.item = item
        self.stack = stack
        self.stack: List

    def __enter__(self):
        self.stack.append(self.item)

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stack.pop()


class Builder:
    def __init__(self, ctor, inner_state=None):
        if inner_state is None:
            inner_state = StackedDict({})
        self.inner_state = inner_state
        self.ctor = ctor

    def when(self, **kwargs):
        return ContextStacker(self.inner_state.stack_dicts, kwargs)

    def __call__(self, **kwargs):
        with self.when(**kwargs):
            return self.ctor(**self.inner_state.merged_dict)
