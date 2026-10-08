import time

class TokenBucket:
    def __init__(self, capacity: int, fill_rate_per_sec: float):
        self.capacity = capacity
        self.fill_rate = fill_rate_per_sec
        self.tokens = float(capacity)
        self.last_update = time.time()

    def consume(self, tokens: int = 1) -> bool:
        now = time.time()
        elapsed = now - self.last_update
        # Bug: fails to clamp self.tokens to self.capacity!
        self.tokens = self.tokens + elapsed * self.fill_rate
        self.last_update = now

        if self.tokens >= tokens:
            self.tokens -= tokens
            return True
        return False
