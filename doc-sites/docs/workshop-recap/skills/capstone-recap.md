---
sidebar_position: 1
title: "capstone-recap"
sidebar_label: "스킬: capstone-recap"
---

# capstone-recap Skill

완성된 캡스톤을 **하나의 자기완결 HTML 페이지**로 정리합니다. CSS는 인라인, 빌드 스텝 없음,
프레임워크 없음, 서버 없음 — 파일 하나(와 캡처가 있으면 그 옆의 이미지들)입니다.

핵심 차이: 페이지는 **인터뷰가 아니라 프로젝트가 생성한 콘텐츠에서** 작성됩니다. 프로젝트의
`CLAUDE.md`, 서브에이전트 파일, 훅 배선, 스펙, 워크플로, IaC가 사실의 출처이고, 그 파일들이
알려줄 수 없는 것만 참가자에게 묻습니다.

## 트리거

| 유형 | 예시 |
|------|------|
| 트리거됨 | "지금까지 만든 산출물을 정리해서 html로 만들어줘" |
| 트리거됨 | "워크숍 결과물 정리해서 한 페이지로 보여주는 html 만들어줘" |
| 트리거됨 | "캡스톤 끝났어. 내가 만든 거랑 어떤 스킬 썼는지 정리한 페이지 뽑아줘" |
| 트리거됨 | "capstone summary page" / "workshop recap" |
| 트리거 안 됨 | "kiro한테 시켜서 이 API 구현해줘" (구현 요청) |
| 트리거 안 됨 | "우리 제품 랜딩 페이지 브로셔로 만들어줘" (제품 마케팅) |
| 트리거 안 됨 | "html 파일 하나 만들어줘 버튼 세 개 있는" (범용 웹페이지) |
| 트리거 안 됨 | "capstone mission E 어떻게 시작하면 돼?" (작업 시작 문의) |

## 6단계 워크플로

### Phase 1 — 프로젝트 스캔

