#!/usr/bin/env python3
"""access_ladder — 막힌 출처를 한 칸씩 올라가며 다시 읽어보는 fetcher.

코어(cite_check)의 fetcher 인터페이스를 그대로 구현한다: (url, timeout) -> (status, ctype, body).
어느 칸에서 뚫렸는지, 못 뚫었으면 왜인지는 `.trace[url]` 에 남는다.

  0 직접 fetch → 1 공개 API → 2 추출기·아카이브 → 3 TLS 위장 → 4 헤드리스 → 5 로그인 세션(옵트인) → 6 사람

경계 (협상 불가): 이 모듈은 비밀번호·키체인·자격증명 저장소를 읽지 않고, 로그인 폼을 채우지 않는다.
로그인 벽은 ① 사용자가 이미 로그인한 브라우저 세션 재사용(읽기 전용, 호스트별 옵트인)
② 사람에게 넘김 ③ 사용자가 발급한 API 키 — 셋 중 하나로만 처리한다.
CAPTCHA 는 풀지 않고, robots.txt Disallow 는 칸 3·4·5 로 우회하지 않는다.

  python3 scripts/access_ladder.py <url>      # 사다리를 한 번 타고 경로를 보여준다
"""
import json
import os
import re
import shutil
import subprocess
import sys
import time
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cite_check import UA, alive, extract, has_source_text, publisher  # noqa: E402

# ── 사유 코드 ────────────────────────────────────────────────────────────────
# 기획(17 §4)의 8종 + dead. 죽은 링크는 인용 부패의 가장 흔한 형태인데 8종에 자리가
# 없었다. bot-wall 로 뭉개면 "사이트가 막았다"는 거짓말이 되므로 코드를 하나 늘렸다.
REASONS = ("bot-wall", "captcha", "login", "paywall", "robots", "pdf", "dynamic", "budget", "dead")

_MARK = (
    ("captcha", re.compile(r"(?i)recaptcha|hcaptcha|turnstile|g-recaptcha|\bcaptcha\b|are you a (robot|human)")),
    ("login", re.compile(r"""(?i)type=["']password["']|\bsign in\b|\blog ?in\b|institutional (sign|log)|"""
                         r"""\bauthentication required\b|\b로그인\b""")),
    ("paywall", re.compile(r"(?i)subscribe to (read|continue)|subscription (is )?required|paywall|"
                           r"purchase (access|this article)|already a subscriber|\b구독\b")),
    ("bot-wall", re.compile(r"(?i)enable javascript|cookies? (are |must be )?(required|enabled)|access denied|"
                            r"unusual traffic|cloudflare|checking your browser|bot detection|"
                            r"cf-chl|challenge-platform|잠시만 기다리십시오")),
)
# 완전 방어는 불가능하다(15 §6). 목표는 차단이 아니라 표시 — 리더가 이 출처를 요약할 때 알게 한다.
_INJECT = re.compile(r"(?i)ignore (all |any )?(the )?(previous|prior|above|earlier) (instruction|prompt|direction)"
                     r"|disregard (all |any )?(the )?(previous|prior|above)"
                     r"|new instructions\s*:"
                     r"|system prompt\b"
                     r"|<\s*\|?\s*im_start")

ALLOW_SESSION_PATH = os.environ.get(
    "VERIFY_ALLOW_SESSION", os.path.expanduser("~/.config/verify/allow-session.json"))


def classify(status, ctype, body):
    """읽지 못한 응답의 사유 코드. 본문 표식 → 상태 코드 순으로 본다."""
    ctype, body = (ctype or ""), (body or "")
    if alive(status) and "pdf" in ctype.lower():
        return "pdf"
    if status is None or status in (404, 410):
        return "dead"
    head = body[:200000]
    for reason, pat in _MARK:
        if pat.search(head):
            return reason
    if status == 203:
        return "bot-wall"
    if status in (401, 402, 403, 429):
        return "paywall" if status == 402 else "bot-wall"
    if alive(status):
        # 200인데 문장이 없다 = JS로 그리는 껍데기
        return "dynamic"
    return "bot-wall"


