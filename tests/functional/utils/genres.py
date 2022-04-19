async def load_index(client, index: str, body):
    await client.indices.create(index, body=body, ignore=300)
