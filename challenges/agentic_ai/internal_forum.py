"""
internal_forum.py - Internal developer forum for the CTF challenge.

A simple in-memory FastAPI forum with threads and replies.
No auth, no persistence - restarts clean every time.

Run with:
    pip install fastapi uvicorn
    uvicorn internal_forum:app --port 4000
"""

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from datetime import datetime, timedelta
import random

app = FastAPI(title="DevHub Internal Forum")

# ---------------------------------------------------------------------------
# Data models
# ---------------------------------------------------------------------------

class Reply(BaseModel):
    id: int
    author: str
    body: str
    created_at: str
    votes: int = 0
    accepted: bool = False


class Thread(BaseModel):
    id: int
    title: str
    body: str
    author: str
    created_at: str
    tags: list[str]
    votes: int = 0
    views: int = 0
    replies: list[Reply] = []


class NewThread(BaseModel):
    title: str
    body: str
    author: str
    tags: list[str] = []


class NewReply(BaseModel):
    author: str
    body: str

# ---------------------------------------------------------------------------
# Seed data
# ---------------------------------------------------------------------------

def ts(days_ago: int, hours_ago: int = 0) -> str:
    t = datetime.now() - timedelta(days=days_ago, hours=hours_ago)
    return t.strftime("%Y-%m-%d %H:%M")


