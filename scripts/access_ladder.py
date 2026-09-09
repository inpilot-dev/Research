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
from http.client import HTTPException
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import adapters  # noqa: E402
from cite_check import UA, alive, has_source_text, is_pdf, publisher, readable_text  # noqa: E402

# ── 사유 코드 ────────────────────────────────────────────────────────────────
# 기획(17 §4)의 8종 + dead. 죽은 링크는 인용 부패의 가장 흔한 형태인데 8종에 자리가
# 없었다. bot-wall 로 뭉개면 "사이트가 막았다"는 거짓말이 되므로 코드를 하나 늘렸다.
REASONS = ("bot-wall", "captcha", "login", "paywall", "robots", "pdf", "dynamic", "budget", "dead")

# 챌린지 표식은 상태 코드와 같은 급의 구조적 신호다 — 본문 낱말보다 먼저 본다.
_CHALLENGE = re.compile(r"(?i)cf-chl|challenge-platform|__cf_chl|checking your browser|잠시만 기다리십시오")
_MARK = (
    ("captcha", re.compile(r"(?i)recaptcha|hcaptcha|turnstile|g-recaptcha|\bcaptcha\b|are you a (robot|human)")),
    # 낱말이 아니라 구조·문구로 본다. 맨 'sign in' 은 멀쩡한 기사 내비게이션에도 있고,
    # 그걸로 login 판정을 내리면 공격자 페이지가 "세션 재사용을 허락해 달라"는 제안을 끌어낸다.
    ("login", re.compile(r"""(?i)type=["']password["']|(sign|log) ?in to (read|continue|view|access)|"""
                         r"""institutional (sign|log)[- ]?in|\bauthentication required\b|로그인 후 이용""")),
    ("paywall", re.compile(r"(?i)subscribe to (read|continue)|subscription (is )?required|paywall|"
                           r"purchase (access|this article)|already a subscriber|\b구독\b")),
    ("bot-wall", re.compile(r"(?i)enable javascript|cookies? (are |must be )?(required|enabled)|access denied|"
                            r"unusual traffic|cloudflare|checking your browser|bot detection|"
                            r"cf-chl|challenge-platform|잠시만 기다리십시오")),
)
# 완전 방어는 불가능하다(15 §6). 목표는 차단이 아니라 표시 — 리더가 이 출처를 요약할 때 알게 한다.
# 제로폭 문자 하나로 정규식을 피할 수 있으므로 먼저 지운다. 한국어 출처도 읽으므로 한국어도 본다.
_ZERO_WIDTH = re.compile(r"[\u200b-\u200f\u2028\u2029\ufeff\u00ad]")
_INJECT = re.compile(r"(?i)ignore (all |any )?(the )?(previous|prior|above|earlier)"
                     r"|disregard (all |any )?(the )?(previous|prior|above|earlier)"
                     r"|new instructions?\s*:"
                     r"|you are now (a|an|in|the)\b"
                     r"|system prompt\b"
                     r"|<\s*\|?\s*im_start"
                     r"|<!--\s*(assistant|ai|claude|system)\b"
                     r"|(이전|앞|위)의? ?(지시|지침|명령)(사항)?(을|를)? ?무시"
                     r"|시스템 프롬프트")


def injected(text):
    """지시문처럼 보이는 문구가 있나. 표시가 목적이지 차단이 목적이 아니다.

    제로폭 문자는 낱말 안에 박아 넣으면(Ig<zwsp>nore) 지워야 잡히고, 낱말 사이에 박아 넣으면
    (Ignore<zwsp>all) 지우는 순간 붙어버려 안 잡힌다. 그래서 지운 것과 공백으로 바꾼 것을 둘 다 본다.
    """
    t = text or ""
    return bool(_INJECT.search(_ZERO_WIDTH.sub("", t)) or _INJECT.search(_ZERO_WIDTH.sub(" ", t)))

ALLOW_SESSION_PATH = os.environ.get(
    "VERIFY_ALLOW_SESSION", os.path.expanduser("~/.config/verify/allow-session.json"))


