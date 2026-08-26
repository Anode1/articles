"""equiv.py: verify the two builds are equivalent at the HTTP boundary.

Starts both servers, replays the probe cases, and compares status, parsed
JSON body (order-insensitive), and the headers the graded checks pin
(WWW-Authenticate). Run before the experiment; any mismatch fails loudly.

The probes cover the contract the tasks and checks live in. Outside it the
sides diverge: a POST body missing a field gets 400 from plain (visible
validation) and 500 from Spring (the database constraint); no task or
check touches that case.

  javac -cp h2.jar plain/App.java && (cd spring && ./gradlew -q bootJar)
  python3 equiv.py
"""
import json, os, socket, subprocess, sys, time, urllib.request, urllib.error

here = os.path.dirname(os.path.abspath(__file__))

PROBES = [
    ("GET", "/items", "t-alice", None),
    ("GET", "/items?author=alice", "t-alice", None),
    ("GET", "/items?author=nobody", "t-alice", None),
    ("GET", "/items", "t-bob", None),
    ("GET", "/items", None, None),
    ("GET", "/items", "t-wrong", None),
    ("POST", "/items", "t-alice", {"author": "alice", "name": "probe"}),
    ("POST", "/items", None, {"author": "alice", "name": "probe"}),
]


def free_port():
    s = socket.socket()
    s.bind(("", 0))
    p = s.getsockname()[1]
    s.close()
    return p


def wait_up(port):
    for _ in range(120):
        try:
            socket.create_connection(("127.0.0.1", port), 0.5).close()
            return
        except OSError:
            time.sleep(0.5)
    raise SystemExit("server did not come up")


def call(port, method, path, token, body):
    req = urllib.request.Request(f"http://127.0.0.1:{port}{path}",
                                 method=method,
                                 data=json.dumps(body).encode() if body else None)
    if token:
        req.add_header("Authorization", "Bearer " + token)
    if body:
        req.add_header("Content-Type", "application/json")
    try:
        r = urllib.request.urlopen(req, timeout=10)
        code, hdrs, data = r.status, r.headers, r.read()
    except urllib.error.HTTPError as e:
        code, hdrs, data = e.code, e.headers, e.read()
    try:
        parsed = json.loads(data) if data else None
    except ValueError:
        parsed = data.decode(errors="replace")
    hl = {k.lower(): v for k, v in hdrs.items()}
    return code, parsed, hl.get("www-authenticate")


def start(side, port):
    if side == "plain":
        return subprocess.Popen(
            ["java", "-cp", "." + os.pathsep + os.path.join(here, "h2.jar"),
             "App", str(port)],
            cwd=os.path.join(here, "plain"),
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return subprocess.Popen(
        ["java", "-jar", "build/libs/endpoint.jar", f"--server.port={port}"],
        cwd=os.path.join(here, "spring"),
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


if __name__ == "__main__":
    results = {}
    for side in ("plain", "spring"):
        port = free_port()
        p = start(side, port)
        try:
            wait_up(port)
            time.sleep(2 if side == "spring" else 0.5)
            results[side] = [call(port, *pr) for pr in PROBES]
        finally:
            p.terminate()
            p.wait()
    bad = 0
    for i, (a, b) in enumerate(zip(results["plain"], results["spring"])):
        if a != b:
            bad += 1
            print(f"MISMATCH probe {i} {PROBES[i][:2]}:\n  plain  {a}\n  spring {b}")
    print(f"{len(PROBES)} probes, {bad} mismatches")
    sys.exit(1 if bad else 0)
