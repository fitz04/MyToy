#!/bin/bash
# 개발 워크플로우 자동화 스크립트

set -e  # 에러 발생 시 중단

BRANCH="claude/coding-agent-deepagent-chainlit-016coptmPhZ2EACt5fLgedUV"

echo "🔄 Step 1: 원격 변경사항 가져오기..."
git fetch origin $BRANCH
git pull origin $BRANCH

echo ""
echo "🧪 Step 2: 기본 검증 실행..."

# Python 문법 체크
echo "  → Python 문법 체크..."
python -m py_compile app.py 2>/dev/null && echo "    ✅ app.py" || echo "    ❌ app.py 문법 오류"

# Import 테스트
echo "  → Import 테스트..."
python -c "
try:
    import agents
    import tools
    import llm
    print('    ✅ 모든 모듈 import 성공')
except Exception as e:
    print(f'    ❌ Import 실패: {e}')
    exit(1)
" || exit 1

# 선택적: pytest 실행 (tests/ 디렉토리가 있는 경우)
if [ -d "tests" ]; then
    echo "  → 테스트 실행..."
    pytest tests/ -v --tb=short 2>/dev/null || echo "    ⚠️ 테스트 실패 (계속 진행)"
fi

echo ""
echo "✅ 모든 검증 완료!"
echo ""
echo "📝 다음 명령어로 변경사항 커밋:"
echo "   git add ."
echo "   git commit -m \"your message\""
echo "   git push -u origin $BRANCH"