def classify(status, ctype, body):
    """읽지 못한 응답의 사유 코드. 본문 표식 → 상태 코드 순으로 본다."""
    ctype = ctype or ""
    if alive(status) and is_pdf(ctype, body):
        return "pdf"
    # PDF 가 아닌데 바이트라면 텍스트 표식을 찾을 수 없다. 스캔하지 않고 상태 코드로만 본다.
    body = body if isinstance(body, str) else ""
    if status is None or status in (404, 410):
        return "dead"
    head = body[:200000]
    if _CHALLENGE.search(head) or status == 203:
        return "bot-wall"
    if status == 402:
        return "paywall"
    if status == 401:
        return "login"
    if status in (403, 429):
        return "bot-wall"
    for reason, pat in _MARK:
        if pat.search(head):
            return reason
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


def rung(*, escalates=False, consent=False, impersonates=False, forwards_url=False):
    """칸의 성질을 그 칸의 함수에 붙인다.

    게이트를 칸 번호(n == 5)에 걸면 칸 하나만 끼워 넣어도 게이트가 조용히 빠진다 —
    로그인된 브라우저가 허락 없이 도는 길이 생긴다. 그래서 번호가 아니라 능력으로 건다.
    """
    def deco(fn):
        fn.escalates = escalates          # robots.txt 를 존중해야 하는 칸인가
        fn.needs_consent = consent        # 사용자의 로그인 세션을 쓰는 칸인가
        fn.impersonates = impersonates    # TLS 위장을 쓰는 칸인가
        fn.forwards_url = forwards_url    # URL 을 제3자에게 넘기는 칸인가
        return fn
    return deco


_SECRETISH = re.compile(r"(?i)(^|&)[^=&]*(token|key|secret|signature|sig|password|passwd|auth|session)=")
_PRIVATE = re.compile(r"^(localhost|127\.|10\.|192\.168\.|172\.(1[6-9]|2\d|3[01])\.)")


def forwardable(url):
    """이 URL 을 외부 추출기·아카이브에 넘겨도 되나.

    넘기면 그 URL 은 제3자의 기록으로 남는다 (아카이브는 영구 공개다). 서명된 링크·사내 주소·
    자격증명이 박힌 URL 은 넘기지 않는다 — 읽으려다 사용자의 비밀 링크를 공개하면 안 된다.
    """
    try:
        u = urlparse(url)
    except ValueError:
        return False
    if "@" in u.netloc:
        return False
    host = u.netloc.split(":")[0].lower()
    if not host or "." not in host or _PRIVATE.match(host) or host.endswith((".local", ".internal", ".lan")):
        return False
    return not _SECRETISH.search(u.query or "")


def _readable(status, ctype, body):
    """대조에 쓸 수 있는 진짜 본문인가 — 코어와 같은 기준을 쓴다.

    PDF 는 받아온 것만으로 "닿았다" 로 친다. 그 안에 글자가 있는지는 추출기가 있어야 알 수
    있고 그 판단은 코어의 몫이다 — 사다리가 여기서 미리 실패로 접으면, 추출기가 깔려 있어도
    윗칸만 헛되이 오르고 결국 못 읽는다."""
    if not alive(status):
        return False
    if isinstance(body, bytes):
        return True
    text, _ = readable_text(ctype, body)
    return has_source_text(status, text)


def _get(url, timeout, ua=UA, headers=None):
    try:
        # Request() raises on a malformed URL — inside the try, or one bad citation kills the run.
        req = Request(url, headers={"User-Agent": ua, "Accept": "text/html,*/*", **(headers or {})})
        with urlopen(req, timeout=timeout) as r:
            ctype, raw = r.headers.get("Content-Type", ""), r.read()
            # PDF 는 바이트 그대로 넘긴다. 여기서 문자열로 만들면("replace") 바이트가
            # 되돌릴 수 없게 망가져 어떤 추출기도 읽을 수 없다 — 코어의 계약도 같다.
            if is_pdf(ctype, raw):
                return r.status, ctype, raw
            return r.status, ctype, raw.decode(r.headers.get_content_charset() or "utf-8", "replace")
    except HTTPError as e:
        try:
            return e.code, e.headers.get("Content-Type", "") if e.headers else "", e.read().decode("utf-8", "replace")
        except Exception:
            return e.code, "", ""
    except (URLError, TimeoutError, ValueError, OSError, HTTPException):
        return None, "", ""   # HTTPException: IncompleteRead is neither OSError nor URLError


