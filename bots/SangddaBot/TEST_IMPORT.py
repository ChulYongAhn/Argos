"""
Import 테스트 - Starter.py 패키지 확인
"""

print("패키지 import 테스트")
print("=" * 40)

# 1. pykrx 테스트
try:
    from pykrx import stock
    print("✅ pykrx import 성공")
except ImportError as e:
    print(f"❌ pykrx import 실패: {e}")

# 2. pandas 테스트
try:
    import pandas as pd
    print("✅ pandas import 성공")
except ImportError as e:
    print(f"❌ pandas import 실패: {e}")

# 3. dotenv 테스트
try:
    from dotenv import load_dotenv
    print("✅ dotenv import 성공")
except ImportError as e:
    print(f"❌ dotenv import 실패: {e}")

# 4. SimpleGoogleSheetService 테스트
try:
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    from services.SimpleGoogleSheetService import Send
    print("✅ SimpleGoogleSheetService import 성공")
except ImportError as e:
    print(f"❌ SimpleGoogleSheetService import 실패: {e}")

print("\n" + "=" * 40)
print("모두 ✅이면 정상입니다!")