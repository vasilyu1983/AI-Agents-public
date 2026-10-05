"""The six runtime verbs.

`write`, `select`, `compress`, `isolate`, `order`, `format` — composable
functions that operate on adapters and contracts. These are the building
blocks of `assemble()`, which is the one function most apps will call."""

from .composition import UnionMemoryStore
from .verbs import (
    assemble,
    compress,
    format_for_model,
    isolate,
    order,
    resolve,
    select,
    write,
)

__all__ = [
    "UnionMemoryStore",
    "assemble",
    "compress",
    "format_for_model",
    "isolate",
    "order",
    "resolve",
    "select",
    "write",
]
