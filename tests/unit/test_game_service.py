import pytest

from app.services.game_service import GameService


@pytest.fixture(scope="module")
def service() -> GameService:
    return GameService()


def test_exists(service: GameService):
    assert len(service.gpt_model) > 0
