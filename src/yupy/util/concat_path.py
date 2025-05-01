from typing import Union

__all__ = ('concat_path',)


def concat_path(path: str, item: Union[str, int]) -> str:
    """
    Concatenates a path string with an item (either a string or an integer)
    to create a new path.

    Args:
        path: The current path string.
        item: The item to append to the path. If it's a string, it's joined
              with a dot; if it's an integer, it's appended in square brackets.

    Returns:
        The concatenated path string.

    Raises:
        TypeError: If the item is not a string or an integer.
    """
    if isinstance(item, str):
        if not path:
            return item
        return ".".join((path, item))
    elif isinstance(item, int):
        return f"{path}[{item!r}]"
    else:
        raise TypeError("Unsupported item type")
