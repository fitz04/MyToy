"""NameError 테스트 케이스

변수가 정의되지 않아 NameError가 발생하는 코드입니다.
AutoErrorFixer가 자동으로 변수를 정의해야 합니다.
"""

def calculate_total():
    result = price * quantity  # price, quantity 미정의
    return result

total = calculate_total()
print(f"Total: {total}")
