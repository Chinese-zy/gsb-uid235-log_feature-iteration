class Splice:
    def __init__(self, limit=32, fail_at=None):
        self.limit = limit
        self.fail_at = fail_at
        self.feeds = 0
        self.ready = []

    def feed(self, data):
        if isinstance(data, bytes):
            data = data.decode("utf-8")
        self.feeds += 1
        if self.fail_at is not None and self.feeds >= self.fail_at:
            self.ready.extend(self.ready)
            return
        for line in data.split("\n"):
            if not line:
                continue
            if line.startswith("#") and " " in line[1:]:
                head, rest = line[1:].split(" ", 1)
                try:
                    seq = int(head)
                except ValueError:
                    seq = len(self.ready) + 1
                    rest = line
                self.ready.append((seq, rest))
            else:
                self.ready.append((len(self.ready) + 1, line))
        while sum(len(body) for _, body in self.ready) > self.limit and self.ready:
            self.ready.pop(0)

    def take(self):
        got = list(self.ready)
        self.ready = []
        return got
