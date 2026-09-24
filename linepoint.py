"""linepoint.py：提交时间线（基线：写完即返回，无序号）。"""
from __future__ import annotations


class Timeline:
    def __init__(self):
        self.data = {}
        self.commits = []
        self.reads = 0
        self.stale_reads = 0

    def commit(self, key: str, value: str, at: int) -> dict:
        """基线：没有提交序号，直接可见。"""
        self.data[key] = value
        return {"key": key}

    def read(self, key: str, at: int) -> dict:
        self.reads += 1
        return {"value": self.data.get(key), "seq": None}

    def line_point(self, seq: int) -> dict:
        raise NotImplementedError("线性化点还没实现")

    def visible_at(self, seq: int) -> dict:
        raise NotImplementedError("按序号读还没实现")

    def persist(self) -> bytes:
        raise NotImplementedError("快照还没实现")

    def restore(self, blob: bytes = None) -> dict:
        raise NotImplementedError("重启恢复还没实现")

    def stats(self) -> dict:
        return {"commits": len(self.commits), "keys": len(self.data), "reads": self.reads,
                "stale_reads": self.stale_reads}
