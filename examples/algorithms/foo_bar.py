from core.base import BaseAlgorithm, Result


class FooBar(BaseAlgorithm):
    async def __call__(self, *args, **kwargs) -> Result:
        if kwargs.get("arg"):
            return Result(True)

        return Result(False)
