#!/usr/bin/env python3
"""Uniform image generation example."""

import asyncio
from pathlib import Path

from pyjvlink import Client, JVServerConfig


async def main() -> None:
    output_dir = Path("output/images/uniforms")
    output_dir.mkdir(parents=True, exist_ok=True)

    pattern = "水色，赤山形一本輪，水色袖"
    output_path = output_dir / "uniform_sample.bmp"

    async with Client(JVServerConfig(port=8765)) as client:
        response = await client.save_uniform(pattern=pattern, filepath=str(output_path))
        print(response)


if __name__ == "__main__":
    asyncio.run(main())
