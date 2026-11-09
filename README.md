# Tangible Heart — 참여형 질문 테스트

> 여섯 문항의 응답을 캐릭터 결과로 연결하고, 결과물을 라벨 프린터로 출력할 수 있도록 만든 Django 웹앱입니다.

## 프로젝트 소개

웹에서 질문에 답하는 경험을 오프라인 출력물로 이어주는 참여형 프로토타입입니다. 문항별 화면, 이전 문항 이동, 결과 이미지, 재시작과 출력 API를 구성했습니다.

## 주요 기능

- 6개 문항을 순서대로 진행하고 세션에 응답 저장
- 이전 문항 이동 시 이후 답변을 잘라내어 상태 정리
- 사전에 정의된 12개 응답 조합을 캐릭터 유형과 연결
- 미등록 조합·불완전 응답에 기본 유형 적용
- 결과 화면과 세션 초기화
- CUPS `lp` 명령을 통한 라벨 인쇄 요청

## 기술 스택

Python · Django · Django Templates · SQLite · HTML/CSS · CUPS

설정 파일은 Django 4.2.23으로 생성된 프로젝트임을 표시합니다. 현재 `requirements.txt`는 비어 있어 의존성 버전 고정이 필요합니다.

## 구현 포인트

**세션 기반 진행 관리:** 응답을 서버 세션에 유지하고 이전 이동·재시작 시 명시적으로 상태를 갱신합니다.

**결과 계산 분리:** `_compute_result_type()`에서 응답 조합과 유형을 연결합니다. 모든 가능한 답변 조합이 12개 유형으로 균등 분류되는 구조는 아니며, 미등록 조합은 `type_01`로 처리합니다.

**화면과 출력 연결:** 결과 화면용 이미지와 인쇄용 이미지 경로를 분리하고, POST API에서 프린터 명령을 실행합니다.

## 로컬 실행

```bash
python -m venv .venv
source .venv/bin/activate
pip install "Django>=4.2,<5"
python manage.py migrate
python manage.py runserver
```

이는 개발 환경 준비 예시이며 검증된 잠금 파일을 대신하지 않습니다. 일반 화면 확인 전 `tangible_heart/settings.py`의 `DIRECT_PRINT = False` 설정을 권장합니다. 현재 저장소 설정은 `True`입니다.

## 프린터 연동

macOS/Linux의 CUPS와 실제 프린터가 필요합니다. `LABEL_PRINTER_NAME`, `LABEL_MEDIA`를 장치에 맞게 설정합니다. 현재 저장소에는 `type_01_result.png` 인쇄용 파일만 포함되어 있습니다. 다른 유형의 `type_XX_result.png`는 별도로 준비해야 합니다.

## 코드 탐색

| 경로 | 역할 |
| --- | --- |
| [testapp/views.py](testapp/views.py) | 문항·결과·인쇄 처리 |
| [testapp/urls.py](testapp/urls.py) | URL 연결 |
| [testapp/templates](testapp/templates) | 화면 템플릿 |
| [testapp/static/characters](testapp/static/characters) | 캐릭터 이미지 |
| [tangible_heart/settings.py](tangible_heart/settings.py) | 개발·프린터 설정 |

## 현재 범위

참여형 콘텐츠 프로토타입이며 심리 진단 도구로 검증된 것은 아닙니다. 배포 전에는 개발용 비밀키·DEBUG·허용 호스트와 의존성 설정을 별도로 정리해야 합니다.
