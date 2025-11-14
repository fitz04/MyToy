# MyToy 프로젝트 개발 자동화 Makefile

.PHONY: help pull test push sync install run lint format clean

# 기본 타겟
help:
	@echo "════════════════════════════════════════"
	@echo "  MyToy 프로젝트 개발 도구"
	@echo "════════════════════════════════════════"
	@echo ""
	@echo "주요 명령어:"
	@echo "  make pull      - 원격 저장소에서 최신 코드 가져오기"
	@echo "  make test      - 빠른 검증 (문법, import)"
	@echo "  make push      - 변경사항 커밋 & 푸시"
	@echo "  make sync      - pull + test + (optional) push"
	@echo ""
	@echo "개발 명령어:"
	@echo "  make install   - 의존성 설치"
	@echo "  make run       - Chainlit 앱 실행"
	@echo "  make lint      - 코드 품질 검사 (flake8, pylint)"
	@echo "  make format    - 코드 포매팅 (black, isort)"
	@echo "  make clean     - 캐시 파일 정리"
	@echo ""
	@echo "예시:"
	@echo "  make sync                    # 동기화 (대화형)"
	@echo "  make push MSG=\"feat: 기능 추가\"  # 빠른 푸시"
	@echo ""

# Git 작업
pull:
	@echo "📥 원격 변경사항 가져오는 중..."
	@./dev.sh

push:
	@if [ -z "$(MSG)" ]; then \
		echo "❌ 커밋 메시지가 필요합니다."; \
		echo "사용법: make push MSG=\"커밋 메시지\""; \
		exit 1; \
	fi
	@./push.sh "$(MSG)"

sync:
	@./sync.sh

# 테스트 & 검증
test:
	@echo "🧪 빠른 검증 중..."
	@echo ""
	@echo "→ Python 문법 체크..."
	@python -m py_compile app.py && echo "  ✅ app.py" || echo "  ❌ app.py"
	@echo ""
	@echo "→ 모듈 Import 테스트..."
	@python -c "import agents, tools, llm, config; print('  ✅ 모든 모듈 OK')" || echo "  ❌ Import 실패"
	@echo ""
	@echo "✅ 검증 완료!"

# 의존성
install:
	@echo "📦 의존성 설치 중..."
	@pip install -r requirements-core.txt
	@echo "✅ 핵심 의존성 설치 완료!"
	@echo ""
	@echo "선택사항:"
	@echo "  pip install -r requirements-ui.txt    # Chainlit UI"
	@echo "  pip install -r requirements-full.txt  # 전체 기능"

install-ui:
	@pip install -r requirements-ui.txt

install-full:
	@pip install -r requirements-full.txt

install-dev:
	@echo "📦 개발 도구 설치 중..."
	@pip install black flake8 pylint isort pytest pytest-cov
	@echo "✅ 개발 도구 설치 완료!"

# 실행
run:
	@echo "🚀 Chainlit 앱 실행 중..."
	@chainlit run app.py -w

# 코드 품질
lint:
	@echo "🔍 코드 품질 검사 중..."
	@echo ""
	@echo "→ flake8..."
	@flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics || true
	@echo ""
	@echo "→ pylint..."
	@pylint agents/ tools/ llm/ --exit-zero || true

format:
	@echo "✨ 코드 포매팅 중..."
	@echo ""
	@echo "→ isort (import 정리)..."
	@isort . --profile black
	@echo ""
	@echo "→ black (코드 포매팅)..."
	@black . --line-length 88
	@echo ""
	@echo "✅ 포매팅 완료!"

# 정리
clean:
	@echo "🧹 캐시 파일 정리 중..."
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete
	@find . -type f -name "*.pyo" -delete
	@find . -type f -name "*.pyd" -delete
	@find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	@echo "✅ 정리 완료!"

# 테스트 (pytest)
pytest:
	@pytest tests/ -v --tb=short

pytest-cov:
	@pytest tests/ -v --cov=. --cov-report=html --cov-report=term

# 상태 확인
status:
	@echo "📊 프로젝트 상태"
	@echo "════════════════════════════════════════"
	@echo ""
	@echo "Git 상태:"
	@git status --short
	@echo ""
	@echo "브랜치:"
	@git branch --show-current
	@echo ""
	@echo "최근 커밋:"
	@git log --oneline -5
