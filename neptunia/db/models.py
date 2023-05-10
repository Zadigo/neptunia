import dataclasses
from dataclasses import dataclass
from functools import cached_property
from neptunia.neptunia.db import live_connection


class QuerysetIterator:
    def __init__(self, queryset):
        self.queryset = queryset

    def __iter__(self):
        queryset = self.queryset
        compiler = queryset.query.get_compiler(connection=live_connection)
        if compiler is None:
            raise
        results = compiler.execute_sql()
        for row in compiler.result_iter(results):
            yield row


class Queryset:
    def __init__(self, model=None, query=None):
        self.model = model
        self.query = query
        self._iterable_class = QuerysetIterator
        self._result_cache = None

    def __str__(self):
        return self._fetch_all()

    def __iter__(self):
        self._fetch_all()
        return iter(self._result_cache)

    def __len__(self):
        self._fetch_all()
        return len(self._result_cache)

    def _fetch_all(self):
        if self._result_cache is None:
            self._result_cache = list(self._iterable_class(self))


class Query:
    def __init__(self, model):
        self.model = model

    def get_compiler(self, connection=None):
        if connection is None:
            raise
        compiler = getattr(connection, 'compiler', None)
        if compiler is None:
            from neptunia.neptunia.db.compilers import Compiler
            return Compiler(self, connection)
        return compiler


class BaseManager:
    def __init__(self):
        """"""
        self.model = None

    @classmethod
    def from_queryset(cls, queryset_class, class_name=None):
        if class_name is None:
            class_name = f'{cls.__class__.__name__} From {queryset_class.__name__}'
        attrs = {'_queryset_class': queryset_class}
        return type(class_name, (cls,), attrs)
    
    def _model_fields(self):
        fields = dataclasses.fields(self.model)
        return {field.name for field in fields}

    def get_queryset(self):
        query = Query(self.model)
        return self._queryset_class(model=self.model, query=query)


class Manager(BaseManager.from_queryset(Queryset)):
    pass


class BaseModel:
    def __post_init__(self):
        self.manager = None
        self._prepare()

    def _prepare(self):
        if self.manager is None:
            self.manager = Manager()
            self.manager.model = self


@dataclass
class Link(BaseModel):
    id: int = None
    url: str = None