# 칸 5가 사용자의 브라우저에서 돌리는 스크립트 — 전문이 여기 있다. 여는 것·기다리는 것·읽는 것·
# 닫는 것뿐이다. 사람이 하는 순서와 같다: 탭에서 열고, 화면이 자리잡길 잠깐 기다리고, 읽는다.
# 기다리는 것은 로딩을 기다리는 것이지 CAPTCHA 를 푸는 것이 아니다 — 그건 하지 않는다.
# 상태를 200으로 박아두면 403 챌린지 페이지가 200짜리 본문으로 둔갑한다(NEJM 실측). 그래서
# 아직 대기 화면이면 그때만 브라우저에 진짜 상태를 물어본다.
# 이 상수에 등장할 수 있는 이름은 테스트가 허용 목록으로 못박는다 — aside 는 자격증명·메일·
# 쿠키·CAPTCHA 전역도 노출하지만 그 이름들은 여기 있을 수 없다 (ADR 0004).
ASIDE_READ_JS = """const W = /cf-chl|challenge-platform|__cf_chl|checking your browser/i;
const t = await openTab(%(u)s);
let h = await page.content();
for (let i = 0; i < 3 && W.test(h); i++) { await sleep(2000); h = await page.content(); }
let s = 200;
if (W.test(h)) { try { s = (await fetch(%(u)s)).status; } catch (e) { s = 403; } }
console.log(JSON.stringify({s: s, h: h}));
await closeTab(t);"""


