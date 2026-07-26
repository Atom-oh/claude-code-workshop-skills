---
sidebar_position: 2
title: "설치"
---

# Workshop Recap 설치

## 마켓플레이스 설치

```bash
# 마켓플레이스 추가
/plugin marketplace add https://github.com/Atom-oh/claude-code-workshop-skills

# 플러그인 설치
/plugin install workshop-recap@claude-code-workshop-skills
```

## 로컬 로딩

```bash
claude --plugin-dir ./plugins/workshop-recap
```

## 설치 확인

### 매니페스트 검증

```bash
python3 -c "import json; d=json.load(open('plugins/workshop-recap/.claude-plugin/plugin.json')); print(f'workshop-recap: {len(d[\"agents\"])} agents, {len(d[\"skills\"])} skills')"
```

예상 출력:

```
workshop-recap: 1 agents, 1 skills
```

### 스크립트 자기검증

두 스크립트는 각자 내장 assertion을 가지고 있습니다. 외부 의존성이나 테스트 프레임워크는
필요하지 않습니다.

```bash
python3 plugins/workshop-recap/skills/capstone-recap/scripts/scan_capstone.py --selftest
python3 plugins/workshop-recap/skills/capstone-recap/scripts/check_recap_html.py --selftest
```

예상 출력:

```
scan_capstone selftest: all assertions passed
check_recap_html selftest: all assertions passed
```

### 저장소 구조 검증

```bash
bash tests/run-all.sh
```

## 플러그인 구조

```
workshop-recap/
├── .claude-plugin/plugin.json      # Claude 매니페스트
├── .codex-plugin/plugin.json       # Codex 매니페스트 (버전 동기 유지)
├── CLAUDE.md                       # 자동 호출 규칙 및 금지 사항
├── agents/
│   └── capstone-recap-agent.md     # 스캔 → 캡처 → 작성 → 검증 오케스트레이터
└── skills/capstone-recap/
    ├── SKILL.md                    # 6단계 워크플로 진입점
    ├── references/
    │   ├── design-system.md        # 토큰·타이포·반응형·접근성·CSS 함정
    │   └── capture-guide.md        # 미션 A–F 캡처 레시피 + 폴백 래더
    ├── scripts/
    │   ├── scan_capstone.py        # 프로젝트 인벤토리 → JSON
    │   └── check_recap_html.py     # 구조/접근성 게이트
    └── evals/trigger-eval.json     # 트리거 정확도 평가 세트
```

## 사전 요구 사항

| 항목 | 필요 여부 | 비고 |
|------|-----------|------|
| Python 3 | 필수 | 두 스크립트 모두 표준 라이브러리만 사용 |
| git | 선택 | 없으면 커밋/파일 수 통계만 생략됨 |
| curl | 선택 | 공개 URL 200 검증에 사용 |
| Playwright MCP | 선택 | 웹 UI 캡처용. 없으면 사용자가 이미지를 직접 제공 |

## 자동 호출 키워드

| 키워드 (한국어) | 키워드 (영어) |
|----------------|--------------|
| 지금까지 만든 산출물 정리 | summarize what i built |
| 산출물 정리해서 html | workshop recap |
| 워크숍 결과물 정리 | capstone summary |
| 실습 결과 정리 | capstone showcase |
| 캡스톤 정리 / 캡스톤 결과 페이지 | — |

구현·리뷰·변환 같은 **작업 수행** 요청이나 일반적인 "랜딩 페이지 만들어줘" 요청에는
트리거되지 않습니다.

:::tip 빠른 시작
캡스톤을 끝낸 프로젝트 디렉토리에서 `지금까지 만든 산출물을 정리해서 html로 만들어줘`라고
입력하면 스캔부터 시작합니다. 먼저 질문을 받는 대신, 프로젝트가 이미 가진 파일에서
사실을 수집한 뒤 빈칸만 물어봅니다.
:::

## 수동 실행

스킬을 거치지 않고 스크립트만 직접 쓸 수도 있습니다.

```bash
# 인벤토리 확인 (사람이 읽는 요약)
python3 plugins/workshop-recap/skills/capstone-recap/scripts/scan_capstone.py <프로젝트-경로>

# 인벤토리 JSON
python3 plugins/workshop-recap/skills/capstone-recap/scripts/scan_capstone.py <프로젝트-경로> --json

# 생성된 페이지 검증
python3 plugins/workshop-recap/skills/capstone-recap/scripts/check_recap_html.py capstone-recap.html
```

`check_recap_html.py`의 종료 코드는 `0` (실패 없음), `1` (FAIL 1건 이상), `2` (사용법 오류)입니다.
