import asyncio
import json
import os
from collections.abc import (
    Coroutine,
    Iterable,
    Iterator,
    Sequence,
)
from typing import Any, Callable, override

import pytest

from .base import BaseAlgorithm, BaseEngine, Result


class DefaultEngine(BaseEngine):
    def __init__(self) -> None:
        super().__init__()
        self._module_extension = ".py"

    @override
    def plug_in(self, base_path: str, *args: Any, **kwargs: Any) -> None:
        if not base_path:
            return

        for module_name in os.listdir(base_path):
            if module_name in ["__pycache__", "__init__.py"]:
                continue

            module_path: str = os.path.join(base_path, module_name)
            if os.path.isdir(module_path):
                self.plug_in(module_path, *args, **kwargs)
            elif os.path.isfile(module_path) and module_name.endswith(self._module_extension):
                class_name: str = self._get_class_name(module_name)
                algorithm: BaseAlgorithm = self._create_instance(module_path, class_name)
                self._algorithms.append(algorithm)

    @override
    async def run(self, *args: Any, **kwargs: Any) -> dict[str, Result | Sequence[Result] | Exception]:  # type: ignore
        tasks: Iterable[Coroutine] = [algorithm(args, kwargs) for algorithm in self._algorithms]
        results: Iterable[Result | Exception] = await asyncio.gather(*tasks, return_exceptions=True)

        report: dict = {}
        for algorithm, result in zip(self._algorithms, results):
            report[algorithm.get_id()] = result

        return report

    def _get_class_name(self, module_name: str) -> str:
        # convert from "foo_bar.py" to "FooBar"
        class_name: str = ""
        for word in module_name.replace(self._module_extension, "").split("_"):
            if word:
                class_name += word[0].upper()

            if len(word) > 1:
                class_name += word[1:]

        return class_name


class PyTestJsonEngine(DefaultEngine):
    def __init__(self) -> None:
        super().__init__()
        self._algorithms: list[tuple[BaseAlgorithm, Iterable[dict]]] = []  # type: ignore
        self._tests_extension: str = ".json"

    def plug_in(self, base_path: str, *args: Any, **kwargs: Any) -> None:
        base_tests_path: str = kwargs.get("base_tests_path")  # type: ignore
        if not base_path or not base_tests_path:
            return

        for module_name in os.listdir(base_path):
            if module_name in ["__pycache__", "__init__.py"]:
                continue

            module_path: str = os.path.join(base_path, module_name)
            tests_name: str = module_name.replace(self._module_extension, self._tests_extension)
            tests_path: str = os.path.join(base_tests_path, tests_name)
            if os.path.isdir(module_path) and os.path.isdir(tests_path):
                self.plug_in(base_path=module_path, base_tests_path=tests_path)
            elif (
                os.path.isfile(module_path)
                and module_name.endswith(self._module_extension)
                and os.path.isfile(tests_path)
                and tests_path.endswith(self._tests_extension)
            ):
                class_name: str = self._get_class_name(module_name)
                algorithm: BaseAlgorithm = self._create_instance(module_path, class_name)
                test_cases: Iterable[dict] = self._load_test_cases(tests_path)

                self._algorithms.append((algorithm, test_cases))

    def run(self, *args: Any, **kwargs: Any) -> Iterator[Callable]:  # type: ignore
        for algorithm, test_cases in self._algorithms:
            test_function: Callable = self._generate_test_function(algorithm, test_cases)
            yield test_function

    @staticmethod
    def _load_test_cases(path: str) -> Iterable[dict]:
        with open(path) as file:
            return json.load(file)

    def _generate_test_function(self, algorithm: BaseAlgorithm, test_cases: Iterable[dict]) -> Callable:
        @pytest.mark.parametrize("params", test_cases)
        @pytest.mark.asyncio
        async def test_function(params: dict) -> None:
            input_arguments, expected_result = self._mock(params)

            result: Result | Sequence[Result] = await algorithm(**input_arguments)

            index = expected_result.get("index")
            if index is not None and isinstance(result, Sequence):
                assert result[index].status == expected_result.get("status")
            elif index is None and isinstance(result, Result):
                assert result.status == expected_result.get("status")
            else:
                raise AssertionError("Test inconsistency.")

        test_function.__name__ = f"test_{algorithm.get_id()}"
        return test_function

    @staticmethod
    def _mock(params: dict) -> tuple[dict, dict]:
        input_arguments = {params.get("argument", ""): params.get("input")}
        return input_arguments, params.get("expected_result", {})
