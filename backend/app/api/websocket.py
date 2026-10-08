import asyncio
import json
import logging
from fastapi import WebSocket, WebSocketDisconnect
from backend.app.services.event_bus import event_bus

logger = logging.getLogger("api.websocket")


async def handle_repair_websocket(websocket: WebSocket, repair_id: str):
    await websocket.accept()
    queue = event_bus.subscribe(repair_id)

    # First send all historical events to the newly connected client
    history = event_bus.get_history(repair_id)
    for evt in history:
        await websocket.send_text(json.dumps(evt))

    try:
        while True:
            # Wait for either new events or incoming ping
            event = await queue.get()
            await websocket.send_text(json.dumps(event))
    except WebSocketDisconnect:
        logger.info(f"WebSocket client disconnected for {repair_id}")
    except Exception as e:
        logger.warning(f"WebSocket exception for {repair_id}: {e}")
    finally:
        event_bus.unsubscribe(repair_id, queue)
