"""
패키지 설치 확인
"""

print("패키지 설치 확인")
print("=" * 40)

packages = [
    "pandas",
    "pykrx",
    "dotenv",
    "gspread",
    "google.auth",
    "requests",
    "numpy"
]

for package in packages:
    try:
        if package == "google.auth":
            import google.auth
        else:
            __import__(package)
        print(f"✅ {package} 설치됨")
    except ImportError:
        print(f"❌ {package} 없음 → pip install {package}")

print("\n" + "=" * 40)
print("모두 ✅이면 성공!")
print("❌가 있으면 해당 패키지 설치 필요")