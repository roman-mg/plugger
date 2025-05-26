import asyncio
import logging

from plugger.core.engines import DefaultEngine


async def main() -> None:
    algorithms_path = "examples/algorithms"

    engine = DefaultEngine()
    engine.plug_in(algorithms_path)
    results = await engine.run()
    logging.info(results)


if __name__ == "__main__":
    asyncio.run(main())
