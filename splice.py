class Splice:
    def __init__(self, limit=32, fail_at=None):
        self.limit = limit
        self.fail_at = fail_at
        self.feeds = 0
        self.open = {}
        self.open_order = []
        self.open_bytes = 0
        self.pending = {}
        self.next_seq = 1

    def feed(self, data):
        if isinstance(data, str):
            data = data.encode("utf-8")
        self.feeds += 1
        if self.fail_at is not None and self.feeds == self.fail_at:
            self.open = {}
            self.open_order = []
            self.open_bytes = 0
            return
        head = self._header(data)
        if head is not None:
            seq, size, rest = head
            if self.open_bytes + min(size, len(rest)) > self.limit:
                return
            body = rest[:size]
            if len(body) < size:
                self.open[seq] = [size, bytearray(body)]
                self.open_order.append(seq)
                self.open_bytes += len(body)
                return
            self._seal(seq, body)
            return
        if not self.open_order:
            return
        seq = self.open_order[-1]
        size, collected = self.open[seq]
        need = size - len(collected)
        collected += data[:need]
        self.open_bytes += min(need, len(data))
        if len(collected) >= size:
            self._seal(seq, bytes(collected))
            self.open_bytes -= size
            del self.open[seq]
            self.open_order.remove(seq)

    def _header(self, data):
        nl = data.find(b"\n")
        if nl < 0:
            return None
        line = data[:nl]
        if not line.startswith(b"#"):
            return None
        parts = line[1:].split(b" ")
        if len(parts) != 2:
            return None
        try:
            seq = int(parts[0])
            size = int(parts[1])
        except ValueError:
            return None
        if size < 0:
            return None
        return seq, size, data[nl + 1:]

    def _seal(self, seq, body):
        if seq < self.next_seq or seq in self.pending:
            return
        self.pending[seq] = bytes(body).replace(b"##", b"#").decode("utf-8")

    def take(self):
        out = []
        while self.next_seq in self.pending:
            out.append((self.next_seq, self.pending.pop(self.next_seq)))
            self.next_seq += 1
        return out
