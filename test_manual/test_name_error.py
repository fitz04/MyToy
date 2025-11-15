"""NameError 테스트 케이스

변수가 정의되지 않아 NameError가 발생하는 코드입니다.
AutoErrorFixer가 자동으로 변수를 정의해야 합니다.
"""

# calculate_total 함수에 매개변수 price와 quantity 추가
def calculate_total(price, quantity):  # 변경사항: 함수 매개변수 추가
    result = price * quantity
    return result

# 함수 호출 시, price와 quantity 값 전달
total = calculate_total(100, 2)  # 변경사항: 함수 호출 시 인자 제공
print(f"Total: {total}")