질문보다 스캔이 먼저입니다.

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/skills/capstone-recap/scripts/scan_capstone.py" <프로젝트-경로> --json
```

수집 항목 (각각 실제 경로가 붙습니다):

| 신호 | 근거가 되는 것 |
|------|---------------|
| `CLAUDE.md` / `AGENTS.md` | 프로젝트 목적·아키텍처·컨벤션 — 개요 문안의 원천 |
| `.claude/agents/*.md` | 만든 서브에이전트 (이름·설명·tools·model) |
| `.claude/commands/*.md` | 커스텀 슬래시 커맨드 |
| `skills/*/SKILL.md` | 작성한 스킬 |
| `.claude/settings*.json` | 훅 배선, 권한 개수, 환경변수 **이름** |
| `.mcp.json` | 연결한 MCP 서버 |
| `.claude-plugin/plugin.json` | 플러그인으로 패키징했는지 |
| `docs/superpowers/specs/*` | brainstorm → plan → execute 산출물 |
| `.github/workflows/*.yml` | 헤드리스 CI 통합 |
| `package.json` / `requirements.txt` | Agent SDK 사용 여부 |
| `cdk.json` / `template.yaml` / `*.tf` | 배포 대상과 인프라 |
| git | 커밋 수, 추적 파일 수, 작업 기간 |

:::warning 부재는 발견이 아닙니다
스캔에서 훅이 나오지 않으면 페이지는 훅에 대해 **아무 말도 하지 않습니다**. "훅을 사용하지
않았습니다"라고 쓰지 않습니다 — 스캐너가 볼 수 없는 작업을 참가자가 했을 수 있습니다.
:::

빈칸만 한 번의 `AskUserQuestion`으로 묻습니다: 미션/프로젝트 정체성(지시 파일에서 못 찾을 때),
공개 URL(후보를 못 찾았을 때 — 모든 미션이 하나를 배포하므로 "있는지"가 아니라 "무엇인지"를 물음),
회고(건너뛰면 섹션 자체를 생략).

### Phase 2 — 데모 캡처

`references/capture-guide.md`의 폴백 래더를 따릅니다.

```bash
curl -s -o /dev/null -w '%{http_code}\n' --max-time 10 "$URL"
```

`200`만이 링크를 "라이브"로 제시할 근거입니다. 그 외에는 상태 코드를 그대로 밝힙니다.
캡처가 불가능하면 사용자 제공 이미지 → 정직한 텍스트 설명 순으로 내려가며,
**플레이스홀더 이미지는 쓰지 않습니다**.

### Phase 3 — 디자인 방향 확정

`references/design-system.md`를 읽고 한 방향을 정확히 실행합니다. 토큰 세트, 타이포그래피
페어링, 768 2티어 브레이크포인트, 접근성 체크리스트, 반복되는 CSS 함정이 들어 있습니다.
게임이나 아트 갤러리처럼 자체 정체성이 있는 캡스톤은 그 프로젝트의 팔레트를 쓰는 편이
기본값보다 낫습니다 — 명암비만 통과하면 됩니다.

### Phase 4 — HTML 작성

파일 하나, CSS 인라인. 섹션 구성은 [개요](../overview.md#페이지-섹션-구성) 참고 —
근거 없는 섹션은 생략합니다.

`capabilities` 섹션은 각 항목을 mono로 출처와 함께 렌더링합니다:
`level-designer` → `.claude/agents/level-designer.md`

### Phase 5 — 자기검증

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/skills/capstone-recap/scripts/check_recap_html.py" <page.html>
```

게이트는 **0 FAIL**입니다. WARN은 고치거나, 이유를 밝혀 참가자에게 보고합니다.

| 옵션 | 용도 |
|------|------|
| `--mobile-breakpoint N` | 768 외의 브레이크포인트를 의도적으로 쓸 때 |
| `--allow-abs-paths` | 절대 경로 FAIL을 경고로 낮춤 (기기 밖으로 안 나가는 페이지 전용) |
| `--selftest` | 스크립트 자체 assertion 실행 |

검사 항목: 태그 균형, viewport 메타, 브레이크포인트 존재, `:focus-visible`, 스킵 링크,
`prefers-reduced-motion`, SMIL `<animate>` JS 제거, 로컬 자산 실재, `<img>` alt,
래스터 이미지 육안 확인 경고, **절대 홈 경로 유출(FAIL)**.

이 마켓플레이스에는 콘텐츠 점수를 매기는 리뷰어가 없으므로 게이트의 나머지 절반은
숫자가 아니라 사실 확인입니다 — **출처 원장**(주장 → 출처)을 출력하고 참가자의 확인을 받습니다.
참가자가 부정한 주장은 완화하지 않고 **삭제**합니다.

### Phase 6 — 출력

프로젝트 디렉토리에 `./capstone-recap.html`을 씁니다. 기존 파일이 있으면 덮어쓰기 전에 확인합니다.
**recap 페이지 자체의 배포는 opt-in**입니다 — 요청받았을 때만 GitHub Pages로 올리고, 같은
비인증 `curl` 200 검증을 거치며, 그 전에 삽입된 모든 인용문을 다시 검토합니다.

## 금지 사항

- 기능·지표·AWS 서비스·벡터 스토어·복구 서사·회고를 **지어내기**
- 출처 파일 / 검증된 URL / 참가자 서술 없는 주장을 페이지에 올리기
- 발견되지 않은 신호를 부정 주장으로 바꾸기
- 비인증 200 없이 URL을 라이브로 제시하기
- `.claude/`, `.kiro/`, 설정 파일에 **쓰기** — 이 스킬은 상태를 읽고 HTML 하나를 씁니다
- 요청 없이 배포하거나, 확인 없이 기존 recap을 덮어쓰기
- 환경변수 **값**·시크릿·계정 ID·ARN 노출. 텍스트 검사 통과를 스크린샷 승인으로 착각하지 않기 —
  픽셀은 사람이 눈으로 봐야 합니다

## 참조

| 파일 | 내용 |
|------|------|
| `references/design-system.md` | 토큰, 타이포그래피, 반응형 티어, 접근성, CSS 함정 |
| `references/capture-guide.md` | 미션별 캡처 레시피, 폴백 래더, 스크린샷 위생 |
| `scripts/scan_capstone.py` | 프로젝트 인벤토리 → JSON |
| `scripts/check_recap_html.py` | 구조/접근성 게이트 |