_threads: list[dict] = [
    {
        "id": 1,
        "title": "Best way to serve static files from our internal Flask/FastAPI apps?",
        "body": (
            "Hey all,\n\n"
            "We have a bunch of small internal tools built in Flask and FastAPI. "
            "Several of them need to serve static assets (CSS, JS, images). "
            "What's the recommended approach for our internal stack? "
            "Should we mount a StaticFiles directory in FastAPI, use a CDN, "
            "or just let nginx handle it upstream?\n\n"
            "Context: these are low-traffic internal dashboards, not public-facing."
        ),
        "author": "priya.nair",
        "created_at": ts(14),
        "tags": ["fastapi", "flask", "static-files", "nginx"],
        "votes": 7,
        "views": 134,
        "replies": [
            {
                "id": 1,
                "author": "tom.bellamy",
                "body": (
                    "For FastAPI it's dead simple:\n\n"
                    "```python\n"
                    "from fastapi.staticfiles import StaticFiles\n"
                    "app.mount('/static', StaticFiles(directory='static'), name='static')\n"
                    "```\n\n"
                    "For anything internal I'd just do this and not bother with nginx unless "
                    "you need SSL termination or load balancing."
                ),
                "created_at": ts(14, 2),
                "votes": 5,
                "accepted": True,
            },
            {
                "id": 2,
                "author": "reza.karimi",
                "body": (
                    "Agree with Tom. One thing worth noting: if you're serving user-uploaded files "
                    "or anything where the path comes from user input, make sure you validate/sanitise "
                    "the path properly before passing it to `FileResponse` or `open()`. "
                    "I've seen people accidentally expose parent directories that way."
                ),
                "created_at": ts(13),
                "votes": 8,
                "accepted": False,
            },
            {
                "id": 3,
                "author": "priya.nair",
                "body": "Thanks both - going with the StaticFiles mount. Reza, good shout on the path validation, will keep that in mind.",
                "created_at": ts(13, 3),
                "votes": 1,
                "accepted": False,
            },
        ],
    },
    {
        "id": 2,
        "title": "Handling CORS properly for our microservices - what are you all doing?",
        "body": (
            "Our frontend team keeps running into CORS issues when calling our internal APIs "
            "from the dashboard SPA. Right now some services just have `allow_origins=['*']` "
            "which I know is bad practice.\n\n"
            "What's the right approach for internal microservices that only need to talk to "
            "our own frontends? Should we enumerate all the origin URLs, use a pattern match, "
            "or is wildcard acceptable for an internal-only network?"
        ),
        "author": "lucas.ferreira",
        "created_at": ts(10),
        "tags": ["cors", "fastapi", "microservices", "security"],
        "votes": 12,
        "views": 210,
        "replies": [
            {
                "id": 1,
                "author": "sarah.okonkwo",
                "body": (
                    "Wildcard is fine if the services are truly internal and not reachable from the internet. "
                    "The CORS risk is cross-origin requests from *other* sites, which doesn't apply if "
                    "there's no external access.\n\n"
                    "That said, if you want to be stricter, just enumerate your internal origins:\n\n"
                    "```python\n"
                    "from fastapi.middleware.cors import CORSMiddleware\n"
                    "app.add_middleware(\n"
                    "    CORSMiddleware,\n"
                    "    allow_origins=['http://dashboard.internal', 'http://localhost:3000'],\n"
                    "    allow_methods=['*'],\n"
                    "    allow_headers=['*'],\n"
                    ")\n"
                    "```"
                ),
                "created_at": ts(10, 1),
                "votes": 9,
                "accepted": True,
            },
            {
                "id": 2,
                "author": "dev.mwangi",
                "body": (
                    "We use an environment variable for the allowed origins list so it's easy to "
                    "configure per environment without touching code. Handy if you have "
                    "staging/dev/prod variants."
                ),
                "created_at": ts(9),
                "votes": 4,
                "accepted": False,
            },
        ],
    },
    {
        "id": 3,
        "title": "Python SSL: certificate verify failed on internal requests",
        "body": (
            "Getting this error when our service calls another internal API:\n\n"
            "```\n"
            "requests.exceptions.SSLError: HTTPSConnectionPool(host='api.internal', port=443): "
            "Max retries exceeded ... caused by SSLCertVerificationError: "
            "certificate verify failed: unable to get local issuer certificate\n"
            "```\n\n"
            "Our internal services use a self-signed cert issued by our own CA. "
            "What's the right fix here? I know `verify=False` exists but that feels wrong."
        ),
        "author": "chen.wei",
        "created_at": ts(8),
        "tags": ["python", "ssl", "requests", "certificates"],
        "votes": 15,
        "views": 389,
        "replies": [
            {
                "id": 1,
                "author": "tom.bellamy",
                "body": (
                    "The proper fix is to point `requests` at your internal CA bundle:\n\n"
                    "```python\n"
                    "import requests\n"
                    "resp = requests.get('https://api.internal/endpoint', verify='/etc/ssl/certs/internal-ca.pem')\n"
                    "```\n\n"
                    "Or set the env var so it applies globally:\n\n"
                    "```bash\n"
                    "export REQUESTS_CA_BUNDLE=/etc/ssl/certs/internal-ca.pem\n"
                    "```\n\n"
                    "Using `verify=False` disables verification entirely which is a bad habit even internally."
                ),
                "created_at": ts(8, 1),
                "votes": 14,
                "accepted": True,
            },
            {
                "id": 2,
                "author": "priya.nair",
                "body": (
                    "If you're using `httpx` instead of `requests`, same idea:\n\n"
                    "```python\n"
                    "import httpx\n"
                    "client = httpx.Client(verify='/etc/ssl/certs/internal-ca.pem')\n"
                    "```\n\n"
                    "You can also add the internal CA to the system trust store once and forget about it."
                ),
                "created_at": ts(7),
                "votes": 6,
                "accepted": False,
            },
        ],
    },
    {
        "id": 4,
        "title": "What's the team's preferred way to structure FastAPI routers for a medium-sized app?",
        "body": (
            "Our main internal API is growing - currently sitting at about 25 endpoints "
            "all jammed into one `main.py`. Time to split it up.\n\n"
            "What structure do you all use? I've seen people go with a flat "
            "`routers/` directory, others do a full domain-driven layout with "
            "`/users/router.py`, `/items/router.py` etc. Curious what's working "
            "for teams at our scale."
        ),
        "author": "amara.diallo",
        "created_at": ts(6),
        "tags": ["fastapi", "architecture", "project-structure"],
        "votes": 9,
        "views": 175,
        "replies": [
            {
                "id": 1,
                "author": "reza.karimi",
                "body": (
                    "I like the domain-driven layout:\n\n"
                    "```\n"
                    "app/\n"
                    "  main.py\n"
                    "  routers/\n"
                    "    users.py\n"
                    "    reports.py\n"
                    "    admin.py\n"
                    "  models/\n"
                    "  services/\n"
                    "```\n\n"
                    "Each router file gets an `APIRouter` instance and then in `main.py` you just:\n\n"
                    "```python\n"
                    "from app.routers import users, reports\n"
                    "app.include_router(users.router, prefix='/users')\n"
                    "app.include_router(reports.router, prefix='/reports')\n"
                    "```\n\n"
                    "Keeps things tidy and easy to test in isolation."
                ),
                "created_at": ts(6, 2),
                "votes": 7,
                "accepted": True,
            },
            {
                "id": 2,
                "author": "sarah.okonkwo",
                "body": "We do basically this but also add a `dependencies.py` at root level for shared auth/DB dependencies. Stops you duplicating the same `Depends(...)` everywhere.",
                "created_at": ts(5),
                "votes": 5,
                "accepted": False,
            },
            {
                "id": 3,
                "author": "amara.diallo",
                "body": "Excellent, this is pretty much what I had in mind. Going ahead with this layout, cheers.",
                "created_at": ts(5, 6),
                "votes": 1,
                "accepted": False,
            },
        ],
    },
    {
        "id": 5,
        "title": "Slow startup on our FastAPI app - taking ~8s to boot",
        "body": (
            "Our main service is taking about 8 seconds to start up, which is painful "
            "for local dev and also slows down our CI container spin-up time.\n\n"
            "We do have some DB connection pooling setup on startup and load a "
            "few ML model files. Is there anything obvious I might be missing? "
            "Any profiling tools you'd recommend for startup time?"
        ),
        "author": "dev.mwangi",
        "created_at": ts(4),
        "tags": ["fastapi", "performance", "startup", "profiling"],
        "votes": 6,
        "views": 98,
        "replies": [
            {
                "id": 1,
                "author": "lucas.ferreira",
                "body": (
                    "ML model loading is almost certainly your culprit if the models are large. "
                    "A few options:\n\n"
                    "1. Lazy-load the model on first request rather than at startup\n"
                    "2. Use a startup lifespan event so at least the timing is explicit and profiled\n"
                    "3. Cache the model in a shared memory segment if you have multiple workers\n\n"
                    "For profiling startup specifically, just add `time.perf_counter()` calls around "
                    "each startup step - crude but effective."
                ),
                "created_at": ts(4, 1),
                "votes": 5,
                "accepted": False,
            },
            {
                "id": 2,
                "author": "chen.wei",
                "body": (
                    "Also worth checking whether you're importing heavy libraries at module level "
                    "that could be deferred. `import torch` or `import tensorflow` at the top of "
                    "every file adds up even if you're not using them on every code path."
                ),
                "created_at": ts(3),
                "votes": 4,
                "accepted": False,
            },
        ],
    },
    {
        "id": 6,
        "title": "Convention for TODO comments in server code - how do you all format them?",
        "body": (
            "Trivial question but wanted to get team consensus: what format do we use "
            "for TODO comments in the internal services? I've seen `# TODO:`, `# TODO(name):`, "
            "# FIXME:`, etc. floating around.\n\n"
            "Also - do we track these anywhere or just leave them in the code?"
        ),
        "author": "priya.nair",
        "created_at": ts(3),
        "tags": ["conventions", "code-style"],
        "votes": 3,
        "views": 61,
        "replies": [
            {
                "id": 1,
                "author": "tom.bellamy",
                "body": (
                    "We settled on `# TODO(username): description` in most of our repos. "
                    "Makes it easy to grep for your own TODOs and also shows who to ask "
                    "if the original author has moved on.\n\n"
                    "We don't formally track them - if it's important enough it should be a ticket."
                ),
                "created_at": ts(3, 1),
                "votes": 4,
                "accepted": True,
            },
            {
                "id": 2,
                "author": "amara.diallo",
                "body": "Agreed. We also lint for `# FIXME` in CI and fail the build - forces people to either fix it or convert it to a proper TODO with a ticket number.",
                "created_at": ts(2),
                "votes": 3,
                "accepted": False,
            },
        ],
    },
]

