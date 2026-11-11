#!/usr/bin/env python3
"""Pull lecture material from Canvas LMS for the vault's study system.

The API token is read from the macOS Keychain (service "canvas-api-token",
account = your Canvas host), or on Windows/Linux from a file OUTSIDE the vault:
~/.config/claude-study-vault/canvas-token. It is never stored in the vault,
printed, or sent anywhere except the Canvas API host.

Usage (from the vault root):
  python3 -I .claude/skills/canvas/canvas.py set-url https://yourschool.instructure.com
  python3 -I .claude/skills/canvas/canvas.py check
  python3 -I .claude/skills/canvas/canvas.py courses
  python3 -I .claude/skills/canvas/canvas.py new [--course ID] [--all]
  python3 -I .claude/skills/canvas/canvas.py fetch KEY [KEY ...] [--out DIR]
  python3 -I .claude/skills/canvas/canvas.py mark KEY [KEY ...]
  python3 -I .claude/skills/canvas/canvas.py map COURSE_ID "<folder in 100 Courses>"

Item KEYs look like  file:12345  or  page:6789:lecture-3-notes
State (course→folder map, processed items, no secrets) lives in state.json next to this script.
"""
import json
import os
import re
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
STATE = Path(os.environ.get("CANVAS_STATE") or HERE / "state.json")  # override only for tests
VAULT = HERE.parents[2]  # .claude/skills/canvas -> vault root
KEYCHAIN_SERVICE = "canvas-api-token"
TOKEN_FILE = Path.home() / ".config" / "claude-study-vault" / "canvas-token"
MAX_DOWNLOAD = 300 * 1024 * 1024
USER_AGENT = "vault-study-canvas/1.0"


def _ssl_context():
    # python.org builds of Python ship without CA certificates; use macOS's bundle.
    import ssl
    ctx = ssl.create_default_context()
    if not ctx.get_ca_certs() and Path("/etc/ssl/cert.pem").is_file():
        ctx = ssl.create_default_context(cafile="/etc/ssl/cert.pem")
    return ctx


SSL_CTX = _ssl_context()


# ---------- state ----------

def load_state():
    if STATE.exists():
        return json.loads(STATE.read_text())
    return {"base_url": None, "courses": {}, "processed": {}}


def save_state(st):
    STATE.write_text(json.dumps(st, indent=2, ensure_ascii=False) + "\n")


# ---------- auth / http ----------

def token(host):
    t = os.environ.get("CANVAS_TOKEN")  # only for local testing
    if t:
        return t.strip()
    if sys.platform == "darwin" and Path("/usr/bin/security").exists():
        res = subprocess.run(
            ["/usr/bin/security", "find-generic-password",
             "-s", KEYCHAIN_SERVICE, "-a", host, "-w"],
            capture_output=True, text=True,
        )
        if res.returncode == 0 and res.stdout.strip():
            return res.stdout.strip()
    if TOKEN_FILE.is_file():
        if VAULT == TOKEN_FILE or VAULT in TOKEN_FILE.resolve().parents:
            sys.exit("The token file must not be inside the vault.")
        return TOKEN_FILE.read_text().strip()
    if sys.platform == "darwin":
        how = ("Add it yourself in Terminal with:\n"
               f"  security add-generic-password -s {KEYCHAIN_SERVICE} -a {host} -w\n"
               "(it asks for the token without showing it or saving it in shell history)")
    else:
        how = (f"Save it yourself, as the only line of a text file at:\n  {TOKEN_FILE}\n"
               "(outside the vault; don't paste it into the chat)")
    sys.exit(f"No Canvas token found for {host}. {how}")


