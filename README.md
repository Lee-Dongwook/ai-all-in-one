# AI All In One

FastAPI와 LangGraph를 기반으로 AI 기능을 조합하기 위한 백엔드 스캐폴딩입니다.
현재는 서버 부트스트랩, 상태 초기화, 빈 supervisor 그래프와 공통 보안 유틸까지만
구성된 MVP 기반입니다. 실제 모델, 도구, 인증 흐름은 각 기능 요구사항이 정해진 뒤 추가합니다.

## 현재 제공하는 기반

- `GET /health`: 배포 및 로컬 실행 확인용 상태 점검
- `GET /models`: 사내 Ollama 서버에 설치된 모델 목록
- `POST /chat`: Ollama 모델과의 단일 대화 요청 (비스트리밍)
- `GET /docs`: FastAPI 기본 API 문서
- `GET /openapi.yaml`: OpenAPI 명세 YAML
- `app.agent.supervisor.workflow:create_graph`: LangGraph에서 불러올 수 있는 최소 그래프
- 환경 변수 기반 쿠키·암호화 유틸

## 실행

Python 3.13 이상과 [uv](https://docs.astral.sh/uv/)를 준비한 뒤 실행합니다.

```bash
uv sync
uv run uvicorn main:app --reload
```

브라우저에서 `http://127.0.0.1:8000/docs`를 열거나, 다음으로 서버를 확인합니다.

```bash
curl http://127.0.0.1:8000/health
# {"status":"ok"}
```

## Ollama 연결

이 프로젝트는 외부 LLM API를 호출하지 않고 Ollama의 HTTP API만 사용합니다. API 서버와
같은 머신에서 Ollama를 실행하는 기본 구성이면 별도 설정이 필요 없습니다.

```bash
ollama serve
ollama pull llama3.2:3b
curl http://127.0.0.1:8000/models
curl -X POST http://127.0.0.1:8000/chat \
  -H 'Content-Type: application/json' \
  -d '{"message":"온프레미스 LLM이 무엇인가요?"}'
```

사내 GPU 서버처럼 Ollama가 다른 머신에 있다면 API 서버의 `.env`에 내부망 주소를 설정합니다.

```env
OLLAMA_BASE_URL=http://10.0.0.20:11434
OLLAMA_DEFAULT_MODEL=llama3.2:3b
OLLAMA_TIMEOUT_SECONDS=60
```

`/chat` 요청에서 `model`을 전달하면 기본 모델 대신 해당 설치 모델을 사용합니다.

## 환경 변수

암호화 기능을 사용할 때만 `SECRET_ENCRYPTION_KEY`가 필요합니다. Fernet 키는 아래처럼
생성하고, 실제 값은 저장소에 커밋하지 마세요.

```bash
uv run python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

| 변수 | 용도 | 기본값 |
| --- | --- | --- |
| `COOKIE_SECURE` | 쿠키의 Secure 속성 (`auto`, `true`, `false`) | `auto` |
| `CORS_ALLOWED_ORIGINS` | 허용할 Origin의 쉼표 구분 목록 | 비어 있음 |
| `CORS_ALLOWED_ORIGINS_REGEX` | 허용할 Origin 정규식 | 비어 있음 |
| `SIGNING_KEY` | 서명 기능에서 사용할 키 | 없음 |
| `AUTH_SESSION_SIGNING_KEY` | 세션 서명 키. 없으면 `SIGNING_KEY` 사용 | 없음 |
| `SECRET_ENCRYPTION_KEY` | Fernet 암호화 키 | 없음 |
| `OLLAMA_BASE_URL` | 내부 Ollama 서버 주소 | `http://127.0.0.1:11434` |
| `OLLAMA_DEFAULT_MODEL` | `/chat`에서 모델을 생략했을 때 사용할 모델 | `llama3.2:3b` |
| `OLLAMA_TIMEOUT_SECONDS` | Ollama 요청 제한 시간(초) | `60` |

## 폴더 구조

```text
src/app/
├── bootstrap.py                 # FastAPI 앱 생성 및 공통 예외 처리
├── agent/
│   └── supervisor/              # 에이전트 상태·입력·LangGraph 진입점
└── core/
    ├── shared/                  # 설정, 쿠키, 오류, 보안 유틸
    └── utils.py                 # Origin / Redirect URI 검증
```

## 다음 구현 순서

1. 서비스의 첫 AI 사용 시나리오와 요청·응답 형식을 확정합니다.
2. 그 시나리오용 API 라우터와 supervisor 그래프 노드를 추가합니다.
3. Ollama 모델별 프롬프트·권한·대화 이력 정책을 추가합니다.
