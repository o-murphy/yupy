from typing import Protocol, Any, runtime_checkable

__all__ = ('Comparable',)


@runtime_checkable
class Comparable(Protocol):
    """
    A protocol for types that support comparison operations.  Provides
    default implementations for all rich comparison methods
    based on __eq__ and __lt__.
    """

    def __eq__(self, other: Any) -> bool:
        """
        Equality comparison.
        """
        raise NotImplementedError

    def __lt__(self, other: Any) -> bool:
        """
        Less-than comparison.
        """
        raise NotImplementedError

    def __le__(self, other: Any) -> bool:
        """
        Less-than-or-equal-to comparison.
        """
        return (self < other) or (self == other)  # Default implementation

    def __gt__(self, other: Any) -> bool:
        """
        Greater-than comparison.
        """
        return not (self <= other)  # Default implementation

    def __ge__(self, other: Any) -> bool:
        """
        Greater-than-or-equal-to comparison.
        """
        return not (self < other)  # Default implementation

    def __ne__(self, other: Any) -> bool:
        """
        Not-equal-to comparison.
        """
        return not (self == other)  # Default implementation
