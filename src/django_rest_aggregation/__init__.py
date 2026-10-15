from importlib.metadata import version
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .mixins import AggregationMixin

__version__ = version("django_rest_aggregation")
__all__ = ["AggregationMixin", "__version__"]


def __getattr__(name: str) -> object:
    # Imported lazily: the mixin imports DRF, which needs configured Django settings.
    if name == "AggregationMixin":
        from .mixins import AggregationMixin

        return AggregationMixin
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
