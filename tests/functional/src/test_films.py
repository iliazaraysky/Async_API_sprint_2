import pytest


@pytest.mark.asyncio
async def test_search_detailed(es_client, make_get_request):
    response = await make_get_request('/')

    assert response.status == 200
    assert len(response.body) == 1
