"""
Import 디버그 테스트
"""
import sys
import os

print("=" * 50)
print("Import 디버그")
print("=" * 50)

print(f"\n1. 현재 디렉토리: {os.getcwd()}")
print(f"2. 스크립트 디렉토리: {os.path.dirname(os.path.abspath(__file__))}")

# sys.path에 현재 스크립트 디렉토리 추가
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, script_dir)

print(f"\n3. sys.path 첫 번째 항목: {sys.path[0]}")

print("\n4. simple_google_sheet 모듈 import 시도:")
try:
    from simple_google_sheet import Send
    print("   ✅ import 성공!")
    print(f"   Send 함수: {Send}")

    # Send 함수 테스트
    print("\n5. Send 함수 테스트:")
    result = Send("상한가", "DEBUG_TEST", "테스트", "성공")
    print(f"   결과: {result}")

except ImportError as e:
    print(f"   ❌ import 실패: {e}")

    # 파일 존재 확인
    print("\n   파일 확인:")
    simple_path = os.path.join(script_dir, "simple_google_sheet.py")
    print(f"   simple_google_sheet.py 경로: {simple_path}")
    print(f"   파일 존재: {os.path.exists(simple_path)}")

except Exception as e:
    print(f"   ❌ 기타 에러: {type(e).__name__}: {e}")

print("\n" + "=" * 50)