def options(reason, host):
    """항상 '사용자가 하는 일'만 적는다. 에이전트가 몰래 더 뚫는 선택지는 없다."""
    save = ("브라우저에서 직접 열어 본문을 저장해 주시면 그 파일로 대조합니다")
    session = f"`{host}` 를 세션 재사용 허용 목록에 넣으면 이미 로그인된 브라우저로 읽습니다 (읽기 전용)"
    return {
        "login": [session, save, "이 사이트에 API가 있으면 키를 발급해 어댑터로 붙일 수 있습니다"],
        "paywall": [session + " — 구독 계정이 있는 경우", "프리프린트·PMC 등 공개 사본을 대신 인용하세요", save],
        "captcha": ["브라우저에서 직접 CAPTCHA 를 통과한 뒤 세션 재사용을 허용해 주세요 (에이전트는 풀지 않습니다)", save],
        "bot-wall": ["`curl_cffi` 를 설치하면 TLS 위장(칸 3)을 시도합니다: `pip install curl_cffi`", save, session],
        "dynamic": ["`playwright` 를 설치하면 헤드리스 렌더링(칸 4)을 시도합니다: `pip install playwright && playwright install chromium`", save],
        "robots": [f"`{host}` 의 robots.txt 가 수집을 금지합니다 — 우회하지 않습니다. 공개 API 나 대체 출처를 쓰세요", save],
        "dead": ["링크가 죽었습니다. 아카이브 사본(web.archive.org)을 인용하거나 원문을 다시 찾아 주세요", save],
        "pdf": ["PDF 본문 추출은 v1 미지원입니다. 본문 텍스트를 저장해 주시면 대조합니다"],
        "budget": ["이 URL 에서 시간 예산을 다 썼습니다. `--budget` 을 늘리거나 다시 시도해 주세요", save],
    }.get(reason, [save])


def _readable(status, ctype, body):
    """대조에 쓸 수 있는 진짜 본문인가 — 코어와 같은 기준을 쓴다."""
    if not alive(status) or "pdf" in (ctype or "").lower():
        return False
    text, _ = extract(body or "")
    return has_source_text(status, text)


def _get(url, timeout, ua=UA, headers=None):
    req = Request(url, headers={"User-Agent": ua, "Accept": "text/html,*/*", **(headers or {})})
    try:
        with urlopen(req, timeout=timeout) as r:
            body = r.read().decode(r.headers.get_content_charset() or "utf-8", "replace")
            return r.status, r.headers.get("Content-Type", ""), body
    except HTTPError as e:
        try:
            return e.code, e.headers.get("Content-Type", "") if e.headers else "", e.read().decode("utf-8", "replace")
        except Exception:
            return e.code, "", ""
    except (URLError, TimeoutError, ValueError, OSError):
        return None, "", ""


# ── 칸 1: 공개 API 어댑터 ────────────────────────────────────────────────────
# ponytail: 지금은 PubMed 하나. #5(어댑터 레지스트리)가 Crossref·OpenAlex 로 넓히면서 이걸 흡수한다.
def _pubmed(url, timeout):
    m = re.search(r"pubmed\.ncbi\.nlm\.nih\.gov/(\d+)", url) or re.search(r"[?&]term=(\d+)", url)
    if not m:
        return None
    api = ("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
           f"?db=pubmed&id={m.group(1)}&rettype=abstract&retmode=text")
    return _get(api, timeout)


ADAPTERS = {"pubmed.ncbi.nlm.nih.gov": _pubmed, "www.ncbi.nlm.nih.gov": _pubmed}


