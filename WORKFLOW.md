# 🔄 개발 워크플로우 가이드

> 로컬 개발을 더 편하게! 자동화 스크립트와 Makefile 사용법

---

## 🎯 문제점과 해결책

### 이전 워크플로우 (번거로움)
```bash
# 매번 반복...
git pull origin claude/coding-agent-deepagent-chainlit-016coptmPhZ2EACt5fLgedUV
python app.py  # 테스트
# 오류 발견 → 수정
git add .
git commit -m "fix: ..."
git push -u origin claude/coding-agent-deepagent-chainlit-016coptmPhZ2EACt5fLgedUV
```

### 새로운 워크플로우 (간단!)
```bash
# 한 번에!
make sync              # pull + test + (optional) push
# 또는
make push MSG="feat: 새 기능"  # 빠른 푸시
```

---

## 🚀 빠른 시작

### 1. Makefile 사용 (가장 추천!) ⭐

```bash
# 도움말 보기
make help

# 전체 동기화 (pull + test + 선택적 push)
make sync

# 빠른 푸시
make push MSG="feat: 프로젝트 로딩 기능 추가"

# 원격에서 가져오기만
make pull

# 검증만
make test

# 앱 실행
make run

# 코드 포매팅
make format

# 상태 확인
make status
```

**Makefile 장점**:
- ✅ 타이핑이 짧음 (`make sync` vs `./sync.sh`)
- ✅ 탭 자동완성 지원
- ✅ 다양한 명령어 한곳에 정리
- ✅ 크로스 플랫폼 (Linux, Mac, Windows with WSL)

---

### 2. Shell 스크립트 사용

#### `./sync.sh` - 올인원 동기화 ⭐⭐⭐

```bash
./sync.sh
```

**실행 과정**:
1. 📥 원격 변경사항 pull
2. 🧪 Python 문법 체크
3. 🧪 모듈 import 테스트
4. 🧪 의존성 체크
5. 💬 (선택) 로컬 변경사항 푸시

**언제 사용?**
- 작업 시작 시
- 다른 환경에서 작업 후
- 협업 시 충돌 방지

---

#### `./dev.sh` - Pull & Test

```bash
./dev.sh
```

**실행 과정**:
1. 📥 원격 변경사항 pull
2. 🧪 기본 검증 (문법, import)
3. 📝 다음 명령어 안내

**언제 사용?**
- Pull만 하고 싶을 때
- 변경사항 확인만 할 때

---

#### `./push.sh` - Commit & Push

```bash
./push.sh "feat: 새 기능 추가"
./push.sh "fix: 버그 수정"
./push.sh "docs: 문서 업데이트"
```

**실행 과정**:
1. 🔍 변경사항 확인
2. 🧪 변경된 Python 파일 문법 체크
3. 🧪 모듈 import 테스트
4. 📦 스테이징 (git add .)
5. 💾 커밋
6. 🚀 푸시

**언제 사용?**
- 빠른 커밋&푸시가 필요할 때
- 검증 후 즉시 푸시하고 싶을 때

---

## 📋 일반적인 시나리오

### 시나리오 1: 작업 시작

```bash
# 방법 1: Makefile
make pull
make test

# 방법 2: 스크립트
./dev.sh
```

---

### 시나리오 2: 기능 개발 후 푸시

```bash
# 방법 1: Makefile (가장 빠름)
make push MSG="feat: 프로젝트 로딩 UI 추가"

# 방법 2: 스크립트
./push.sh "feat: 프로젝트 로딩 UI 추가"

# 방법 3: 수동
git add .
git commit -m "feat: 프로젝트 로딩 UI 추가"
git push -u origin claude/coding-agent-deepagent-chainlit-016coptmPhZ2EACt5fLgedUV
```

---

### 시나리오 3: 다른 환경에서 작업 후 동기화

```bash
# 방법 1: Makefile
make sync

# 방법 2: 스크립트
./sync.sh
```

대화형으로:
1. Pull 실행
2. 검증 자동 실행
3. 로컬 변경사항이 있으면 → 푸시할지 물어봄
4. 커밋 메시지 입력
5. 자동 푸시

---

### 시나리오 4: 코드 품질 개선

```bash
# 코드 포매팅
make format

# Lint 검사
make lint

# 둘 다 실행
make format lint
```

---

## 🛠️ 고급 사용법

### Git Hooks 설정 (선택사항)

commit이나 push 전에 자동으로 검증하도록 설정:

```bash
# .git/hooks/pre-commit 파일 생성
cat > .git/hooks/pre-commit << 'EOF'
#!/bin/bash
echo "🧪 Pre-commit 검증 중..."
python -m py_compile app.py || {
    echo "❌ app.py 문법 오류!"
    exit 1
}
echo "✅ 검증 완료!"
EOF

chmod +x .git/hooks/pre-commit
```