# Internal counter for new IDs
_next_thread_id = max(t["id"] for t in _threads) + 1
_next_reply_ids = {t["id"]: (max((r["id"] for r in t["replies"]), default=0) + 1) for t in _threads}


def _get_thread(thread_id: int) -> dict:
    for t in _threads:
        if t["id"] == thread_id:
            return t
    raise HTTPException(status_code=404, detail="Thread not found")

# ---------------------------------------------------------------------------
# HTML helpers
# ---------------------------------------------------------------------------

CSS = """
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&family=IBM+Plex+Sans:wght@400;500;600&display=swap');

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

:root {
  --bg:        #0f1117;
  --surface:   #181c27;
  --border:    #2a2f3f;
  --accent:    #4f8ef7;
  --accent2:   #3ecf8e;
  --muted:     #8892a4;
  --text:      #e2e8f0;
  --tag-bg:    #1e2535;
  --tag-text:  #7ba4f4;
  --code-bg:   #131720;
  --accepted:  #1a3a2a;
  --accepted-border: #3ecf8e;
  --vote-up:   #4f8ef7;
  --danger:    #f87171;
}

body {
  font-family: 'IBM Plex Sans', sans-serif;
  background: var(--bg);
  color: var(--text);
  font-size: 14px;
  line-height: 1.6;
}

a { color: var(--accent); text-decoration: none; }
a:hover { text-decoration: underline; }

.topbar {
  background: var(--surface);
  border-bottom: 1px solid var(--border);
  padding: 0 24px;
  height: 52px;
  display: flex;
  align-items: center;
  gap: 24px;
  position: sticky;
  top: 0;
  z-index: 100;
}
.topbar-brand {
  font-family: 'IBM Plex Mono', monospace;
  font-size: 15px;
  font-weight: 600;
  color: var(--accent2);
  letter-spacing: -0.5px;
}
.topbar-brand span { color: var(--accent); }
.topbar-nav { display: flex; gap: 16px; margin-left: auto; }
.topbar-nav a { color: var(--muted); font-size: 13px; }
.topbar-nav a:hover { color: var(--text); text-decoration: none; }

.layout { display: flex; max-width: 1100px; margin: 0 auto; padding: 24px 16px; gap: 24px; }

.sidebar {
  width: 200px;
  flex-shrink: 0;
}
.sidebar-section { margin-bottom: 24px; }
.sidebar-title {
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 1px;
  color: var(--muted);
  margin-bottom: 8px;
}
.sidebar-link {
  display: block;
  padding: 5px 10px;
  border-radius: 4px;
  color: var(--muted);
  font-size: 13px;
  margin-bottom: 2px;
}
.sidebar-link:hover, .sidebar-link.active {
  background: var(--tag-bg);
  color: var(--text);
  text-decoration: none;
}

.main { flex: 1; min-width: 0; }

.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20px;
  padding-bottom: 16px;
  border-bottom: 1px solid var(--border);
}
.page-title { font-size: 20px; font-weight: 600; }
.page-meta { font-size: 12px; color: var(--muted); }

.btn {
  display: inline-block;
  padding: 7px 16px;
  border-radius: 5px;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  border: none;
  font-family: inherit;
  transition: opacity 0.15s;
}
.btn:hover { opacity: 0.85; text-decoration: none; }
.btn-primary { background: var(--accent); color: #fff; }
.btn-secondary { background: var(--tag-bg); color: var(--text); border: 1px solid var(--border); }

/* Thread list */
.thread-list { display: flex; flex-direction: column; gap: 1px; }
.thread-card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 6px;
  padding: 14px 16px;
  display: flex;
  gap: 16px;
  margin-bottom: 6px;
  transition: border-color 0.15s;
}
.thread-card:hover { border-color: #3a3f52; }
.thread-stats {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  min-width: 60px;
  padding-top: 2px;
}
.stat-box {
  text-align: center;
  background: var(--tag-bg);
  border: 1px solid var(--border);
  border-radius: 4px;
  padding: 3px 8px;
  min-width: 52px;
}
.stat-box.answered { background: var(--accepted); border-color: var(--accepted-border); }
.stat-num { font-size: 14px; font-weight: 600; display: block; font-family: 'IBM Plex Mono', monospace; }
.stat-label { font-size: 10px; color: var(--muted); text-transform: uppercase; letter-spacing: 0.5px; }
.thread-body { flex: 1; min-width: 0; }
.thread-title { font-size: 15px; font-weight: 500; margin-bottom: 6px; line-height: 1.4; }
.thread-excerpt { color: var(--muted); font-size: 13px; margin-bottom: 8px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.thread-footer { display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }
.tag {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 3px;
  background: var(--tag-bg);
  color: var(--tag-text);
  font-size: 11px;
  font-family: 'IBM Plex Mono', monospace;
  border: 1px solid #2a3450;
}
.thread-author-info { margin-left: auto; font-size: 11px; color: var(--muted); white-space: nowrap; }
.thread-author-info strong { color: var(--accent); }

/* Thread detail */
.question-block, .reply-block {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 6px;
  padding: 20px;
  margin-bottom: 12px;
  display: flex;
  gap: 16px;
}
.reply-block.accepted {
  border-color: var(--accepted-border);
  background: var(--accepted);
}
.vote-col { display: flex; flex-direction: column; align-items: center; gap: 4px; min-width: 32px; }
.vote-count { font-family: 'IBM Plex Mono', monospace; font-size: 18px; font-weight: 600; color: var(--muted); }
.vote-arrow { font-size: 18px; color: var(--border); cursor: pointer; user-select: none; }
.vote-arrow:hover { color: var(--vote-up); }
.post-col { flex: 1; min-width: 0; }
.post-body { color: var(--text); line-height: 1.7; }
.post-body pre {
  background: var(--code-bg);
  border: 1px solid var(--border);
  border-radius: 5px;
  padding: 12px;
  overflow-x: auto;
  margin: 12px 0;
}
.post-body code {
  font-family: 'IBM Plex Mono', monospace;
  font-size: 12.5px;
  background: var(--code-bg);
  padding: 1px 5px;
  border-radius: 3px;
}
.post-body pre code { background: none; padding: 0; }
.post-footer { display: flex; align-items: center; gap: 8px; margin-top: 16px; padding-top: 12px; border-top: 1px solid var(--border); }
.post-author { margin-left: auto; font-size: 12px; color: var(--muted); }
.post-author strong { color: var(--accent2); }
.accepted-badge {
  display: inline-flex; align-items: center; gap: 4px;
  background: var(--accepted); border: 1px solid var(--accepted-border);
  color: var(--accent2); font-size: 11px; padding: 2px 8px; border-radius: 3px;
  font-weight: 600;
}

.section-label {
  font-size: 13px; font-weight: 600; color: var(--muted);
  text-transform: uppercase; letter-spacing: 0.5px;
  margin: 24px 0 12px;
}

/* Forms */
.form-card { background: var(--surface); border: 1px solid var(--border); border-radius: 6px; padding: 20px; margin-top: 16px; }
.form-title { font-size: 16px; font-weight: 600; margin-bottom: 16px; }
.form-group { margin-bottom: 14px; }
.form-label { display: block; font-size: 12px; font-weight: 500; color: var(--muted); text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 6px; }
.form-input, .form-textarea {
  width: 100%;
  background: var(--bg);
  border: 1px solid var(--border);
  border-radius: 4px;
  padding: 8px 12px;
  color: var(--text);
  font-family: inherit;
  font-size: 13px;
  outline: none;
  transition: border-color 0.15s;
}
.form-input:focus, .form-textarea:focus { border-color: var(--accent); }
.form-textarea { resize: vertical; min-height: 100px; line-height: 1.6; }

/* Breadcrumb */
.breadcrumb { font-size: 12px; color: var(--muted); margin-bottom: 16px; }
.breadcrumb a { color: var(--muted); }
.breadcrumb a:hover { color: var(--text); }
.breadcrumb span { margin: 0 6px; }

/* Thread detail header */
.thread-detail-title { font-size: 22px; font-weight: 600; line-height: 1.35; margin-bottom: 8px; }
.thread-detail-meta { font-size: 12px; color: var(--muted); margin-bottom: 14px; display: flex; gap: 16px; flex-wrap: wrap; }
.thread-detail-meta .meta-item strong { color: var(--text); }

hr.divider { border: none; border-top: 1px solid var(--border); margin: 20px 0; }

.empty { color: var(--muted); font-size: 13px; padding: 12px 0; }
"""

