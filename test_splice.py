import unittest
from splice import Splice

def frame(seq, body):
    raw = body.encode()
    return f"#{seq} {len(raw)}\n".encode() + raw

class SpliceTest(unittest.TestCase):
    def test_multiline_stays_one(self):
        s = Splice()
        s.feed(frame(1, "hello\nworld"))
        self.assertEqual(s.take(), [(1, "hello\nworld")])

    def test_marker_inside_body(self):
        body = "see #2 1\nx"
        s = Splice()
        s.feed(frame(1, body))
        self.assertEqual(s.take(), [(1, body)])

    def test_marker_on_seam(self):
        body = "ab\n#9"
        s = Splice()
        s.feed(frame(1, body))
        self.assertEqual(s.take(), [(1, body)])

    def test_doubled_marker_is_one(self):
        s = Splice()
        s.feed(frame(1, "a##b"))
        self.assertEqual(s.take(), [(1, "a#b")])

    def test_inner_marker_does_not_close_outer(self):
        inner = frame(9, "z")
        body = "A" + inner.decode() + "B"
        s = Splice()
        s.feed(frame(1, body))
        self.assertEqual(s.take(), [(1, body)])

    def test_stack_line_is_not_a_record(self):
        body = "boom\n# File app.py"
        s = Splice()
        s.feed(frame(1, body))
        self.assertEqual(s.take(), [(1, body)])

    def test_same_seq_once(self):
        s = Splice()
        s.feed(frame(1, "ok"))
        s.feed(frame(1, "ok"))
        self.assertEqual(s.take(), [(1, "ok")])

    def test_gap_holds_later(self):
        s = Splice()
        s.feed(frame(1, "a"))
        s.feed(frame(3, "c"))
        self.assertEqual(s.take(), [(1, "a")])
        s.feed(frame(2, "b"))
        self.assertEqual(s.take(), [(2, "b"), (3, "c")])

    def test_arrival_order_does_not_win(self):
        s = Splice()
        s.feed(frame(2, "b"))
        s.feed(frame(1, "a"))
        self.assertEqual(s.take(), [(1, "a"), (2, "b")])

    def test_cap_rejects_new_keeps_old(self):
        s = Splice(limit=8)
        s.feed(b"#1 20\nhello")
        s.feed(frame(2, "zzzz"))
        self.assertEqual(s.take(), [])
        rest = b"world\nxxxxx!!!!"
        self.assertEqual(len(rest), 15)
        s.feed(rest)
        self.assertEqual(s.take(), [(1, "hello" + rest.decode())])

    def test_fail_drops_partial_keeps_sealed(self):
        s = Splice(fail_at=2)
        s.feed(frame(1, "ok"))
        self.assertEqual(s.take(), [(1, "ok")])
        s.feed(b"#2 20\nhello")
        self.assertEqual(s.take(), [])
        s.feed(frame(2, "bb"))
        self.assertEqual(s.take(), [(2, "bb")])

if __name__ == "__main__":
    unittest.main()