이제 `git commit` 시 자동으로 검증됩니다!

---

### VS Code Tasks 설정

`.vscode/tasks.json` 생성:

```json
{
  "version": "2.0.0",
  "tasks": [
    {
      "label": "Sync (Pull + Test + Push)",
      "type": "shell",
      "command": "make sync",
      "group": "build",
      "presentation": {
        "reveal": "always",
        "panel": "new"
      }
    },
    {
      "label": "Quick Push",
      "type": "shell",
      "command": "make push MSG=\"${input:commitMessage}\"",
      "group": "build"
    }
  ],
  "inputs": [
    {
      "id": "commitMessage",
      "type": "promptString",
      "description": "커밋 메시지"
    }
  ]
}
```

이제 `Ctrl+Shift+B` → "Sync" 선택하면 실행됩니다!

---

### Alias 설정 (더 짧게!)

`~/.bashrc` 또는 `~/.zshrc`에 추가:

```bash
# MyToy 프로젝트 alias
alias mtoy='cd /path/to/MyToy'
alias mpull='make pull'
alias mpush='make push MSG='
alias msync='make sync'
alias mrun='make run'
alias mtest='make test'
```

이제:
```bash
mtoy         # 프로젝트 디렉토리로 이동
msync        # 동기화
mpush "fix"  # 빠른 푸시
mrun         # 앱 실행
```

---

## 📊 스크립트 비교

| 기능 | `make sync` | `make push` | `make pull` | `make test` |
|------|-------------|-------------|-------------|-------------|
| Pull | ✅ | ❌ | ✅ | ❌ |
| 문법 체크 | ✅ | ✅ | ✅ | ✅ |
| Import 테스트 | ✅ | ✅ | ✅ | ✅ |
| 의존성 체크 | ✅ | ❌ | ✅ | ❌ |
| Commit | 선택적 | ✅ | ❌ | ❌ |
| Push | 선택적 | ✅ | ❌ | ❌ |
| 대화형 | ✅ | ❌ | ❌ | ❌ |

**추천 사용법**:
- 🌅 **작업 시작**: `make pull`
- 💾 **빠른 저장**: `make push MSG="..."`
- 🔄 **전체 동기화**: `make sync`
- 🧪 **검증만**: `make test`

---

## 🐛 문제 해결

### 문제 1: "permission denied" 오류

```bash
chmod +x dev.sh push.sh sync.sh
```

### 문제 2: "make: command not found"

```bash
# Ubuntu/Debian
sudo apt install make

# Mac
xcode-select --install

# 또는 스크립트 직접 사용
./sync.sh
```

### 문제 3: Python 문법 오류

```bash
# 어떤 파일에 오류가 있는지 확인
python -m py_compile app.py
python -m py_compile agents/*.py
python -m py_compile tools/*.py
```

### 문제 4: Import 실패

```bash
# 의존성 재설치
make install

# 또는
pip install -r requirements-core.txt
```

---

## 💡 팁

### 1. Commit 메시지 규칙

```bash
feat: 새 기능 추가
fix: 버그 수정
docs: 문서 업데이트
refactor: 리팩토링
test: 테스트 추가
chore: 기타 작업
```

예시:
```bash
make push MSG="feat: 프로젝트 로딩 UI 구현"
make push MSG="fix: import 오류 수정"
make push MSG="docs: WORKFLOW.md 추가"
```

### 2. 작업 전 항상 Pull

```bash
# 작업 시작 전
make pull

# 변경사항 확인
make status
```

### 3. 자주 커밋하기

작은 단위로 자주 커밋:
```bash
make push MSG="feat: SessionManager 클래스 추가"
# ... 작업 ...
make push MSG="feat: SessionManager save 메서드 구현"
# ... 작업 ...
make push MSG="feat: SessionManager load 메서드 구현"
```

### 4. 포매팅 자동화

커밋 전 자동 포매팅:
```bash
make format
make push MSG="style: 코드 포매팅"
```

---

## 🎓 학습 리소스

- **Makefile 문법**: https://makefiletutorial.com/
- **Git Hooks**: https://git-scm.com/book/en/v2/Customizing-Git-Git-Hooks
- **Shell Script**: https://www.shellscript.sh/

---

## 📝 요약

### 매일 사용할 명령어

```bash
# 1. 작업 시작
make pull

# 2. 개발...

# 3. 빠른 푸시
make push MSG="feat: 기능 추가"

# 또는 전체 동기화
make sync
```

**이것만 기억하세요**: `make sync` 하나면 충분합니다! 🚀

---

**작성일**: 2025-11-15
**최종 업데이트**: 2025-11-15
