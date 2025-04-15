import importlib
import types
from abc import ABC, ABCMeta, abstractmethod
from dataclasses import dataclass
from typing import Any, Iterable, List, Optional, Sequence


@dataclass(frozen=True, slots=True)
class Result:
    status: bool
    metadata: Optional[Any] = None


class BaseAlgorithm(ABC):
    def __init__(self) -> None:
        self._id: str = self.__class__.__module__

    @abstractmethod
    async def __call__(self, *args: Any, **kwargs: Any) -> Result | Sequence[Result]: ...

    def get_id(self) -> str:
        return self._id


class BaseEngine(ABC):
    def __init__(self) -> None:
        self._algorithms: List[BaseAlgorithm] = []

    @abstractmethod
    def plug_in(self, base_path: str, *args: Any, **kwargs: Any) -> None: ...

    @abstractmethod
    async def run(self, *args: Any, **kwargs: Any) -> Iterable[Result | Sequence[Result] | Exception]: ...

    @staticmethod
    def _create_instance(module_path: str, class_name: str, **kwargs: Any) -> BaseAlgorithm:
        import_module_path: str = module_path.replace("/", ".").replace("\\", ".").replace(".py", "")
        module: types.ModuleType = importlib.import_module(import_module_path)
        attribute: ABCMeta = getattr(module, class_name)
        return attribute(**kwargs)
