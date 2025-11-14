"""간단한 독립 테스트 - 의존성 최소화"""
import asyncio
import sys
from pathlib import Path

print("🧪 Phase 1 기능 간단 테스트\n")

# Test 1: 파일 쓰기 모듈 직접 테스트
print("="*60)
print("Test 1: 파일 쓰기 기능")
print("="*60)

sys.path.insert(0, str(Path(__file__).parent))

try:
    from tools.file_operations import FileOperations

    async def test_file_ops():
        file_ops = FileOperations(backup_dir="test_backup")

        # 1. 파일 쓰기
        print("\n1. write_file() 테스트...")
        result = await file_ops.write_file(
            "test_hello.py",
            "print('Hello, World!')\n"
        )
        print(f"   결과: {result}")

        # 2. 파일 읽기
        print("\n2. read_file() 테스트...")
        result = await file_ops.read_file("test_hello.py")
        print(f"   성공: {result['success']}")
        print(f"   내용: {result.get('content', 'N/A')[:50]}")

        # 3. 파일 편집
        print("\n3. edit_file() 테스트...")
        result = await file_ops.edit_file(
            "test_hello.py",
            "World",
            "AI Agent"
        )
        print(f"   성공: {result['success']}")
        if result['success']:
            print(f"   Diff 생성됨: {len(result.get('diff', ''))} chars")

        # 4. 코드 삽입
        print("\n4. insert_code() 테스트...")
        result = await file_ops.insert_code(
            "test_hello.py",
            0,
            "# -*- coding: utf-8 -*-\n"
        )
        print(f"   성공: {result['success']}")

        # 5. 최종 파일 읽기
        print("\n5. 최종 파일 내용:")
        result = await file_ops.read_file("test_hello.py")
        if result['success']:
            print(result['content'])

        # 6. 백업 목록
        print("\n6. 백업 목록:")
        backups = await file_ops.list_backups("test_hello.py")
        print(f"   총 {len(backups)}개 백업")
        for b in backups:
            print(f"   - {b['timestamp']}")

        print("\n✅ 파일 쓰기 기능 테스트 완료!")
        return True

    asyncio.run(test_file_ops())

except Exception as e:
    print(f"❌ 에러: {e}")
    import traceback
    traceback.print_exc()

# Test 2: Git 통합 테스트
print("\n" + "="*60)
print("Test 2: Git 통합 기능")
print("="*60)

try:
    from tools.git_operations import GitOperations

    async def test_git_ops():
        git_ops = GitOperations()

        # 1. Git 상태
        print("\n1. git_status() 테스트...")
        result = await git_ops.git_status()
        print(f"   성공: {result['success']}")
        if result['success']:
            print(f"   브랜치: {result['current_branch']}")
            print(f"   요약: {result['summary']}")
            print(f"   더티: {result['is_dirty']}")

        # 2. 커밋 이력
        print("\n2. get_commit_history() 테스트...")
        result = await git_ops.get_commit_history(max_count=3)
        print(f"   성공: {result['success']}")
        if result['success']:
            print(f"   커밋 수: {result['count']}")
            for commit in result['commits']:
                print(f"   - {commit['hash']}: {commit['message'][:40]}")

        print("\n✅ Git 통합 기능 테스트 완료!")
        return True

    asyncio.run(test_git_ops())

except Exception as e:
    print(f"❌ 에러: {e}")
    import traceback
    traceback.print_exc()

# Test 3: TODO 시스템 테스트
print("\n" + "="*60)
print("Test 3: TODO 계획 시스템")
print("="*60)

try:
    from agents.planner import TaskPlanner, TaskStatus

    async def test_planner_sys():
        planner = TaskPlanner()

        # 1. 계획 생성
        print("\n1. create_plan() 테스트...")
        plan = planner.create_plan(
            "test_plan",
            "테스트 작업",
            [
                {"id": "task1", "description": "작업 1"},
                {"id": "task2", "description": "작업 2", "dependencies": ["task1"]},
                {"id": "task3", "description": "작업 3", "dependencies": ["task2"]}
            ]
        )
        print(f"   계획 ID: {plan.id}")
        print(f"   작업 수: {len(plan.tasks)}")

        # 2. 진행 상황
        print("\n2. get_progress() 테스트...")
        progress = plan.get_progress()
        print(f"   총 작업: {progress['total']}")
        print(f"   완료: {progress['completed']}")
        print(f"   진행률: {progress['percentage']}%")

        # 3. 마크다운 출력
        print("\n3. to_markdown() 테스트...")
        markdown = plan.to_markdown()
        print(markdown)

        # 4. 다음 작업 가져오기
        print("\n4. get_next_task() 테스트...")
        next_task = plan.get_next_task()
        if next_task:
            print(f"   다음 작업: {next_task.description}")
            next_task.status = TaskStatus.COMPLETED
            print(f"   작업 완료 처리")

        # 5. 진행 상황 업데이트
        print("\n5. 진행률 업데이트...")
        progress = plan.get_progress()
        print(f"   진행률: {progress['percentage']}%")
        progress_bar = planner.format_progress_bar(plan, width=40)
        print(f"   {progress_bar}")

        print("\n✅ TODO 계획 시스템 테스트 완료!")
        return True

    asyncio.run(test_planner_sys())

except Exception as e:
    print(f"❌ 에러: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "🎉"*30)
print("테스트 완료!")
print("🎉"*30)
