import websockets
import asyncio

async def test():
    uri = "ws://localhost:5000/ws/chat"
    async with websockets.connect(uri) as websocket:
        await websocket.send("Привет!")
        print(await websocket.recv())

asyncio.run(test())