class Canvas:
    def __init__(self, base_url):
        self.base = base_url.rstrip("/")
        self.host = urllib.parse.urlparse(self.base).netloc
        self._tok = token(self.host)

    def _req(self, url, auth=True):
        req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
        if auth:
            # only ever send the token to the Canvas host itself
            if urllib.parse.urlparse(url).netloc != self.host:
                raise ValueError("refusing to send the token to another host")
            req.add_header("Authorization", f"Bearer {self._tok}")
        return req

    def get(self, path, params=None):
        """GET with pagination; returns a list (or a dict for single objects)."""
        url = path if path.startswith("http") else f"{self.base}/api/v1{path}"
        if params:
            url += ("&" if "?" in url else "?") + urllib.parse.urlencode(params, doseq=True)
        out = []
        while url:
            for attempt in range(3):
                try:
                    with urllib.request.urlopen(self._req(url), timeout=60, context=SSL_CTX) as r:
                        data = json.load(r)
                        link = r.headers.get("Link", "")
                    break
                except urllib.error.HTTPError as e:
                    if e.code == 403 and "Rate Limit" in (e.read() or b"").decode("utf-8", "replace"):
                        time.sleep(2 * (attempt + 1))
                        continue
                    raise
            if isinstance(data, dict):
                return data
            out.extend(data)
            m = re.search(r'<([^>]+)>;\s*rel="next"', link)
            url = m.group(1) if m else None
        return out

    def download(self, url, dest):
        # Canvas file URLs carry their own verifier; they redirect to a storage
        # host, so they are fetched WITHOUT the token.
        req = self._req(url, auth=False)
        with urllib.request.urlopen(req, timeout=300, context=SSL_CTX) as r, open(dest, "wb") as f:
            size = 0
            while chunk := r.read(1 << 16):
                size += len(chunk)
                if size > MAX_DOWNLOAD:
                    raise ValueError("file larger than 300 MB, skipped")
                f.write(chunk)


def http_error(e):
    if isinstance(e, urllib.error.HTTPError):
        if e.code == 401:
            return "Canvas rejected the token (401). It may be expired or deleted; make a new one and update the Keychain."
        if e.code == 403:
            return "Not allowed (403): this course hides that part of Canvas from students."
        if e.code == 404:
            return "Not found (404)."
        return f"HTTP {e.code}"
    return str(e)


# ---------- helpers ----------

def safe_name(name):
    name = re.sub(r"[/\\:\x00-\x1f]", "-", name).strip(" .")
    return name[:150] or "file"


def emit(obj):
    print(json.dumps(obj, indent=2, ensure_ascii=False))


def course_items(cv, cid):
    """File and Page items from the course's modules, in module order."""
    items, notes = [], []
    try:
        modules = cv.get(f"/courses/{cid}/modules", {"include[]": "items", "per_page": 100})
    except Exception as e:
        modules = []
        notes.append(f"modules: {http_error(e)}")
    for mod in modules:
        mod_items = mod.get("items")
        if mod_items is None:  # large modules don't inline items
            try:
                mod_items = cv.get(f"/courses/{cid}/modules/{mod['id']}/items", {"per_page": 100})
            except Exception as e:
                notes.append(f"module {mod.get('name')}: {http_error(e)}")
                mod_items = []
        for it in mod_items:
            if it.get("type") == "File":
                items.append({"key": f"file:{it['content_id']}", "kind": "file",
                              "module": mod.get("name"), "title": it.get("title")})
            elif it.get("type") == "Page":
                items.append({"key": f"page:{cid}:{it['page_url']}", "kind": "page",
                              "module": mod.get("name"), "title": it.get("title")})
    if not items:  # course without modules: fall back to the Files area
        try:
            for f in cv.get(f"/courses/{cid}/files", {"per_page": 100, "sort": "created_at"}):
                items.append({"key": f"file:{f['id']}", "kind": "file", "module": "Files",
                              "title": f.get("display_name"), "size": f.get("size"),
                              "updated": f.get("updated_at")})
        except Exception as e:
            notes.append(f"files: {http_error(e)}")
    return items, notes


# ---------- commands ----------

def cmd_check(cv, st, args):
    me = cv.get("/users/self")
    emit({"ok": True, "name": me.get("name"), "base_url": cv.base})


def cmd_courses(cv, st, args):
    courses = cv.get("/courses", {"enrollment_state": "active", "per_page": 100})
    emit([{"id": c["id"], "name": c.get("name"), "code": c.get("course_code"),
           "vault_folder": st["courses"].get(str(c["id"]))}
          for c in courses if c.get("name")])


