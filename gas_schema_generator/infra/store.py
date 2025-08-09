from __future__ import annotations

from typing import Callable, List, Tuple

from ..core.intents import Intent
from ..core.model import AppState

Dispatcher = Callable[[Intent, object | None], None]
Effect = Callable[[Dispatcher], None]
Reducer = Callable[[AppState, Intent, object | None], Tuple[AppState, List[Effect]]]
Subscriber = Callable[[AppState], None]


class Store:
    def __init__(self, initial: AppState, reducer: Reducer) -> None:
        self.state: AppState = initial
        self.reducer: Reducer = reducer
        self.subs: List[Subscriber] = []

    def subscribe(self, fn: Subscriber) -> None:
        self.subs.append(fn)
        fn(self.state)

    def _dispatch_cb(self, i: Intent, p: object | None = None) -> None:
        self.dispatch(i, p)

    def dispatch(self, intent: Intent, payload: object | None = None) -> None:
        self.state, effects = self.reducer(self.state, intent, payload)
        for cb in self.subs:
            cb(self.state)
        for eff in effects:
            eff(self._dispatch_cb)
