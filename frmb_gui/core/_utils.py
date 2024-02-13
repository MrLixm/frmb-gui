import re
from typing import Any

import unicodedata


def slugify(object_: Any, allow_unicode: bool = False) -> str:
    """
    Generate a more simple string and filesystem-safe representation of the given object.

    Characters allowed are `A-Z a-z 0-9 _ - .` anything else is replaced by a carret
    or just removed.

    Convert to ASCII if ``allow_unicode`` is *False*.

    Args:
        object_:
            Object to convert to a slug.
        allow_unicode:
            Whether to allow unicode characters in the generated slug.

    Returns:
        simplified and filesystem safe representation of the source object

    References:
        - Django Software Foundation ``slugify()``
        - https://learn.microsoft.com/en-us/windows/win32/fileio/naming-a-file#naming-conventions
    """

    value = str(object_)

    if allow_unicode:
        value = unicodedata.normalize("NFKC", value)
    else:
        value = (
            unicodedata.normalize("NFKD", value)
            .encode("ascii", "ignore")
            .decode("ascii")
        )
    value = re.sub(r"[\s\\/'\"|:,]", "-", value)
    value = re.sub(r"[^\w\-.]", "", value)
    value = re.sub(r"-{2,}", "--", value)
    return value
