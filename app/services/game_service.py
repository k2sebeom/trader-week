import json
from typing import Dict, List
import base64
from io import BytesIO

from openai import OpenAI
from pydantic import BaseModel

from core.config import config
from PIL import Image


COMPANY_PROMPT = ''''Create me 5 imaginary companies with very short descriptions.
You can go wild! Come up with some fun concepts! All response in korean
Format should in in JSON
{
    "companies": [{
        "name": Name of the company,
        "description": Brief description of the company,
        "price": current stock price in number between 100 ~ 1000
    }]
}
'''

class Company(BaseModel):
    name: str
    description: str
    price: int


class GameService:
    def __init__(self, gpt_model: str = 'gpt-4o'):
        self.openai_client = OpenAI(
            api_key=config.openai_key,
        )
        self.gpt_model = gpt_model
    
    def get_companies(self) -> List[Company]:
        resp = self.openai_client.chat.completions.create(
            model=self.gpt_model,
            messages=[
                {
                    'role': 'user',
                    'content': COMPANY_PROMPT,
                }
            ],
            response_format={"type": "json_object"},
        )
        data = json.loads(resp.choices[0].message.content)
        return [
            Company(
                name=c['name'],
                description=c['description'],
                price=c['price'],
            ) for c in data['companies']
        ]

    def get_company_thumbnail(self, company: Company):
        resp = self.openai_client.images.generate(
            prompt=f'Create me an image thumbnail for the following company. Name: {company.name}, Desc: {company.description}',
            model='dall-e-3',
            size='1024x1024',
            response_format='b64_json',
        )
        b64_json = resp.data[0].b64_json
        data = base64.b64decode(b64_json)
        img = Image.open(BytesIO(data))
        img.save(f'{company.name}.jpg', 'JPEG')
