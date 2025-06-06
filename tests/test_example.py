import os

from plugger.core.engines import PyTestJsonEngine


def register_tests() -> None:
    algorithms_path = os.path.join("plugger", "examples", "algorithms")
    tests_path = os.path.join("tests", "examples", "tests")

    pytest_engine = PyTestJsonEngine()
    pytest_engine.plug_in(base_path=algorithms_path, base_tests_path=tests_path)
    for test_function in pytest_engine.run():
        globals()[test_function.__name__] = test_function


register_tests()
