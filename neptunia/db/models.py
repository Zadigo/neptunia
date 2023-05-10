import dataclasses
from dataclasses import dataclass


class QuerysetIterator:
    def __iter__(self, queryset):
        pass 


class Queryset:
    queryset_iterator = QuerysetIterator()

    def __init__(self, items=[]):
        self.cache = items

    def __str__(self):
        return self.get_queryset()
    
    def get_queryset(self):
        if self.cache is None:
            return []
        return []


class BaseManager:
    def __init__(self):
        self.query = None
        self.compiler = None
        self._model = None

    def __get__(self, instance, cls=None):
        self._model = instance
        self.compiler = instance.compiler
        connection = self.compiler.get_connection
        setattr(self, 'connection', connection)
        result = connection.execute(self.query)
        queryset = Queryset(items=result)
        setattr(self, 'queryset', queryset)
        return self
    
    def _model_fields(self):
        fields = dataclasses.fields(self._model)
        return {field.name for field in fields}
    
    def all(self):
        self.compiler.select.format()
        sql = self.compiler.compile()


class BaseModel:
    objects = BaseManager()


@dataclass
class Link(BaseModel):
    id: int
    url: str

