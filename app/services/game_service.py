import json
import os
import asyncio
from typing import List, Dict, Any, Tuple
from uuid import uuid1
import base64
from io import BytesIO
from datetime import datetime, timedelta

from openai import AsyncOpenAI
from openai.types.chat import ChatCompletionMessageParam
from openai.types.chat import ChatCompletionUserMessageParam, ChatCompletionAssistantMessageParam
from openai.types.chat_model import ChatModel
from PIL import Image

from core.entities.schema.game import Event, Company, Game, User, Trade
from core.entities.dto.game import TradeReqDTO
from core.config import config
from core.utils.logger import logger


COMPANY_PROMPT = """'Create me 5 imaginary companies with very short descriptions.
Theme: {theme}
You can go wild! Come up with some fun concepts!
All fields in Language: {language}
Format should in in JSON:"""

COMPANY_PROMPT_FORMAT = """
{
    "title": Brief title for the theme you created,
    "companies": [{
        "name": Name of the company,
        "description": Brief description of the company,
        "price": current stock price in number between 100 ~ 1000
    }]
}
"""

EVENT_PROMPT = """We're playing stock price games with these companies.

{companies}

At each day, we get an event related to each company and stock price change corresponding to the event.
Events should make a coherent story as a whole.
There are 7 days max, so make sure that dramatic drop / rise is included within 7 days.
Make sure 3 out of 5 companies end up going dramatically lower than the initial price on day 7,
so you should make it very difficult for people to make money in this market.

All fields in Language: {language}. Give output in Json Format:"""

EVENT_PROMPT_FORMAT = """
{
    "events": [{
        "company": company name,
        "description": What happened,
        "price": Price change number in percentage,
    }]
}
"""


class GameException(Exception):
    pass


class InvalidTradesException(GameException):
    pass


class GameService:
    def __init__(self, gpt_model: ChatModel = "gpt-4o"):
        self.openai_client = AsyncOpenAI(
            api_key=config.openai_key,
        )
        self.gpt_model = gpt_model

    async def get_companies(self, theme: str, language: str) -> Tuple[List[Company], str]:
        logger.info("Creating Companies...")
        resp = await self.openai_client.chat.completions.create(
            model=self.gpt_model,
            messages=[
                {
                    "role": "user",
                    "content": COMPANY_PROMPT.format(
                        theme=theme,
                        language=language,
                    )
                    + COMPANY_PROMPT_FORMAT,
                }
            ],
            response_format={"type": "json_object"},
        )
        data: Dict[str, Any] = json.loads(resp.choices[0].message.content or "{}")
        companies = [
            Company(
                name=c["name"],
                description=c["description"],
                price=c["price"],
            )
            for c in data["companies"]
        ]
        logger.info("Companies Creation Complete")
        logger.info("Creating Thumbnails...")
        files = await self.get_companies_thumbnail(companies)
        for i in range(len(companies)):
            companies[i].thumbnail = files[i]
        logger.info("Thumbnails creation complete")
        return companies, data.get("title", theme)

    async def get_companies_thumbnail(self, companies: List[Company]):
        tasks = []
        for c in companies:
            task = self.openai_client.images.generate(
                prompt=f"Create me an image thumbnail for the following company. Name: {c.name}, Desc: {c.description}",
                model="dall-e-3",
                size="1024x1024",
                response_format="b64_json",
            )
            tasks.append(task)

        results = await asyncio.gather(*tasks)
        files = []
        for resp in results:
            b64_json = resp.data[0].b64_json or ""
            data = base64.b64decode(b64_json)
            img = Image.open(BytesIO(data))
            fname = f"{uuid1()}.jpg"
            fpath = os.path.join(config.thumbnails_path, fname)
            img.save(fpath, "JPEG")
            files.append(fname)
        return files

    async def create_new_events(self, companies: List[Company], language: str) -> List[Event]:
        companies_prompt = ""
        for c in companies:
            companies_prompt += f"{c.name} ({c.price} Gold): {c.description}\n"

        event_prompt = (
            EVENT_PROMPT.format(
                companies=companies_prompt,
                language=language,
            )
            + EVENT_PROMPT_FORMAT
        )

        messages: List[ChatCompletionMessageParam] = [ChatCompletionUserMessageParam(role="user", content=event_prompt)]
        events: List[Event] = []
        logger.info("Creating Events...")
        for d in range(7):
            messages.append(ChatCompletionUserMessageParam(role="user", content=f"Day {d + 1}"))
            resp = await self.openai_client.chat.completions.create(
                messages=messages,
                model=self.gpt_model,
                response_format={"type": "json_object"},
            )
            msg = resp.choices[0].message
            data = json.loads(msg.content or "{}")
            for i, e in enumerate(data["events"]):
                new_event = Event(
                    day=d + 1,
                    company_id=companies[i].id,
                    description=e["description"],
                    price=e["price"],
                    happen_at=datetime.now(),
                )
                events.append(new_event)
                companies[i].events.append(new_event)

            logger.info(f"Day {d + 1} creation complete")
            messages.append(ChatCompletionAssistantMessageParam(role="assistant", content=msg.content))
        return events

    def start_game(self, game: Game):
        now = datetime.now()
        game.started_at = now
        for c in game.companies:
            for i, e in enumerate(c.events):
                e.happen_at = now + timedelta(minutes=1 * (i + 1))

    def perform_trades(self, user: User, game: Game, trade_reqs: List[TradeReqDTO]) -> List[Trade]:
        company_dict = {c.id: c for c in game.companies}
        holdings = game.get_holdings(user)
        curr_gold = user.gold

        trades: List[Trade] = []

        for t in trade_reqs:
            if t.company_id in company_dict:
                company = company_dict[t.company_id]

                price = company.prices[-1] * t.amount

                curr_gold -= price
                holdings[company.id] += t.amount

                trades.append(
                    Trade(
                        user_id=user.id,
                        game_id=game.id,
                        company_id=t.company_id,
                        day=len(company.filtered_events),
                        amount=t.amount,
                    )
                )
        if curr_gold < 0:
            raise InvalidTradesException("Insufficient gold for trades")
        for _, h in holdings.items():
            if h < 0:
                raise InvalidTradesException("Insufficient holdings for trades")

        user.gold = curr_gold
        return trades

    def get_game_result(self, game: Game) -> Dict[int, int]:
        result = {u.id: 0 for u in game.users}
        prices = {c.id: c.prices for c in game.companies}
        for t in game.trades:
            result[t.user_id] -= prices[t.company_id][t.day] * t.amount
        for u in game.users:
            holdings = game.get_holdings(u)
            for c in game.companies:
                result[u.id] += prices[c.id][-1] * holdings[c.id]

        return result

    def throws_all_stocks(self, game: Game, user: User):
        holdings = game.get_holdings(user)

        for c in game.companies:
            if holdings[c.id] > 0:
                game.trades.append(
                    Trade(
                        user_id=user.id,
                        day=7,
                        amount=-holdings[c.id],
                        company_id=c.id,
                    )
                )
                user.gold += holdings[c.id] * c.prices[-1]