def _render_body(text: str) -> str:
    """Minimal markdown-ish renderer: code blocks and inline code only."""
    import html as html_mod
    import re

    # Escape HTML in the full text first
    text = html_mod.escape(text)

    # Fenced code blocks
    def replace_code_block(m):
        lang = m.group(1) or ""
        code = m.group(2)
        return f'<pre><code class="language-{html_mod.escape(lang)}">{code}</code></pre>'

    text = re.sub(r'```(\w*)\n(.*?)```', replace_code_block, text, flags=re.DOTALL)

    # Inline code
    text = re.sub(r'`([^`]+)`', r'<code>\1</code>', text)

    # Paragraphs
    paragraphs = re.split(r'\n{2,}', text)
    result = []
    for p in paragraphs:
        p = p.strip()
        if p.startswith('<pre>'):
            result.append(p)
        elif p:
            p = p.replace('\n', '<br>')
            result.append(f'<p style="margin-bottom:10px">{p}</p>')
    return '\n'.join(result)


def _page(title: str, body: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title} — DevHub</title>
  <style>{CSS}</style>
</head>
<body>
  <div class="topbar">
    <div class="topbar-brand">dev<span>hub</span> <span style="color:var(--muted);font-weight:400;font-size:12px">// internal</span></div>
    <nav class="topbar-nav">
      <a href="/">Questions</a>
      <a href="/threads/new">Ask</a>
    </nav>
  </div>
  <div class="layout">
    <aside class="sidebar">
      <div class="sidebar-section">
        <div class="sidebar-title">Browse</div>
        <a class="sidebar-link active" href="/">All Questions</a>
      </div>
      <div class="sidebar-section">
        <div class="sidebar-title">Tags</div>
        <a class="sidebar-link" href="/?tag=fastapi">fastapi</a>
        <a class="sidebar-link" href="/?tag=python">python</a>
        <a class="sidebar-link" href="/?tag=security">security</a>
        <a class="sidebar-link" href="/?tag=ssl">ssl</a>
        <a class="sidebar-link" href="/?tag=nginx">nginx</a>
      </div>
    </aside>
    <main class="main">
      {body}
    </main>
  </div>
