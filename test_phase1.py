"""Phase 1 기능 테스트 스크립트"""
import asyncio
import sys
from pathlib import Path

# 프로젝트 루트를 Python path에 추가
sys.path.insert(0, str(Path(__file__).parent))

from tools import file_ops, git_ops
from agents import planner, TaskStatus


async def test_file_operations():
    """파일 쓰기 기능 테스트"""
    print("\n" + "="*60)
    print("🧪 Test 1: 파일 쓰기 기능")
    print("="*60)

    # 테스트 디렉토리 생성
    test_dir = Path("test_output")
    test_dir.mkdir(exist_ok=True)

    # 1. 파일 생성 테스트
    print("\n1️⃣ write_file() 테스트...")
    result = await file_ops.write_file(
        file_path="test_output/hello.py",
        content="print('Hello, World!')\n"
    )

    if result["success"]:
        print(f"   ✅ 파일 생성 성공: {result['file_path']}")
        print(f"   📝 작업: {result['operation']}")
        print(f"   📊 크기: {result['size']} bytes, {result['lines']} lines")
    else:
        print(f"   ❌ 실패: {result['error']}")
        return False

    # 2. 파일 읽기 테스트
    print("\n2️⃣ read_file() 테스트...")
    result = await file_ops.read_file("test_output/hello.py")

    if result["success"]:
        print(f"   ✅ 파일 읽기 성공")
        print(f"   📄 내용:\n{result['content']}")
    else:
        print(f"   ❌ 실패: {result['error']}")
        return False

    # 3. 파일 편집 테스트
    print("\n3️⃣ edit_file() 테스트...")
    result = await file_ops.edit_file(
        file_path="test_output/hello.py",
        old_content="print('Hello, World!')",
        new_content="print('Hello, AI Agent!')"
    )

    if result["success"]:
        print(f"   ✅ 파일 편집 성공")
        print(f"   📊 변경: {result['changes']['lines_before']} → {result['changes']['lines_after']} lines")
        print(f"   💾 백업: {result['backup_path']}")
        print(f"\n   📋 Diff:")
        print("   " + "\n   ".join(result['diff'].split('\n')[:10]))
    else:
        print(f"   ❌ 실패: {result['error']}")
        return False

    # 4. 코드 삽입 테스트
    print("\n4️⃣ insert_code() 테스트...")
    result = await file_ops.insert_code(
        file_path="test_output/hello.py",
        line_number=0,
        code="# -*- coding: utf-8 -*-\n"
    )

    if result["success"]:
        print(f"   ✅ 코드 삽입 성공")
        print(f"   📍 삽입 위치: line {result['inserted_at_line']}")
    else:
        print(f"   ❌ 실패: {result['error']}")
        return False

    # 5. 최종 파일 확인
    print("\n5️⃣ 최종 파일 확인...")
    result = await file_ops.read_file("test_output/hello.py")
    print(f"   📄 최종 내용:\n{result['content']}")

    # 6. 백업 목록 조회
    print("\n6️⃣ 백업 목록 조회...")
    backups = await file_ops.list_backups("test_output/hello.py")
    print(f"   💾 백업 개수: {len(backups)}")
    for backup in backups[:3]:
        print(f"   - {backup['timestamp']}: {backup['backup_path']}")

    print("\n✅ 파일 쓰기 기능 테스트 통과!")
    return True


