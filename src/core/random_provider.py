import random


class RandomProvider:
    def __init__(self, seed: int):
        self.seed = seed
        self.random = random.Random(seed)

    def choice(self, values):
        return self.random.choice(values)

    def sample(self, values, count):
        return self.random.sample(values, count)

    def randint(self, start: int, end: int) -> int:
        return self.random.randint(start, end)

    def shuffle(self, values) -> None:
        self.random.shuffle(values)

