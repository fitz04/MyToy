"""Phase 2 수동 테스트 러너

실제 LLM을 사용하여 AutoErrorFixer를 테스트합니다.
"""

import asyncio
import sys
from pathlib import Path

# 프로젝트 루트를 Python path에 추가
sys.path.insert(0, str(Path(__file__).parent))

print("="*70)
print("🧪 Phase 2 수동 테스트 - AutoErrorFixer")
print("="*70)


async def test_name_error():
    """NameError 자동 수정 테스트"""
    print("\n📋 Test: NameError 자동 수정")
    print("-"*70)

    try:
        from agents import AutoErrorFixer
        from llm import LLMManager
        from tools import FileOperations
    except ImportError as e:
        print(f"❌ Import 실패: {e}")
        print("   의존성이 설치되지 않았을 수 있습니다.")
        return False

    # 테스트 파일 경로
    test_file = "test_manual/test_name_error.py"

    # 파일 읽기
    try:
        with open(test_file, 'r') as f:
            code = f.read()
        print(f"✅ 테스트 파일 로드: {test_file}")
    except FileNotFoundError:
        print(f"❌ 테스트 파일을 찾을 수 없습니다: {test_file}")
        return False

    # 코드 출력
    print(f"\n📄 테스트 코드:")
    print("-"*70)
    for i, line in enumerate(code.split('\n')[:15], 1):
        print(f"{i:3d}: {line}")
    print("-"*70)

    # AutoErrorFixer 초기화
    try:
        print("\n🔧 AutoErrorFixer 초기화 중...")
        llm = LLMManager()
        file_ops = FileOperations()
        fixer = AutoErrorFixer(llm, file_ops, max_retries=2)
        print("✅ 초기화 완료")
    except Exception as e:
        print(f"❌ 초기화 실패: {e}")
        return False

    # 코드 실행하여 에러 발생시키기
    print("\n🚀 코드 실행 중...")
    try:
        exec(code)
        print("✅ 코드가 에러 없이 실행되었습니다 (예상치 못한 결과)")
        return True
    except NameError as e:
        print(f"❌ NameError 발생: {e}")
        print("\n🔧 자동 수정 시작...\n")

        # 자동 수정 실행
        try:
            result = await fixer.auto_fix(
                error=e,
                code=code,
                file_path=test_file,
                executor=None  # 검증 생략
            )

            # 결과 출력
            print("\n" + "="*70)
            print("📊 테스트 결과")
            print("="*70)

            if result["success"]:
                print(f"✅ 자동 수정 성공!")
                print(f"   시도 횟수: {result['attempts']}")
                print(f"   파일: {result['file_path']}")

                if result.get('cause'):
                    print(f"\n📍 원인 분석:")
                    print(f"   {result['cause'][:200]}...")

                if result.get('method'):
                    print(f"\n🔧 수정 방법:")
                    print(f"   {result['method'][:200]}...")

                # 수정된 코드 미리보기
                if result.get('fixed_code'):
                    print(f"\n📄 수정된 코드 (처음 10줄):")
                    print("-"*70)
                    for i, line in enumerate(result['fixed_code'].split('\n')[:10], 1):
                        print(f"{i:3d}: {line}")
                    print("-"*70)

                return True
            else:
                print(f"❌ 자동 수정 실패")
                print(f"   시도 횟수: {result['attempts']}")
                if result.get('last_error'):
                    print(f"   마지막 에러: {result['last_error']}")
                return False

        except Exception as e:
            print(f"\n❌ 예외 발생: {e}")
            import traceback
            traceback.print_exc()
            return False
    except Exception as e:
        print(f"❌ 예상치 못한 에러: {type(e).__name__}: {e}")
        return False


async def main():
    """메인 함수"""
    print("\n시작 시간:", __import__('datetime').datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print()

    # 환경 확인
    print("🔍 환경 확인")
    print("-"*70)
    print(f"Python: {sys.version.split()[0]}")
    print(f"작업 디렉토리: {Path.cwd()}")

    # API 키 확인
    import os
    anthropic_key = os.getenv("ANTHROPIC_API_KEY")
    openai_key = os.getenv("OPENAI_API_KEY")

    if anthropic_key:
        print(f"✅ ANTHROPIC_API_KEY: {anthropic_key[:10]}...")
    else:
        print("⚠️  ANTHROPIC_API_KEY: 설정되지 않음")

    if openai_key:
        print(f"✅ OPENAI_API_KEY: {openai_key[:10]}...")
    else:
        print("⚠️  OPENAI_API_KEY: 설정되지 않음")

    if not (anthropic_key or openai_key):
        print("\n❌ API 키가 설정되지 않았습니다!")
        print("   .env 파일을 확인하세요.")
        return False

    print()

    # 테스트 실행
    try:
        result = await test_name_error()

        print("\n" + "="*70)
        if result:
            print("🎉 테스트 성공!")
        else:
            print("❌ 테스트 실패")
        print("="*70)

        return result

    except KeyboardInterrupt:
        print("\n\n⚠️  사용자가 테스트를 중단했습니다.")
        return False
    except Exception as e:
        print(f"\n\n❌ 예외 발생: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ 실행 실패: {e}")
        exit(1)
