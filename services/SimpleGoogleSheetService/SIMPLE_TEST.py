"""
가장 간단한 테스트
"""
print("Python 작동 확인: OK")

try:
    import gspread
    print("gspread 설치 확인: OK")
except:
    print("gspread 설치 안됨: 에러")

try:
    from simple_google_sheet import Send
    print("Send 함수 import: OK")
except Exception as e:
    print(f"Send 함수 import 실패: {e}")

print("\n위 3개가 모두 OK면 정상입니다.")