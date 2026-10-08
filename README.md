# AI All In One

FastAPI와 Ollama를 사용해 외부 LLM API 없이 실행하는 온프레미스 LLM API입니다.
기본 Docker Compose 구성은 API와 Ollama를 같은 내부 네트워크에 두며, 모델 데이터는
Docker 영구 볼륨에 저장합니다. Ollama의 `11434` 포트는 호스트에 공개하지 않습니다.

## 현재 제공하는 기반

- `GET /health`: 배포 및 로컬 실행 확인용 상태 점검
- `GET /models`: 사내 Ollama 서버에 설치된 모델 목록
- `POST /chat`: Ollama 모델과의 단일 대화 요청 (비스트리밍)
- `GET /docs`: FastAPI 기본 API 문서
- `GET /openapi.yaml`: OpenAPI 명세 YAML
- 컨테이너 기반 Ollama 실행 및 모델 영구 보관
- `app.agent.supervisor.workflow:create_graph`: 이후 확장할 LangGraph 진입점

## 가장 쉬운 실행: Docker Compose

Docker와 Docker Compose가 설치된 Linux 서버에서 실행합니다. NVIDIA GPU를 쓸 경우
호스트에 NVIDIA 드라이버와 NVIDIA Container Toolkit이 먼저 준비되어 있어야 합니다.

```bash
cp .env.example .env
docker compose -f compose.yaml -f compose.gpu.yaml up -d --build
```

GPU가 없는 테스트 환경이라면 GPU 오버레이를 빼고 실행합니다. 모델 추론은 매우 느릴 수 있습니다.

```bash
docker compose up -d --build
```

### 1. 모델 내려받기

이미 실행된 Ollama 컨테이너에 원하는 모델을 한 번만 내려받습니다. 모델 파일은
`ollama-models` 볼륨에 남으므로 컨테이너를 재시작해도 다시 받지 않습니다.

```bash
docker compose exec ollama ollama pull llama3.2:3b
docker compose exec ollama ollama list
```

### 2. API 확인

API는 기본적으로 서버 자신의 `127.0.0.1:8000`에서만 열립니다. 서버에서 다음 명령으로
확인하거나, SSH 터널/리버스 프록시를 통해 접근하세요.

```bash
curl http://127.0.0.1:8000/health
# {"status":"ok"}

curl http://127.0.0.1:8000/models

curl -X POST http://127.0.0.1:8000/chat \
  -H 'Content-Type: application/json' \
  -d '{"message":"온프레미스 LLM이 무엇인가요?"}'
```

응답에서 `model`은 실제 사용 모델명이고, `message`는 Ollama의 답변입니다.

### 3. 상태 확인과 종료

```bash
docker compose ps
docker compose logs -f api
docker compose logs -f ollama
docker compose down
```

`docker compose down`은 컨테이너만 중지합니다. 모델 볼륨은 유지됩니다. 모델까지 지우려면
영구 데이터가 삭제된다는 점을 확인한 뒤 `docker compose down -v`를 사용하세요.

## API와 Ollama를 분리하는 운영 구성

권장 운영 형태는 GPU가 있는 Linux 서버에는 Ollama만 두고, API 서버는 별도로 배포하는 것입니다.
API 서버의 `.env`에 Ollama의 **사내망 주소**를 설정합니다.

```env
OLLAMA_BASE_URL=http://10.0.0.20:11434
OLLAMA_DEFAULT_MODEL=llama3.2:3b
OLLAMA_TIMEOUT_SECONDS=60
```

이때 Ollama 포트는 공용 인터넷에 노출하지 말고, 방화벽·VPN·사설 네트워크 또는 Kubernetes
Service로 API 서버에서만 접근하게 구성하세요. 별도 Ollama 서버를 쓰는 경우에도 `/models`,
`/chat` API의 사용법은 같습니다.

## 개발 환경에서 직접 실행

Docker 대신 Python 환경에서 API만 실행하려면 Python 3.13 이상과
[uv](https://docs.astral.sh/uv/)가 필요합니다. Ollama는 별도로 실행되어 있어야 합니다.

```bash
uv sync
uv run uvicorn main:app --reload
```

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
| `OLLAMA_BASE_URL` | 내부 Ollama 서버 주소 | 개발 실행 시 `http://127.0.0.1:11434` |
| `OLLAMA_DEFAULT_MODEL` | `/chat`에서 모델을 생략했을 때 사용할 모델 | `llama3.2:3b` |
| `OLLAMA_TIMEOUT_SECONDS` | Ollama 요청 제한 시간(초) | `60` |
| `API_BIND_ADDRESS` | Compose에서 API를 공개할 호스트 주소 | `127.0.0.1` |
| `API_PORT` | Compose에서 API를 공개할 포트 | `8000` |
| `OLLAMA_IMAGE` | Ollama 컨테이너 이미지 | `ollama/ollama:latest` |

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
