from typing import List


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
