#!/bin/bash
# 올인원 동기화 스크립트: pull → test → (optional) push

set -e

BRANCH="claude/coding-agent-deepagent-chainlit-016coptmPhZ2EACt5fLgedUV"

echo "═══════════════════════════════════════"
echo "  🔄 Git 동기화 시작"
echo "═══════════════════════════════════════"
echo ""

# 로컬 변경사항 확인
if [[ -n $(git status --porcelain) ]]; then
    echo "⚠️  로컬에 커밋되지 않은 변경사항이 있습니다:"
    git status --short
    echo ""
    read -p "계속하시겠습니까? (y/N): " confirm
    if [[ ! "$confirm" =~ ^[Yy]$ ]]; then
        echo "취소되었습니다."
        exit 0
    fi
    echo ""
fi

echo "📥 Step 1: 원격 변경사항 가져오기..."
git fetch origin $BRANCH
git pull origin $BRANCH
echo "  ✅ Pull 완료"

echo ""
echo "🧪 Step 2: 자동 검증..."

# Python 문법 체크
echo "  → Python 주요 파일 문법 체크..."
MAIN_FILES="app.py"
for file in $MAIN_FILES; do
    if [ -f "$file" ]; then
        python -m py_compile "$file" 2>/dev/null && echo "    ✅ $file" || {
            echo "    ❌ $file 문법 오류!"
            exit 1
        }
    fi
done

# Import 테스트
echo "  → 모듈 Import 테스트..."
python -c "
try:
    import agents
    import tools
    import llm
    import config
    print('    ✅ 모든 모듈 import 성공')
except Exception as e:
    print(f'    ❌ Import 실패: {e}')
    exit(1)
" || exit 1

# requirements 체크 (선택적)
echo "  → 의존성 체크..."
python -c "
import pkg_resources
import sys

try:
    with open('requirements-core.txt') as f:
        requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]

    missing = []
    for req in requirements:
        # requirements에서 버전 제약 제거
        pkg_name = req.split('>=')[0].split('==')[0].split('<')[0].strip()
        try:
            pkg_resources.require(pkg_name)
        except:
            missing.append(pkg_name)

    if missing:
        print(f'    ⚠️  누락된 패키지: {', '.join(missing)}')
        print(f'       설치: pip install -r requirements-core.txt')
    else:
        print('    ✅ 모든 핵심 의존성 설치됨')
except Exception as e:
    print(f'    ⚠️  의존성 체크 실패: {e}')
"

echo ""
echo "✅ 모든 검증 완료!"
echo ""

# 로컬 변경사항이 있으면 푸시 옵션 제공
if [[ -n $(git status --porcelain) ]]; then
    echo "═══════════════════════════════════════"
    echo ""
    read -p "로컬 변경사항을 커밋하고 푸시하시겠습니까? (y/N): " push_confirm
    if [[ "$push_confirm" =~ ^[Yy]$ ]]; then
        echo ""
        read -p "커밋 메시지를 입력하세요: " commit_msg
        if [ -n "$commit_msg" ]; then
            ./push.sh "$commit_msg"
        else
            echo "❌ 커밋 메시지가 필요합니다."
        fi
    fi
else
    echo "📝 현재 커밋할 변경사항이 없습니다."
fi

echo ""
echo "═══════════════════════════════════════"
echo "  ✅ 동기화 완료!"
echo "═══════════════════════════════════════"
