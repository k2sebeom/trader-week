from typing import List, Dict
from datetime import datetime, timedelta

from core.entities.schema.game import Trade, Company, Event


def filter_events(events: List[Event], started: bool = False) -> List[Event]:
    now = datetime.now()
    if not started:
        return []
    return list(filter(lambda e: (e.happen_at - now) < timedelta(seconds=0), events))


def get_prices(initial_price: int, events: List[Event]) -> List[int]:
    history = [initial_price]
    for e in events:
        initial_price += int(initial_price * e.price / 100)
        history.append(initial_price)
    return history


def get_holdings(user_id: int, companies: List[Company], trades: List[Trade]) -> Dict[int, int]:
    holding = {
        c.id: 0
        for c in companies
    }
    for t in filter(lambda t: t.user_id == user_id, trades):
        holding[t.company_id] += t.amount
    return holding
