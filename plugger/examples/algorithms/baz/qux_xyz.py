from collections.abc import Iterable

from plugger.core.base import BaseAlgorithm, Result


class QuxXyz(BaseAlgorithm):
    async def __call__(self, *args, **kwargs) -> Iterable[Result]:  # type: ignore
        if kwargs.get("arg"):
            return [Result(True)]

        return [Result(False)]