class AccessLadder:
    """cite_check 에 주입하는 fetcher. 호출부는 (status, ctype, body) 만 본다."""

    def __init__(self, *, tls=True, extractor=True, session=True, budget=30.0,
                 allow_session=None, consent=None, clock=time.monotonic, rungs=None, robots=None):
        self.tls, self.extractor, self.session_enabled = tls, extractor, session
        self.budget, self.clock, self.trace = budget, clock, {}
        self.consent = consent                      # (host) -> bool. 없으면 묻지 않고 거절로 본다.
        self._allow = allow_session if allow_session is not None else _load_allow()
        self._rungs = rungs or [(0, self._direct), (1, self._adapter), (2, self._extractor),
                                (3, self._impersonate), (4, self._headless), (5, self._browser_session)]
        self._robots_check = robots if robots is not None else self._robots_ok
        self._robots_cache = {}

    # ── 사다리 ───────────────────────────────────────────────────────────
    def __call__(self, url, timeout=10):
        t0, last = self.clock(), (None, "", "")
        tr = {"via": None, "attempts": [], "reason": None, "options": [],
              "injection_suspect": False, "archive": False, "tls": False}
        self.trace[url] = tr
        for n, fn in self._rungs:
            if self.clock() - t0 > self.budget:
                return self._stop(url, tr, "budget", last)
            if n >= 3 and not self._robots_check(url, timeout):
                tr["attempts"].append(f"{n}:robots-disallow")
                return self._stop(url, tr, "robots", last)
            if n == 5 and not self._session_ok(url, tr):
                continue
            try:
                got = fn(url, timeout, tr)
            except Exception as e:                      # 한 칸이 터져도 사다리는 계속 오른다
                tr["attempts"].append(f"{n}:error {type(e).__name__}")
                continue
            if got is None:
                continue
            status, ctype, body = got
            if _readable(status, ctype, body):
                tr["attempts"].append(f"{n}:ok")
                tr["via"] = n
                tr["injection_suspect"] = bool(_INJECT.search(body or ""))
                return got
            last = got
            tr["attempts"].append(f"{n}:{status if status is not None else 'net-error'}")
            reason = classify(status, ctype, body)
            # PDF 는 어느 칸에서도 v1이 못 읽는다. CAPTCHA 는 풀지 않지만(성역), 아래 칸에서 봤다고
            # 멈추면 정작 사람 없이 통과되는 칸(3·4·5)을 못 간다 — 진짜 브라우저가 보고 나서야 끝이다.
            if reason == "pdf" or (reason == "captcha" and n >= 4):
                return self._stop(url, tr, reason, got)
        return self._stop(url, tr, classify(*last), last)

    def _stop(self, url, tr, reason, last):
        """칸 6 — 사람에게 넘긴다."""
        tr["reason"] = reason
        tr["options"] = options(reason, publisher(url))
        return last

    # ── 각 칸 ────────────────────────────────────────────────────────────
    def _direct(self, url, timeout, tr):
        return _get(url, timeout)

    def _adapter(self, url, timeout, tr):
        fn = ADAPTERS.get(urlparse(url).netloc.lower())
        if not fn:
            tr["attempts"].append("1:어댑터 없음")
            return None
        return fn(url, timeout)

    def _extractor(self, url, timeout, tr):
        if not self.extractor:
            tr["attempts"].append("2:꺼짐")
            return None
        key = os.environ.get("JINA_API_KEY")
        if key:
            got = _get("https://r.jina.ai/" + url, timeout, headers={"Authorization": f"Bearer {key}"})
            if _readable(*got):
                return got
            tr["attempts"].append(f"2:jina {got[0]}")
        else:
            tr["attempts"].append("2:jina 키 없음(익명 차단)")
        got = _get("https://web.archive.org/web/2/" + url, timeout)  # 죽은 링크의 유일한 답
        if _readable(*got):
            tr["archive"] = True
            return got
        tr["attempts"].append(f"2:archive {got[0]}")
        return None

    def _impersonate(self, url, timeout, tr):
        if not self.tls:
            tr["attempts"].append("3:꺼짐")
            return None
        try:
            from curl_cffi import requests as cffi     # ponytail: 선택 의존성, 없으면 그냥 건너뛴다
        except ImportError:
            tr["attempts"].append("3:건너뜀(curl_cffi 미설치)")
            return None
        r = cffi.get(url, impersonate="chrome", timeout=timeout)
        tr["tls"] = True
        return r.status_code, r.headers.get("Content-Type", ""), r.text

    def _headless(self, url, timeout, tr):
        try:
            from playwright.sync_api import sync_playwright
        except ImportError:
            tr["attempts"].append("4:건너뜀(playwright 미설치)")
            return None
        with sync_playwright() as p:                    # 비로그인 렌더링만 — 사용자 프로필을 쓰지 않는다
            b = p.chromium.launch()
            try:
                pg = b.new_page()
                pg.goto(url, timeout=timeout * 1000)
                return 200, "text/html", pg.content()
            finally:
                b.close()

    def _browser_session(self, url, timeout, tr):
        """칸 5 — 사용자가 이미 로그인한 브라우저로 '읽기만' 한다.

        여는 것·읽는 것 외에는 아무것도 하지 않는다. aside 는 자격증명 접근(applePasswords)과
        CAPTCHA 처리 기능도 노출하지만 이 모듈은 그 둘을 호출하지 않는다 (성역 — 테스트로 고정).
        """
        exe = shutil.which("aside")
        if not exe:
            tr["attempts"].append("5:건너뜀(aside 미설치)")
            return None
        # 사람이 하는 것과 같은 순서: 탭에서 열고, 화면이 자리잡을 때까지 잠깐 기다리고, 읽는다.
        # 상태 코드를 200으로 박아두면 403 챌린지 페이지가 200짜리 본문으로 둔갑한다(NEJM 실측).
        # 아직도 대기 화면이면 그때만 브라우저 fetch 로 진짜 상태를 물어본다.
        # 기다리는 것은 로딩을 기다리는 것이지 CAPTCHA 를 푸는 것이 아니다 — 그건 하지 않는다.
        js = ("const W = /cf-chl|challenge-platform|__cf_chl|checking your browser|잠시만 기다리십시오/i;\n"
              "const t = await openTab(%(u)s);\n"
              "let h = await page.content();\n"
              "for (let i = 0; i < 3 && W.test(h); i++) { await sleep(2000); h = await page.content(); }\n"
              "let s = 200;\n"
              "if (W.test(h)) { try { s = (await fetch(%(u)s)).status; } catch (e) { s = 403; } }\n"
              "console.log(JSON.stringify({s: s, h: h}));\n"
              "await closeTab(t);" % {"u": json.dumps(url)})
        p = subprocess.run([exe, "repl", js], capture_output=True, text=True, timeout=max(timeout, 90))
        for line in p.stdout.splitlines():
            if line.startswith('{"s"'):
                d = json.loads(line)
                return d["s"], "text/html", d["h"]
        tr["attempts"].append("5:aside 응답 없음")
        return None

    # ── 게이트 ───────────────────────────────────────────────────────────
    def _session_ok(self, url, tr):
        host = publisher(url)
        if not self.session_enabled:
            tr["attempts"].append("5:꺼짐")
            return False
        if self._allow.get(host) is True:
            return True
        if self.consent and self.consent(host):         # 물어보고 기억한다 (마찰 1회)
            self._allow[host] = True
            _save_allow(self._allow)
            return True
        tr["attempts"].append("5:세션 미허용")           # 묻지 못했으면 시도하지 않는다
        return False

    def _robots_ok(self, url, timeout):
        from urllib.robotparser import RobotFileParser
        u = urlparse(url)
        root = f"{u.scheme}://{u.netloc}"
        if root not in self._robots_cache:
            status, _, body = _get(root + "/robots.txt", min(timeout, 5))
            rp = RobotFileParser()
            rp.parse((body or "").splitlines() if alive(status) else [])
            self._robots_cache[root] = rp
        return self._robots_cache[root].can_fetch(UA, url)


def _load_allow(path=None):
    try:
        with open(path or ALLOW_SESSION_PATH, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return {}


def _save_allow(allow, path=None):
    path = path or ALLOW_SESSION_PATH
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(allow, f, ensure_ascii=False, indent=2)
    except OSError:
        pass


if __name__ == "__main__":
    lad = AccessLadder()
    for u in sys.argv[1:]:
        s, c, b = lad(u, 15)
        t = lad.trace[u]
        print(f"{u}\n  via={t['via']} status={s} len={len(b)} 시도={' → '.join(t['attempts'])}")
        if t["reason"]:
            print(f"  사유={t['reason']}\n  방안=" + "\n       ".join(t["options"]))
