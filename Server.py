#!/usr/bin/env python

import asyncio
import json
import logging
import websockets
import uuid

logging.basicConfig()

USERS = {}
VALUE = 0

def users_event():
    return json.dumps({"type": "users", "count": len(USERS)})

def value_event():
    return json.dumps({"type": "value", "value": VALUE})

async def clientConnection(websocket):
    global USERS, VALUE
    id = uuid.uuid4()
    try:
        # Register user
        USERS[id] = websocket
        websockets.broadcast(USERS.values(), users_event())
        print("Client connected->  " + str(id) + "Number of active clients -> " + str(len(USERS)))
        # Send current state to user
        await websocket.send(value_event())
        await getMessage(websocket, id)

    finally:
        # Unregister user
        USERS.pop(id)
        websockets.broadcast(USERS.values(), users_event())

async def getMessage(websocket, id):
    global VALUE
    try:
        message = await websocket.recv()
    except:
        return

    event = convertFromJson(message)

    print(str(id) + "  -> Receive Message: " + message)
    if event == None:
        await websocket.send(json.dumps({ "id":str(id), "type": "error", "value": "json format error Received Message" + message }))

    elif event.get("action") == None:
        await websocket.send(json.dumps({"id":str(id), "type": "error", "value": "Wrong key value for type"}))
    elif event["action"] == "reply":
        await websocket.send(json.dumps({"id":str(id), "type": "reply", "value": VALUE}))
    elif event["action"] == "plus":
        VALUE+=1
        await websocket.send(json.dumps({"id":str(id), "type": "plus", "value": VALUE}))
    elif event["action"] == "minus":
        VALUE-=1
        await websocket.send(json.dumps({"id":str(id), "type": "minus", "value": VALUE}))
    else :
        await websocket.send(json.dumps({"id":str(id), "type": "error", "value": "unknown error"}))

    await getMessage(websocket, id)

def convertFromJson(message):
    try:
        event = json.loads(message)
    except:
        event = None

    return event

async def main():
    async with websockets.serve(clientConnection, "localhost", 6789):
        await asyncio.Future()  # run forever

if __name__ == "__main__":
    asyncio.run(main())