</body>
</html>"""

# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.get("/", response_class=HTMLResponse)
def list_threads(tag: str | None = None):
    threads = _threads
    if tag:
        threads = [t for t in threads if tag in t["tags"]]

    cards = []
    for t in sorted(threads, key=lambda x: x["id"], reverse=True):
        excerpt = t["body"][:120].replace("\n", " ") + "…"
        tags_html = " ".join(f'<span class="tag">{tg}</span>' for tg in t["tags"])
        answer_count = len(t["replies"])
        has_accepted = any(r["accepted"] for r in t["replies"])
        answered_class = "answered" if has_accepted else ""
        cards.append(f"""
        <div class="thread-card">
          <div class="thread-stats">
            <div class="stat-box">
              <span class="stat-num">{t['votes']}</span>
              <span class="stat-label">votes</span>
            </div>
            <div class="stat-box {answered_class}">
              <span class="stat-num">{answer_count}</span>
              <span class="stat-label">answers</span>
            </div>
            <div class="stat-box">
              <span class="stat-num">{t['views']}</span>
              <span class="stat-label">views</span>
            </div>
          </div>
          <div class="thread-body">
            <div class="thread-title"><a href="/threads/{t['id']}">{t['title']}</a></div>
            <div class="thread-excerpt">{excerpt}</div>
            <div class="thread-footer">
              {tags_html}
              <div class="thread-author-info">asked {t['created_at']} by <strong>{t['author']}</strong></div>
            </div>
          </div>
        </div>""")

    tag_badge = f' <span class="tag" style="font-size:13px">#{tag}</span>' if tag else ""
    body = f"""
    <div class="page-header">
      <div>
        <div class="page-title">All Questions{tag_badge}</div>
        <div class="page-meta">{len(threads)} question{'s' if len(threads) != 1 else ''}</div>
      </div>
      <a class="btn btn-primary" href="/threads/new">Ask a Question</a>
    </div>
    <div class="thread-list">{''.join(cards) if cards else '<div class="empty">No threads found.</div>'}</div>
    """
    return _page("Questions", body)


@app.get("/threads/new", response_class=HTMLResponse)
def new_thread_form():
    body = """
    <div class="breadcrumb"><a href="/">Questions</a> <span>›</span> New Question</div>
    <div class="form-card">
      <div class="form-title">Ask a Question</div>
      <form method="post" action="/threads">
        <div class="form-group">
          <label class="form-label" for="title">Title</label>
          <input class="form-input" id="title" name="title" type="text" placeholder="What's your question? Be specific." required>
        </div>
        <div class="form-group">
          <label class="form-label" for="body">Body</label>
          <textarea class="form-textarea" id="body" name="body" style="min-height:180px" placeholder="Describe your problem in detail. Supports inline `code` and ```code blocks```." required></textarea>
        </div>
        <div class="form-group">
          <label class="form-label" for="author">Your Username</label>
          <input class="form-input" id="author" name="author" type="text" placeholder="e.g. your.name" required>
        </div>
        <div class="form-group">
          <label class="form-label" for="tags">Tags (comma-separated)</label>
          <input class="form-input" id="tags" name="tags" type="text" placeholder="e.g. fastapi, python, ssl">
        </div>
        <button class="btn btn-primary" type="submit">Post Question</button>
      </form>
    </div>
    """
    return _page("Ask a Question", body)


@app.post("/threads", response_class=HTMLResponse)
async def create_thread_form(request: Request):
    global _next_thread_id
    form = await request.form()
    title = (form.get("title") or "").strip()
    body_text = (form.get("body") or "").strip()
    author = (form.get("author") or "anonymous").strip()
    tags_raw = (form.get("tags") or "").strip()
    tags = [t.strip() for t in tags_raw.split(",") if t.strip()]

    if not title or not body_text:
        raise HTTPException(status_code=400, detail="Title and body are required")

    thread = {
        "id": _next_thread_id,
        "title": title,
        "body": body_text,
        "author": author,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "tags": tags,
        "votes": 0,
        "views": random.randint(1, 5),
        "replies": [],
    }
    _threads.append(thread)
    _next_reply_ids[_next_thread_id] = 1
    _next_thread_id += 1

    from fastapi.responses import RedirectResponse
    return RedirectResponse(url=f"/threads/{thread['id']}", status_code=303)


@app.get("/threads/{thread_id}", response_class=HTMLResponse)
def view_thread(thread_id: int):
    t = _get_thread(thread_id)
    t["views"] += 1

    tags_html = " ".join(f'<span class="tag">{tg}</span>' for tg in t["tags"])

    question_html = f"""
    <div class="question-block">
      <div class="vote-col">
        <span class="vote-arrow">▲</span>
        <span class="vote-count">{t['votes']}</span>
        <span class="vote-arrow">▼</span>
      </div>
      <div class="post-col">
        <div class="post-body">{_render_body(t['body'])}</div>
        <div class="post-footer">
          {tags_html}
          <div class="post-author">asked {t['created_at']} by <strong>{t['author']}</strong></div>
        </div>
      </div>
    </div>
    """

    replies_html = []
    for r in t["replies"]:
        accepted_badge = '<span class="accepted-badge">✓ Accepted</span>' if r["accepted"] else ""
        accepted_class = "accepted" if r["accepted"] else ""
        replies_html.append(f"""
        <div class="reply-block {accepted_class}">
          <div class="vote-col">
            <span class="vote-arrow">▲</span>
            <span class="vote-count">{r['votes']}</span>
            <span class="vote-arrow">▼</span>
          </div>
          <div class="post-col">
            <div class="post-body">{_render_body(r['body'])}</div>
            <div class="post-footer">
              {accepted_badge}
              <div class="post-author">answered {r['created_at']} by <strong>{r['author']}</strong></div>
            </div>
          </div>
        </div>""")

    reply_count = len(t["replies"])
    replies_section = f"""
    <div class="section-label">{reply_count} Answer{'s' if reply_count != 1 else ''}</div>
    {''.join(replies_html) if replies_html else '<div class="empty">No answers yet — be the first!</div>'}
    """

    add_reply_form = f"""
    <hr class="divider">
    <div class="form-card">
      <div class="form-title">Your Answer</div>
      <form method="post" action="/threads/{t['id']}/replies">
        <div class="form-group">
          <label class="form-label" for="body">Answer</label>
          <textarea class="form-textarea" id="body" name="body" style="min-height:160px" placeholder="Write your answer here. Supports `inline code` and ```code blocks```." required></textarea>
        </div>
        <div class="form-group">
          <label class="form-label" for="author">Your Username</label>
          <input class="form-input" id="author" name="author" type="text" placeholder="e.g. your.name" required>
        </div>
        <button class="btn btn-primary" type="submit">Post Answer</button>
      </form>
    </div>
    """

    body = f"""
    <div class="breadcrumb"><a href="/">Questions</a> <span>›</span> Thread #{t['id']}</div>
    <div class="thread-detail-title">{t['title']}</div>
    <div class="thread-detail-meta">
      <span class="meta-item">Asked <strong>{t['created_at']}</strong></span>
      <span class="meta-item">Views <strong>{t['views']}</strong></span>
      <span class="meta-item">Votes <strong>{t['votes']}</strong></span>
    </div>
    {question_html}
    {replies_section}
    {add_reply_form}
    """
    return _page(t["title"], body)


@app.post("/threads/{thread_id}/replies", response_class=HTMLResponse)
async def add_reply_form(thread_id: int, request: Request):
    t = _get_thread(thread_id)
    form = await request.form()
    body_text = (form.get("body") or "").strip()
    author = (form.get("author") or "anonymous").strip()

    if not body_text:
        raise HTTPException(status_code=400, detail="Reply body required")

    reply_id = _next_reply_ids.get(thread_id, 1)
    reply = {
        "id": reply_id,
        "author": author,
        "body": body_text,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "votes": 0,
        "accepted": False,
    }
    t["replies"].append(reply)
    _next_reply_ids[thread_id] = reply_id + 1

    from fastapi.responses import RedirectResponse
    return RedirectResponse(url=f"/threads/{thread_id}", status_code=303)


# ---------------------------------------------------------------------------
# JSON API (used by bot.py for RAG ingestion)
# ---------------------------------------------------------------------------

@app.get("/api/threads")
def api_list_threads():
    return _threads


@app.get("/api/threads/{thread_id}")
def api_get_thread(thread_id: int):
    return _get_thread(thread_id)


@app.post("/api/threads")
def api_create_thread(payload: NewThread):
    global _next_thread_id
    thread = {
        "id": _next_thread_id,
        **payload.model_dump(),
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "votes": 0,
        "views": 0,
        "replies": [],
    }
    _threads.append(thread)
    _next_reply_ids[_next_thread_id] = 1
    _next_thread_id += 1
    return thread


@app.post("/api/threads/{thread_id}/replies")
def api_add_reply(thread_id: int, payload: NewReply):
    t = _get_thread(thread_id)
    reply_id = _next_reply_ids.get(thread_id, 1)
    reply = {
        "id": reply_id,
        **payload.model_dump(),
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "votes": 0,
        "accepted": False,
    }
    t["replies"].append(reply)
    _next_reply_ids[thread_id] = reply_id + 1
    return reply
