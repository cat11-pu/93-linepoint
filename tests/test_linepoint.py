import json
import threading
import unittest
import urllib.error
import urllib.request

from linepoint import Timeline
from server import serve

class TestTimeline(unittest.TestCase):
    def test_commit_records(self):
        timeline = Timeline()
        timeline.commit("a", "1", 1)
        self.assertEqual(timeline.stats()["keys"], 1)

    def test_read_value(self):
        timeline = Timeline()
        timeline.commit("a", "1", 1)
        self.assertEqual(timeline.read("a", 2)["value"], "1")

    def test_read_missing(self):
        self.assertIsNone(Timeline().read("zz", 1)["value"])

    def test_stats_shape(self):
        self.assertIn("commits", Timeline().stats())

    def test_http_commit_read(self):
        server = serve(0)
        threading.Thread(target=server.serve_forever, daemon=True).start()
        base = "http://127.0.0.1:%d" % server.server_port
        urllib.request.urlopen(base + "/commit", data=b'{"key": "a", "value": "1", "at": 1}', timeout=5).read()
        with urllib.request.urlopen(base + "/read", data=b'{"key": "a", "at": 2}', timeout=5) as response:
            self.assertEqual(json.loads(response.read())["value"], "1")
        server.shutdown()