class AccessLadder:
    """cite_check 에 주입하는 fetcher. 호출부는 (status, ctype, body) 만 본다."""

    def __init__(self, *, tls=True, extractor=True, session=True, budget=30.0, registry=None,
                 allow_session=None, consent=None, clock=time.monotonic, rungs=None, robots=None):
        self.registry = registry if registry is not None else adapters.Registry()
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
        tr = {"via": None, "attempts": [], "reason": None, "options": [], "forwarded": [],
              "injection_suspect": False, "archive": False, "tls": False}
        self.trace[url] = tr
        for n, fn in self._rungs:
            left = self.budget - (self.clock() - t0)
            if left <= 0:
                return self._stop(url, tr, "budget", last)
            if getattr(fn, "escalates", False) and not self._robots_ok_guarded(url, timeout):
                tr["attempts"].append(f"{n}:robots-disallow")
                return self._stop(url, tr, "robots", last)
            if getattr(fn, "needs_consent", False) and not self._session_ok(url, tr):
                continue
            try:
                got = fn(url, min(timeout, left), tr, left)
            except Exception as e:                      # 한 칸이 터져도 사다리는 계속 오른다
                tr["attempts"].append(f"{n}:error {type(e).__name__}")
                continue
            if got is None:
                continue
            status, ctype, body = got
            # 이긴 칸의 본문만 보면, 아래 칸에서 이미 읽은 지시문을 놓친다.
            # PDF 바이트에는 텍스트 패턴 검사를 걸 수 없다. 추출된 본문은 코어가 본다.
            tr["injection_suspect"] = tr["injection_suspect"] or (isinstance(body, str) and injected(body))
            if _readable(status, ctype, body):
                tr["attempts"].append(f"{n}:ok")
                tr["via"] = n
                tr["tls"] = getattr(fn, "impersonates", False)   # 진 칸의 수단을 성공에 붙이지 않는다
                return got
            last = got
            tr["attempts"].append(f"{n}:{status if status is not None else 'net-error'}")
            reason = classify(status, ctype, body)
            # 여기 오는 PDF 는 응답 자체가 성립하지 않은 것이다(받아낸 PDF 는 위에서 이미 반환됐다).
            # 윗칸이라고 살아 있는 응답이 되지 않으므로 더 오르지 않는다. CAPTCHA 는 풀지 않지만(성역), 아래 칸에서 봤다고
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
    def _direct(self, url, timeout, tr, left):
        return _get(url, timeout)

    def _adapter(self, url, timeout, tr, left):
        self.registry.used = None          # 앞 URL 이 쓴 어댑터가 이 URL 에 눌러붙지 않게
        status, ctype, body = self.registry.fetch(url, timeout)
        if status is None:
            tr["attempts"].append("1:어댑터 없음")
            return None
        if self.registry.used:
            tr["adapter"] = self.registry.used
        return status, ctype, body

    @rung(forwards_url=True)
    def _extractor(self, url, timeout, tr, left):
        if not self.extractor:
            tr["attempts"].append("2:꺼짐")
            return None
        if not forwardable(url):
            tr["attempts"].append("2:건너뜀(사적·서명된 URL 은 제3자에 넘기지 않음)")
            return None
        tr["forwarded"] = ["r.jina.ai", "web.archive.org"]   # 감사 로그에 남긴다
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

    @rung(escalates=True, impersonates=True)
    def _impersonate(self, url, timeout, tr, left):
        if not self.tls:
            tr["attempts"].append("3:꺼짐")
            return None
        try:
            from curl_cffi import requests as cffi     # ponytail: 선택 의존성, 없으면 그냥 건너뛴다
        except ImportError:
            tr["attempts"].append("3:건너뜀(curl_cffi 미설치)")
            return None
        r = cffi.get(url, impersonate="chrome", timeout=timeout)
        ctype = r.headers.get("Content-Type", "")
        return r.status_code, ctype, (r.content if is_pdf(ctype, r.content) else r.text)

    @rung(escalates=True)
    def _headless(self, url, timeout, tr, left):
        try:
            from playwright.sync_api import sync_playwright
        except ImportError:
            tr["attempts"].append("4:건너뜀(playwright 미설치)")
            return None
        with sync_playwright() as p:                    # 비로그인 렌더링만 — 사용자 프로필을 쓰지 않는다
            b = p.chromium.launch()
            try:
                pg = b.new_page()
                # 상태를 200으로 박으면 렌더된 404·403 페이지가 살아있는 본문이 된다 — 칸 5에서
                # 실제로 났던 버그다. 응답이 알려주는 상태를 그대로 쓴다.
                resp = pg.goto(url, timeout=int(min(timeout, left) * 1000))
                ctype = (resp.header_value("content-type") or "text/html") if resp else "text/html"
                return (resp.status if resp else None), ctype, pg.content()
            finally:
                b.close()

    @rung(escalates=True, consent=True)
    def _browser_session(self, url, timeout, tr, left):
        """칸 5 — 사용자가 이미 로그인한 브라우저로 '읽기만' 한다.

        여는 것·읽는 것 외에는 아무것도 하지 않는다. aside 는 자격증명 접근(applePasswords)과
        CAPTCHA 처리 기능도 노출하지만 이 모듈은 그 둘을 호출하지 않는다 (성역 — 테스트로 고정).
        """
        exe = shutil.which("aside")
        if not exe:
            tr["attempts"].append("5:건너뜀(aside 미설치)")
            return None
        js = ASIDE_READ_JS % {"u": json.dumps(url)}
        p = subprocess.run([exe, "repl", js], capture_output=True, text=True,
                           timeout=max(5.0, min(left, 60.0)))
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

    @property
    def usage(self):
        """어댑터 API 가 알려준 사용량·비용 — 감사 로그로 넘어간다."""
        return self.registry.usage

    def _robots_ok_guarded(self, url, timeout):
        """robots 조회가 터져도 사다리 전체를 죽이지 않는다 — 못 읽으면 허용으로 본다."""
        try:
            return self._robots_check(url, timeout)
        except Exception:
            return True

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
