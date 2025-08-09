from __future__ import annotations
from typing import Callable, Optional
from ..core.model import AppState
from ..core.intents import Intent

class Store:
    def __init__(self, initial: AppState, reducer):
        self.state = initial
        self.reducer = reducer
        self.subs: list[Callable[[AppState], None]] = []

    def subscribe(self, fn: Callable[[AppState], None]):
        self.subs.append(fn)
        fn(self.state)

    def dispatch(self, intent: Intent, payload: Optional[object] = None):
        self.state, effects = self.reducer(self.state, intent, payload)
        for cb in self.subs:
            cb(self.state)
        for eff in effects:
            eff(lambda i, p=None: self.dispatch(i, p))