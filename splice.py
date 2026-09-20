import re

HEADER = re.compile(rb"#(\d+) (\d+)\n")


class Splice:
    def __init__(self, limit=1 << 20, fail_at=None):
        self.limit = limit
        self.fail_at = fail_at
        self.feeds = 0
        self.buf = bytearray()
        self.pending = {}
        self.ready = []
        self.next_seq = 1

    def feed(self, data):
        if isinstance(data, str):
            data = data.encode("utf-8")
        self.feeds += 1
        if self.fail_at is not None and self.feeds == self.fail_at:
            self.buf.clear()
            return
        if len(self.buf) > self.limit and HEADER.match(data):
            return
        self.buf += data
        self._parse()

    def _parse(self):
        while self.buf:
            m = HEADER.match(self.buf)
            if m:
                start = m.end()
                need = int(m.group(2))
                if len(self.buf) - start < need:
                    return
                seq = int(m.group(1))
                raw = bytes(self.buf[start:start + need])
                del self.buf[:start + need]
                self._seal(seq, raw)
                continue
            nl = self.buf.find(b"\n")
            if self.buf[:1] == b"#" and nl == -1:
                return
            if nl == -1:
                self.buf.clear()
                return
            del self.buf[:nl + 1]

    def _seal(self, seq, raw):
        body = raw.replace(b"##", b"#").decode("utf-8", "replace")
        if seq < self.next_seq or seq in self.pending:
            return
        self.pending[seq] = body
        while self.next_seq in self.pending:
            self.ready.append((self.next_seq, self.pending.pop(self.next_seq)))
            self.next_seq += 1

    def take(self):
        got = list(self.ready)
        self.ready = []
        return got
