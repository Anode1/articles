"""cdp.py: the smallest Chrome DevTools Protocol client the grader needs.

Boots headless Chrome against a local static server, evaluates JS in the
page, returns JSON values. Nothing else. Chrome runs --headless=new with
--ozone-platform=headless; no window can reach a display.
"""
import json, os, shutil, socket, subprocess, tempfile, time, urllib.request

import websocket

CHROME = os.environ.get("CHROME", "google-chrome")


def free_port():
    s = socket.socket()
    s.bind(("", 0))
    p = s.getsockname()[1]
    s.close()
    return p


class Page:
    def __init__(self):
        self.port = free_port()
        self.profile = tempfile.mkdtemp(prefix="cdp-")
        self.proc = subprocess.Popen(
            [CHROME, "--headless=new", "--ozone-platform=headless",
             "--disable-gpu", "--no-first-run", "--disable-extensions",
             f"--remote-debugging-port={self.port}",
             f"--user-data-dir={self.profile}", "about:blank"],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            env={**os.environ, "DISPLAY": "", "WAYLAND_DISPLAY": ""})
        self.ws = None
        self.msg_id = 0
        for _ in range(100):
            try:
                tabs = json.load(urllib.request.urlopen(
                    f"http://127.0.0.1:{self.port}/json/list", timeout=2))
                tab = next(t for t in tabs if t["type"] == "page")
                self.ws = websocket.create_connection(
                    tab["webSocketDebuggerUrl"], timeout=30,
                    suppress_origin=True)
                break
            except Exception:
                time.sleep(0.2)
        if not self.ws:
            self.close()
            raise RuntimeError("chrome did not come up")

    def cmd(self, method, **params):
        self.msg_id += 1
        self.ws.send(json.dumps({"id": self.msg_id, "method": method,
                                 "params": params}))
        while True:
            msg = json.loads(self.ws.recv())
            if msg.get("id") == self.msg_id:
                if "error" in msg:
                    raise RuntimeError(f"{method}: {msg['error']}")
                return msg.get("result", {})

    def goto(self, url):
        self.cmd("Page.enable")
        self.cmd("Page.navigate", url=url)
        # loadEventFired arrives as an event; poll readyState instead.
        for _ in range(100):
            if self.eval("document.readyState") == "complete":
                return
            time.sleep(0.1)
        raise RuntimeError("page did not load")

    def eval(self, expr):
        r = self.cmd("Runtime.evaluate", expression=expr,
                     returnByValue=True, awaitPromise=True)
        if "exceptionDetails" in r:
            d = r["exceptionDetails"]
            raise RuntimeError(d.get("exception", {}).get("description",
                                                          str(d))[:500])
        return r["result"].get("value")

    def close(self):
        try:
            if self.ws:
                self.ws.close()
        except Exception:
            pass
        self.proc.terminate()
        self.proc.wait()
        shutil.rmtree(self.profile, ignore_errors=True)


class Server:
    """Static file server for one directory on a free port."""

    def __init__(self, directory):
        self.port = free_port()
        self.proc = subprocess.Popen(
            ["python3", "-m", "http.server", str(self.port),
             "--bind", "127.0.0.1", "--directory", directory],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        for _ in range(50):
            try:
                socket.create_connection(("127.0.0.1", self.port), 0.5).close()
                return
            except OSError:
                time.sleep(0.1)
        raise RuntimeError("server did not come up")

    def url(self):
        return f"http://127.0.0.1:{self.port}/"

    def close(self):
        self.proc.terminate()
        self.proc.wait()
