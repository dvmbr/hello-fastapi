from typing import Generic
from typing import TypeVar
from pydantic.generics import GenericModel

T = TypeVar("T")


class ListResponse(GenericModel, Generic[T]):
    total: int
    items: list[T]
