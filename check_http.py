"""check_http.py：起服务、按脚本走一圈，打印验收面。"""
import json
import sys
import threading
import urllib.error
import urllib.request

from server import serve


def call(method, url, body=None):
    request = urllib.request.Request(url, data=body, method=method, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(request, timeout=5) as response:
            return response.status, response.read().decode()
    except urllib.error.HTTPError as error:
        return error.code, error.read().decode()


def parse(text):
    try:
        return json.loads(text)
    except Exception:
        return {"_raw": (text or "")[:60]}


def main() -> int:
    spec = json.load(open(sys.argv[1] if len(sys.argv) > 1 else "sample/ops.json", encoding="utf-8"))
    server = serve(0)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    base = "http://127.0.0.1:%d" % server.server_port
    seqs = []
    for step in spec["ops"]:
        result = parse(call("POST", base + "/" + step["op"], json.dumps(step).encode())[1])
        if step["op"] == "commit":
            seqs.append((step["key"], result.get("seq")))
    points = [parse(call("POST", base + "/line_point", json.dumps({"seq": seq}).encode())[1])
              for seq in spec["line_seqs"]]
    visible = [parse(call("POST", base + "/visible", json.dumps({"seq": seq}).encode())[1])
               for seq in spec["visible_seqs"]]
    stats = parse(call("GET", base + "/")[1])
    recovered = parse(call("POST", base + "/recover", b"{}")[1])
    print("提交序号 =", seqs)
    print("各序号的线性化点 =", [item.get("point") for item in points])
    print("按序号读到的值 =", [item.get("value") for item in visible])
    print("提交总数 =", stats.get("commits"))
    print("读取次数 =", stats.get("reads"))
    print("读到旧值的次数 =", stats.get("stale_reads"))
    print("恢复后的提交数 =", recovered.get("commits"))
    print("不变量（序号单调且可见性沿序号不回退） =", spec["monotonic_invariant"])
    print("提交次数 =", len([step for step in spec["ops"] if step["op"] == "commit"]))
    server.shutdown()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
