# 어댑터 설정 스키마

출처 API 하나당 JSON 하나. **코드가 아니라 데이터다** (ADR 0002) — 새 출처를 붙일 때 스킬이나 모듈을 만들지 않고 이 폴더에 파일 하나를 넣는다.

| 키 | 뜻 |
|---|---|
| `name` | 어댑터 식별자. 감사 로그에 이 이름이 찍힌다 |
| `label` | 사람이 읽는 이름 |
| `hosts` | 이 어댑터가 맡는 호스트. 접근 사다리의 칸 1이 이 목록으로 어댑터를 고른다 |
| `identifier.scheme` | `doi` · `pmid` 등 식별자 종류 |
| `identifier.pattern` | 벌거벗은 식별자를 알아보는 정규식 (`10.1056/NEJMoa2007764`, `32445440`) |
| `identifier.url_patterns` | URL 에서 식별자를 뽑는 정규식들 |
| `identifier.canonical_url` | 식별자 → 사람이 여는 주소. 리포트에 이 주소를 적는다 |
| `endpoint` | `{id}` 를 끼워 넣는 API 주소 |
| `auth` | 인증 방식. `null` 이면 키 없이 쓴다. 키가 필요하면 **사용자가 발급해 환경변수로 준다** (ADR 0004) |
| `rate_limit_per_second` | 이 값을 넘지 않게 요청 사이를 벌린다 |
| `text.type` | `plain`(본문이 곧 응답) 또는 `json` |
| `text.fields` | `json` 일 때 대조할 텍스트가 있는 점 표기 경로들 |
| `text.inverted_index` | 역색인으로 저장된 초록의 경로 (OpenAlex) — 원문 순서로 되돌린다 |
| `text.landing` | 사람이 열 랜딩 URL 이 있는 경로 |
| `structured` | 문장 대조가 아니라 **필드 대조**가 필요할 때 쓰는 경로 묶음. `text.fields` 는 문자열을 이어 붙여 원문 텍스트를 만들지만, 평가변수처럼 `measure`·`timeFrame` 이 짝을 이룬 **객체 목록**은 그렇게 이으면 짝이 깨진다. `id`·`title`·`primary_outcomes`·`secondary_outcomes`(목록 경로) · `outcome_fields`(목록 안 객체의 키 이름) · `dates`(`registered`·`start`·`primary_completion`). 이 자리를 읽는 것은 `scripts/prereg.py` 하나뿐이고, 없는 어댑터는 그냥 건너뛴다 |
| `usage_headers` | 응답에서 감사 로그로 옮길 사용량·비용 헤더 |
| `note` | 실측으로 알게 된 것. 왜 이렇게 설정했는지 |

**실패는 `확인 불가`다.** 어댑터가 HTTP 로 실패하거나 응답 모양이 설정과 다르면 그 주장만 `blocked` 로 표기하고 나머지는 계속 간다 — 어댑터가 깨졌다고 "출처에 그런 말이 없다"고 말하지 않는다.
