import json
from typing import Dict, List
import base64
from io import BytesIO

from openai import OpenAI

from core.entities.schema.game import Event, Company
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

EVENT_PROMPT = '''We're playing stock price games with these companies.

{companies}

At each day, we get an event related to each company and stock price change corresponding to the event.

All response in Korean. Give output in Json Format:'''

EVENT_PROMPT_FORMAT = '''
{
    "events": [{
        "company": company name,
        "description": What happened,
        "price": Price change number in percentage,
    }]
}
'''

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

    def create_new_events(self, companies: List[Company]) -> List[Event]:
        companies_prompt = ''
        for c in companies:
            companies_prompt += f'{c.name} ({c.price} Gold): {c.description}\n'

        curr_day = len(companies[0].events) + 1

        event_prompt = EVENT_PROMPT.format(
            companies=companies_prompt,
        ) + EVENT_PROMPT_FORMAT

        messages = [{
            'role': 'user',
            'content': event_prompt
        }]
        for d in range(len(companies[0].events)):
            messages.append({
                'role': 'user',
                'content': f'Day {d + 1}'
            })
            messages.append({
                'role': 'assistant',
                'content': json.dumps({
                    "events": [{
                        "company": c.name,
                        "description": c.events[d].description,
                        "price": c.events[d].price,
                    } for c in companies]
                }, ensure_ascii=False, indent=2)
            })
        messages.append({
            'role': 'user',
            'content': f'Day {curr_day}'
        })
        
        resp = self.openai_client.chat.completions.create(
            model=self.gpt_model,
            messages=messages,
            response_format={"type": "json_object"},
        )
        data = json.loads(resp.choices[0].message.content)
        return [
            Event(
                day=curr_day,
                company_id=companies[i].id,
                description=e['description'],
                price=e['price'],
            )
            for i, e in enumerate(data['events'])
        ]
