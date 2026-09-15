"""The app exists and answers a cross-origin preflight.

The frontend is cross-origin in dev. If the preflight comes back without an
allow-origin header the browser drops the response and no request reaches the API,
which is why this is evidence rather than a nicety.
"""

from fastapi.testclient import TestClient

from app.main import app

DEV_ORIGIN = "http://localhost:4200"


def test_cross_origin_preflight_is_answered_with_allow_origin() -> None:
    client = TestClient(app)

    response = client.options(
        "/quotes",
        headers={
            "Origin": DEV_ORIGIN,
            "Access-Control-Request-Method": "GET",
        },
    )

    assert "access-control-allow-origin" in response.headers
    assert response.headers["access-control-allow-origin"] == DEV_ORIGIN
