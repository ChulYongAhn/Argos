"""
VSCode F5 실행 환경 체크
"""
import sys
import os

print("=" * 50)
print("Python 실행 환경 정보")
print("=" * 50)

print(f"\n1. Python 실행 파일: {sys.executable}")
print(f"2. Python 버전: {sys.version}")
print(f"3. 현재 작업 디렉토리: {os.getcwd()}")
print(f"4. 스크립트 위치: {os.path.abspath(__file__)}")

print(f"\n5. Python 경로 (sys.path):")
for i, path in enumerate(sys.path):
    print(f"   {i}: {path}")

print(f"\n6. 환경 변수 확인:")
print(f"   PYTHONPATH: {os.environ.get('PYTHONPATH', '설정 안됨')}")

print(f"\n7. gspread 모듈 확인:")
try:
    import gspread
    print(f"   ✅ gspread 설치됨: {gspread.__file__}")
except ImportError as e:
    print(f"   ❌ gspread 없음: {e}")

print(f"\n8. dotenv 모듈 확인:")
try:
    from dotenv import load_dotenv
    import dotenv
    print(f"   ✅ python-dotenv 설치됨: {dotenv.__file__}")
except ImportError as e:
    print(f"   ❌ python-dotenv 없음: {e}")

print(f"\n9. .env 파일 확인:")
env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), '.env')
print(f"   경로: {env_path}")
print(f"   존재: {os.path.exists(env_path)}")

print("\n" + "=" * 50)
print("F5를 눌러서 이 스크립트를 실행해보세요!")
print("=" * 50)