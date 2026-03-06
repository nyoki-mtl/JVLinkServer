#!/usr/bin/env python3
"""Course image generation example."""

import asyncio
from pathlib import Path

from pyjvlink import Client, JVServerConfig


async def main() -> None:
    output_dir = Path("output/images/courses")
    output_dir.mkdir(parents=True, exist_ok=True)

    key = "9999999905240011"
    output_path = output_dir / "course_sample.gif"

    async with Client(JVServerConfig(port=8765)) as client:
        response = await client.save_course(key=key, filepath=str(output_path))
        print(response)


if __name__ == "__main__":
    asyncio.run(main())