def cmd_set_url(cv, st, args):
    if len(args) != 1 or not args[0].startswith("https://"):
        sys.exit("usage: set-url https://yourschool.instructure.com")
    p = urllib.parse.urlparse(args[0])
    st["base_url"] = f"https://{p.netloc}"
    save_state(st)
    emit({"base_url": st["base_url"], "keychain_account": p.netloc})


def cmd_map(cv, st, args):
    if len(args) != 2:
        sys.exit('usage: map COURSE_ID "<folder in 100 Courses>"')
    cid, folder = args
    if not (VAULT / "100 Courses" / folder).is_dir():
        sys.exit(f'"100 Courses/{folder}" does not exist. Ask the user before creating a folder.')
    st["courses"][cid] = folder
    save_state(st)
    emit({"mapped": cid, "folder": folder})


def cmd_new(cv, st, args):
    show_all = "--all" in args
    only = args[args.index("--course") + 1] if "--course" in args else None
    cids = [only] if only else list(st["courses"])
    if not cids:
        sys.exit("No courses mapped yet. Run `courses`, then `map COURSE_ID \"<folder>\"`.")
    result = []
    for cid in cids:
        items, notes = course_items(cv, cid)
        if not show_all:
            items = [i for i in items if i["key"] not in st["processed"]]
        result.append({"course_id": cid, "vault_folder": st["courses"].get(cid),
                       "items": items, "notes": notes})
    emit(result)


def cmd_fetch(cv, st, args):
    out = None
    if "--out" in args:
        i = args.index("--out")
        out = Path(args[i + 1]).expanduser().resolve()
        del args[i:i + 2]
    if out is None:
        out = Path(tempfile.mkdtemp(prefix="canvas-"))
    if out == VAULT or VAULT in out.parents:
        sys.exit("Refusing to download into the vault. Use a temporary folder; /learn copies what's needed.")
    out.mkdir(parents=True, exist_ok=True)
    results = []
    for key in args:
        try:
            if key.startswith("file:"):
                meta = cv.get(f"/files/{key.split(':', 1)[1]}")
                if meta.get("size") and meta["size"] > MAX_DOWNLOAD:
                    raise ValueError("file larger than 300 MB, skipped")
                dest = out / safe_name(meta.get("display_name") or meta.get("filename") or key)
                cv.download(meta["url"], dest)
                results.append({"key": key, "path": str(dest), "title": meta.get("display_name"),
                                "updated": meta.get("updated_at")})
            elif key.startswith("page:"):
                _, cid, url = key.split(":", 2)
                page = cv.get(f"/courses/{cid}/pages/{urllib.parse.quote(url)}")
                dest = out / (safe_name(page.get("title") or url) + ".html")
                dest.write_text(f"<h1>{page.get('title', '')}</h1>\n{page.get('body') or ''}", "utf-8")
                results.append({"key": key, "path": str(dest), "title": page.get("title"),
                                "updated": page.get("updated_at")})
            else:
                raise ValueError("unknown key type")
        except Exception as e:
            results.append({"key": key, "error": http_error(e)})
    emit({"folder": str(out), "items": results})


def cmd_mark(cv, st, args):
    today = time.strftime("%Y-%m-%d")
    for key in args:
        st["processed"][key] = today
    save_state(st)
    emit({"marked": args})


COMMANDS = {"set-url": cmd_set_url, "check": cmd_check, "courses": cmd_courses, "map": cmd_map,
            "new": cmd_new, "fetch": cmd_fetch, "mark": cmd_mark}


def main():
    if len(sys.argv) < 2 or sys.argv[1] not in COMMANDS:
        print(__doc__)
        sys.exit(2)
    st = load_state()
    cmd, args = sys.argv[1], sys.argv[2:]
    base = os.environ.get("CANVAS_URL") or st.get("base_url")
    if cmd in ("mark", "map", "set-url"):
        cv = None
    elif not base:
        sys.exit("No Canvas address set yet. Run: set-url https://yourschool.instructure.com")
    else:
        cv = Canvas(base)
    try:
        COMMANDS[cmd](cv, st, args)
    except (urllib.error.URLError, urllib.error.HTTPError) as e:
        sys.exit(http_error(e))


if __name__ == "__main__":
    main()
