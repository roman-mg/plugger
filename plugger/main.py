import asyncio

from plugger.core.engines import DefaultEngine


async def main() -> None:
    algorithms_path = "examples/algorithms"

    engine = DefaultEngine()
    engine.plug_in(algorithms_path)
    results = await engine.run()
    print(results)


if __name__ == "__main__":
    asyncio.run(main())
