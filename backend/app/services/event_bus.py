import asyncio
from datetime import datetime, timezone
import json
import logging
from typing import Dict, List, Any, Optional

logger = logging.getLogger("services.event_bus")


class EventBus:
    """
    Central event broadcaster for real-time frontend streaming (WebSockets / SSE).
    Maintains active subscriber queues and historical event caches per repair_id.
    """

    def __init__(self):
        self._subscribers: Dict[str, List[asyncio.Queue]] = {}
        self._history: Dict[str, List[Dict[str, Any]]] = {}

    def subscribe(self, repair_id: str) -> asyncio.Queue:
        queue = asyncio.Queue()
        if repair_id not in self._subscribers:
            self._subscribers[repair_id] = []
        self._subscribers[repair_id].append(queue)
        return queue

    def unsubscribe(self, repair_id: str, queue: asyncio.Queue) -> None:
        if repair_id in self._subscribers:
            if queue in self._subscribers[repair_id]:
                self._subscribers[repair_id].remove(queue)
            if not self._subscribers[repair_id]:
                del self._subscribers[repair_id]

    async def publish(self, repair_id: str, event_type: str, payload: Dict[str, Any]) -> None:
        event = {
            "repair_id": repair_id,
            "event_type": event_type,
            "payload": payload,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        # Store in historical log
        if repair_id not in self._history:
            self._history[repair_id] = []
        self._history[repair_id].append(event)

        logger.info(f"[{repair_id}] Event: {event_type}")

        # Broadcast to active queues
        if repair_id in self._subscribers:
            for q in list(self._subscribers[repair_id]):
                try:
                    await q.put(event)
                except Exception as e:
                    logger.warning(f"Error publishing to subscriber queue: {e}")

    def get_history(self, repair_id: str) -> List[Dict[str, Any]]:
        return list(self._history.get(repair_id, []))


event_bus = EventBus()