async def test_git_operations():
    """Git 통합 기능 테스트"""
    print("\n" + "="*60)
    print("🧪 Test 2: Git 통합 기능")
    print("="*60)

    # 1. Git 상태 확인
    print("\n1️⃣ git_status() 테스트...")
    result = await git_ops.git_status()

    if result["success"]:
        print(f"   ✅ Git 상태 조회 성공")
        print(f"   🌿 현재 브랜치: {result['current_branch']}")
        print(f"   📊 요약: {result['summary']}")
        print(f"   📝 수정된 파일: {len(result['modified_files'])}개")
        print(f"   📂 추적되지 않은 파일: {len(result['untracked_files'])}개")

        if result['untracked_files']:
            print(f"\n   추적되지 않은 파일:")
            for f in result['untracked_files'][:5]:
                print(f"   - {f}")
    else:
        print(f"   ❌ 실패: {result['error']}")
        return False

    # 2. Git diff 확인 (수정된 파일이 있다면)
    if result['modified_files']:
        print("\n2️⃣ git_diff() 테스트...")
        diff_result = await git_ops.git_diff(file_path=result['modified_files'][0])

        if diff_result["success"]:
            print(f"   ✅ Diff 조회 성공")
            print(f"   📋 변경된 파일 수: {diff_result['files_changed']}")
        else:
            print(f"   ❌ 실패: {diff_result['error']}")

    # 3. 커밋 이력 조회
    print("\n3️⃣ get_commit_history() 테스트...")
    result = await git_ops.get_commit_history(max_count=3)

    if result["success"]:
        print(f"   ✅ 커밋 이력 조회 성공")
        print(f"   📚 조회된 커밋: {result['count']}개\n")

        for commit in result['commits']:
            print(f"   🔖 {commit['hash']} - {commit['message'][:50]}...")
            print(f"      👤 {commit['author']}")
            print(f"      📅 {commit['date'][:19]}")
            print()
    else:
        print(f"   ❌ 실패: {result['error']}")
        return False

    print("✅ Git 통합 기능 테스트 통과!")
    return True


async def test_planner():
    """TODO 계획 시스템 테스트"""
    print("\n" + "="*60)
    print("🧪 Test 3: TODO 계획 시스템")
    print("="*60)

    # 1. 계획 생성
    print("\n1️⃣ 계획 생성 테스트...")
    plan = planner.create_plan(
        plan_id="test_plan",
        description="테스트 기능 구현",
        tasks=[
            {
                "id": "analyze",
                "description": "요구사항 분석",
                "dependencies": []
            },
            {
                "id": "design",
                "description": "설계 작성",
                "dependencies": ["analyze"]
            },
            {
                "id": "implement",
                "description": "코드 구현",
                "dependencies": ["design"]
            },
            {
                "id": "test",
                "description": "테스트 실행",
                "dependencies": ["implement"]
            }
        ]
    )

    print(f"   ✅ 계획 생성 성공")
    print(f"   📋 계획 ID: {plan.id}")
    print(f"   📊 작업 수: {len(plan.tasks)}개")

    # 2. 진행 상황 확인
    print("\n2️⃣ 진행 상황 확인...")
    progress = plan.get_progress()
    print(f"   📊 진행률: {progress['percentage']:.1f}%")
    print(f"   ✅ 완료: {progress['completed']}/{progress['total']}")
    print(f"   🔄 진행 중: {progress['in_progress']}")
    print(f"   ⏳ 대기: {progress['pending']}")

    # 3. 마크다운 출력
    print("\n3️⃣ 마크다운 출력...")
    markdown = plan.to_markdown()
    print(markdown)

    # 4. 작업 실행 시뮬레이션
    print("\n4️⃣ 작업 실행 시뮬레이션...")

    async def mock_executor(task):
        """모의 작업 실행"""
        await asyncio.sleep(0.5)  # 작업 시간 시뮬레이션
        return {"status": "success", "message": f"{task.description} 완료"}

    # 작업 하나씩 실행
    for i in range(len(plan.tasks)):
        task = plan.get_next_task()
        if not task:
            break

        print(f"\n   🔄 실행 중: {task.description}")
        task.status = TaskStatus.IN_PROGRESS

        result = await planner.execute_task(task, mock_executor)

        if result["success"]:
            print(f"   ✅ 완료: {task.description}")

        # 진행 상황 업데이트
        progress = plan.get_progress()
        progress_bar = planner.format_progress_bar(plan, width=40)
        print(f"   {progress_bar}")

    # 5. 최종 결과
    print("\n5️⃣ 최종 결과...")
    final_progress = plan.get_progress()
    print(f"   🎉 모든 작업 완료: {final_progress['is_complete']}")
    print(f"   📊 완료율: {final_progress['percentage']:.1f}%")

    # 최종 마크다운
    print("\n6️⃣ 최종 계획 상태...")
    print(plan.to_markdown())

    print("\n✅ TODO 계획 시스템 테스트 통과!")
    return True


