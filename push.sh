#!/bin/bash
# 빠른 커밋 & 푸시 스크립트

set -e

BRANCH="claude/coding-agent-deepagent-chainlit-016coptmPhZ2EACt5fLgedUV"

# 인자가 없으면 사용법 표시
if [ -z "$1" ]; then
    echo "사용법: ./push.sh \"커밋 메시지\""
    echo ""
    echo "예시:"
    echo "  ./push.sh \"feat: 프로젝트 로딩 기능 추가\""
    echo "  ./push.sh \"fix: 버그 수정\""
    echo "  ./push.sh \"docs: 문서 업데이트\""
    exit 1
fi

COMMIT_MSG="$1"

echo "🔍 Step 1: 변경사항 확인..."
git status --short

echo ""
echo "🧪 Step 2: 빠른 검증..."

# Python 문법 체크 (변경된 .py 파일만)
CHANGED_PY_FILES=$(git diff --name-only HEAD | grep '\.py$' || true)
if [ -n "$CHANGED_PY_FILES" ]; then
    echo "  → Python 문법 체크 중..."
    for file in $CHANGED_PY_FILES; do
        if [ -f "$file" ]; then
            python -m py_compile "$file" 2>/dev/null && echo "    ✅ $file" || {
                echo "    ❌ $file 문법 오류!"
                exit 1
            }
        fi
    done
fi

# Import 테스트
echo "  → Import 테스트..."
python -c "
import sys
try:
    import agents
    import tools
    import llm
    print('    ✅ 모든 모듈 import 성공')
except Exception as e:
    print(f'    ❌ Import 실패: {e}')
    sys.exit(1)
" || exit 1

echo ""
echo "📦 Step 3: 변경사항 스테이징..."
git add .

echo ""
echo "💾 Step 4: 커밋..."
git commit -m "$COMMIT_MSG" || {
    echo "⚠️ 커밋할 변경사항이 없습니다."
    exit 0
}

echo ""
echo "🚀 Step 5: 푸시..."
git push -u origin $BRANCH

echo ""
echo "✅ 완료!"
echo "   커밋: $COMMIT_MSG"
echo "   브랜치: $BRANCH"
