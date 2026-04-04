"""Simple in-process pub/sub helpers for real-time dashboard updates."""

from queue import Queue
from threading import Lock

_listeners = []
_lock = Lock()


def subscribe():
    queue = Queue()
    with _lock:
      _listeners.append(queue)
    return queue


def unsubscribe(queue):
    with _lock:
        if queue in _listeners:
            _listeners.remove(queue)


def publish_dashboard_update(payload=None):
    message = payload or {'type': 'dashboard-updated'}
    with _lock:
        listeners = list(_listeners)

    for queue in listeners:
        queue.put(message)