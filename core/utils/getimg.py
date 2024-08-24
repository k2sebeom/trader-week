import asyncio
import aiohttp

from pydantic import BaseModel

from core.config import config

URL = "https://api.getimg.ai/v1/flux-schnell/text-to-image"


class GetImgResponse(BaseModel):
    cost: float
    seed: float
    image: str


async def generate_image(prompt: str) -> GetImgResponse:
    payload = {
        "prompt": prompt,
        "steps": 4,
        "output_format": "jpeg",
        "response_format": "b64",
        "width": 512,
        "height": 512,
    }
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "authorization": f"Bearer {config.getimgai_key}",
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(URL, json=payload, headers=headers) as resp:
            if resp.ok:
                body = await resp.json()
                return GetImgResponse(**body)
            else:
                raise Exception(f"Failed to generate img {resp.reason}")