async def test_integration():
    """통합 테스트: 전체 워크플로우"""
    print("\n" + "="*60)
    print("🧪 Test 4: 통합 테스트 - 전체 워크플로우")
    print("="*60)

    # 시나리오: 간단한 Python 모듈 생성
    print("\n📝 시나리오: math_utils.py 모듈 생성 및 커밋")

    # 1. 계획 생성
    print("\n1️⃣ 계획 수립...")
    plan = planner.create_plan(
        plan_id="create_module",
        description="math_utils 모듈 생성",
        tasks=[
            {"id": "create", "description": "모듈 파일 생성"},
            {"id": "verify", "description": "파일 확인"},
            {"id": "status", "description": "Git 상태 확인"}
        ]
    )

    # 2. 파일 생성
    print("\n2️⃣ 모듈 파일 생성...")
    task1 = plan.get_task("create")
    task1.status = TaskStatus.IN_PROGRESS

    module_code = '''"""간단한 수학 유틸리티 모듈"""

def add(a: int, b: int) -> int:
    """두 수를 더합니다."""
    return a + b

def multiply(a: int, b: int) -> int:
    """두 수를 곱합니다."""
    return a * b

def is_even(n: int) -> bool:
    """짝수인지 확인합니다."""
    return n % 2 == 0
'''

    result = await file_ops.write_file(
        file_path="test_output/math_utils.py",
        content=module_code
    )

    if result["success"]:
        task1.status = TaskStatus.COMPLETED
        print(f"   ✅ 파일 생성: {result['file_path']}")
    else:
        print(f"   ❌ 실패: {result['error']}")
        return False

    # 3. 파일 확인
    print("\n3️⃣ 생성된 파일 확인...")
    task2 = plan.get_task("verify")
    task2.status = TaskStatus.IN_PROGRESS

    result = await file_ops.read_file("test_output/math_utils.py")

    if result["success"]:
        task2.status = TaskStatus.COMPLETED
        print(f"   ✅ 파일 읽기 성공")
        print(f"   📊 크기: {result['size']} bytes")
        print(f"   📝 라인 수: {result['lines']}")
        print(f"\n   내용 미리보기:")
        lines = result['content'].split('\n')[:5]
        for line in lines:
            print(f"   {line}")
    else:
        print(f"   ❌ 실패: {result['error']}")
        return False

    # 4. Git 상태 확인
    print("\n4️⃣ Git 상태 확인...")
    task3 = plan.get_task("status")
    task3.status = TaskStatus.IN_PROGRESS

    result = await git_ops.git_status()

    if result["success"]:
        task3.status = TaskStatus.COMPLETED
        print(f"   ✅ Git 상태 조회 성공")
        print(f"   📊 {result['summary']}")
    else:
        print(f"   ❌ 실패: {result['error']}")
        return False

    # 5. 최종 계획 상태
    print("\n5️⃣ 계획 완료 상태...")
    print(plan.to_markdown())

    progress = plan.get_progress()
    if progress['is_complete']:
        print("\n🎉 통합 테스트 성공!")
        return True
    else:
        print(f"\n⚠️ 일부 작업 미완료: {progress['pending']} pending")
        return False


async def main():
    """모든 테스트 실행"""
    print("\n" + "🚀 "*30)
    print("Phase 1 기능 테스트 시작")
    print("🚀 "*30)

    results = {
        "file_operations": False,
        "git_operations": False,
        "planner": False,
        "integration": False
    }

    try:
        # Test 1: 파일 쓰기
        results["file_operations"] = await test_file_operations()

        # Test 2: Git 통합
        results["git_operations"] = await test_git_operations()

        # Test 3: TODO 시스템
        results["planner"] = await test_planner()

        # Test 4: 통합 테스트
        results["integration"] = await test_integration()

    except Exception as e:
        print(f"\n❌ 예외 발생: {e}")
        import traceback
        traceback.print_exc()

    # 최종 결과
    print("\n" + "="*60)
    print("📊 최종 테스트 결과")
    print("="*60)

    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")

    total = len(results)
    passed = sum(results.values())
    print(f"\n총 {passed}/{total} 테스트 통과 ({passed/total*100:.1f}%)")

    if all(results.values()):
        print("\n🎉 모든 테스트 통과! Phase 1 기능이 정상 작동합니다!")
    else:
        print("\n⚠️ 일부 테스트 실패. 로그를 확인하세요.")


if __name__ == "__main__":
    asyncio.run(main())
