"""
VSCode F5 실행 환경 체크
"""
import os
import sys

print("=" * 50)
print("🔍 실행 환경 정보")
print("=" * 50)

print(f"\n1. 현재 작업 디렉토리:")
print(f"   {os.getcwd()}")

print(f"\n2. 이 파일의 위치:")
print(f"   {os.path.abspath(__file__)}")

print(f"\n3. Python 실행 파일:")
print(f"   {sys.executable}")

print(f"\n4. .env 파일 찾기:")
# 현재 디렉토리에서
env1 = os.path.join(os.getcwd(), '.env')
print(f"   현재 디렉토리: {env1}")
print(f"   → 존재: {os.path.exists(env1)}")

# 프로젝트 루트에서
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
env2 = os.path.join(project_root, '.env')
print(f"   프로젝트 루트: {env2}")
print(f"   → 존재: {os.path.exists(env2)}")

print(f"\n5. GOOGLE_SHEET_ID 환경변수:")
print(f"   {os.getenv('GOOGLE_SHEET_ID', '없음')}")

# .env 수동 로드 후
from dotenv import load_dotenv
load_dotenv(env2)
print(f"\n6. .env 로드 후 GOOGLE_SHEET_ID:")
print(f"   {os.getenv('GOOGLE_SHEET_ID', '없음')}")

print("\n" + "=" * 50)
print("이 정보를 스크린샷으로 보내주세요!")
print("=" * 50)