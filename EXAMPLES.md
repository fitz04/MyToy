# 💡 사용 예제

이 문서는 AI Coding Assistant를 효과적으로 사용하는 다양한 예제를 제공합니다.

## 📋 목차
1. [기본 사용법](#기본-사용법)
2. [코드 리뷰](#코드-리뷰)
3. [디버깅](#디버깅)
4. [코드 설명](#코드-설명)
5. [리팩토링](#리팩토링)
6. [웹 검색 활용](#웹-검색-활용)
7. [RAG 활용](#rag-활용)
8. [LLM 전환](#llm-전환)

---

## 기본 사용법

### 간단한 코드 작성 요청
```
사용자: Python에서 리스트를 역순으로 정렬하는 함수를 작성해줘
```

### 프로젝트 분석
```
사용자: /analyze
```
프로젝트의 전체 구조와 통계를 확인할 수 있습니다.

---

## 코드 리뷰

### Python 코드 리뷰
```
사용자: 이 코드를 리뷰해주고 개선점을 제안해줘:

def calculate_total(items):
    total = 0
    for item in items:
        total = total + item['price'] * item['quantity']
    return total
```

**AI 응답 예시:**
- 변수명이 명확함
- list comprehension 사용 가능
- 타입 힌팅 추가 권장
- 에러 처리 필요

### JavaScript 코드 리뷰
```
사용자: 이 React 컴포넌트를 리뷰해줘:

function UserList({ users }) {
    return (
        <div>
            {users.map(user => (
                <div>{user.name}</div>
            ))}
        </div>
    );
}
```

---

## 디버깅

### TypeError 디버깅
```
사용자: 이 코드에서 TypeError가 발생해. 도와줘:

def process_data(data):
    result = []
    for item in data:
        result.append(item.upper())
    return result

# 에러: TypeError: 'NoneType' object is not iterable
```

### 논리 오류 찾기
```
사용자: 이 함수가 예상대로 동작하지 않아:

def is_palindrome(text):
    return text == text[::-1]

# "A man a plan a canal Panama"가 False를 반환함
```

---

## 코드 설명

### 복잡한 알고리즘 설명
```
사용자: 이 퀵소트 구현을 단계별로 설명해줘:

def quicksort(arr):
    if len(arr) <= 1:
        return arr
    pivot = arr[len(arr) // 2]
    left = [x for x in arr if x < pivot]
    middle = [x for x in arr if x == pivot]
    right = [x for x in arr if x > pivot]
    return quicksort(left) + middle + quicksort(right)
```

### 라이브러리 사용법 설명
```
사용자: Python의 asyncio가 어떻게 작동하는지 간단한 예제와 함께 설명해줘
```

---

## 리팩토링

### 코드 개선
```
사용자: 이 코드를 더 파이썬스럽게 리팩토링해줘:

def get_even_numbers(numbers):
    result = []
    for num in numbers:
        if num % 2 == 0:
            result.append(num)
    return result
```

### 성능 최적화
```
사용자: 이 함수의 성능을 개선해줘:

def find_duplicates(lst):
    duplicates = []
    for i in range(len(lst)):
        for j in range(i+1, len(lst)):
            if lst[i] == lst[j] and lst[i] not in duplicates:
                duplicates.append(lst[i])
    return duplicates
```

---

## 웹 검색 활용

### 공식 문서 검색
```
사용자: /search FastAPI middleware documentation
```

### 최신 라이브러리 정보
```
사용자: React 18의 새로운 기능에 대한 문서를 검색해줘
```

### 에러 해결법 검색
```
사용자: "ModuleNotFoundError: No module named 'sklearn'" 에러 해결법을 검색해줘
```

---

## RAG 활용

### 프로젝트 문서 업로드
```
사용자: /upload
```
프로젝트의 API 문서, 설계 문서 등을 업로드합니다.

### 업로드된 문서 기반 질문
```
사용자: 우리 프로젝트의 인증 시스템은 어떻게 구현되어 있어?
```

### RAG 통계 확인
```
사용자: /stats
```

### 문서 삭제
```
사용자: /clear-docs
```

---

## LLM 전환

### Claude로 전환 (복잡한 분석)
```
사용자: /switch claude
사용자: 이 대규모 코드베이스의 아키텍처를 분석하고 개선점을 제안해줘
```

### Groq로 전환 (빠른 응답)
```
사용자: /switch groq
사용자: 간단한 TODO 앱을 만들어줘
```

### OpenAI로 전환 (범용)
```
사용자: /switch openai
사용자: 데이터베이스 설계를 도와줘
```

### DeepInfra로 전환 (비용 절감)
```
사용자: /switch deepinfra
사용자: 여러 개의 유닛 테스트를 작성해줘
```

---

## 고급 활용 예제

### 1. 전체 프로젝트 분석 및 리팩토링
```
사용자: /analyze
사용자: 프로젝트 구조를 분석한 결과를 바탕으로 개선할 점을 제안해줘
```

### 2. 문서 기반 코드 생성
```
사용자: /upload  (API 문서 업로드)
사용자: 업로드한 API 문서에 맞춰 클라이언트 코드를 작성해줘
```

### 3. 웹 검색 + 코드 생성
```
사용자: Stripe API의 최신 결제 구현 방법을 검색하고, 샘플 코드를 작성해줘
```

### 4. 멀티스텝 디버깅
```
사용자: /switch claude  (복잡한 분석을 위해)
사용자: 이 에러를 분석해줘: [에러 로그]
사용자: 제안한 해결책을 적용한 코드를 작성해줘
사용자: /switch groq  (빠른 테스트를 위해)
사용자: 수정한 코드가 제대로 작동하는지 간단히 검증해줘
```

### 5. 코드 리뷰 + 테스트 작성
```
사용자: 이 함수를 리뷰해줘: [코드]
사용자: 리뷰 결과를 반영해서 개선된 코드를 작성해줘
사용자: 개선된 코드에 대한 유닛 테스트를 작성해줘
```

---

## 팁과 트릭

### 1. 컨텍스트 제공
더 나은 답변을 위해 충분한 컨텍스트를 제공하세요:
```
❌ 나쁜 예: "이 코드 고쳐줘"
✅ 좋은 예: "Python Flask 앱에서 JWT 인증이 실패해. 다음은 관련 코드야: [코드]"
```

### 2. 단계별 접근
복잡한 작업은 단계별로 나눠서 요청하세요:
```
1. 먼저 프로젝트 분석
2. 문제 진단
3. 해결책 제안
4. 코드 작성
5. 테스트
```

### 3. LLM 선택 가이드
- **복잡한 아키텍처 설계**: Claude
- **빠른 코드 스니펫**: Groq
- **일반적인 코딩 작업**: OpenAI
- **대량 작업 (테스트 생성 등)**: DeepInfra

### 4. RAG 효과적으로 사용
- 프로젝트 시작 시 주요 문서를 미리 업로드
- 팀 코딩 컨벤션 문서 업로드
- API 스펙 문서 업로드
- 정기적으로 `/stats`로 확인

### 5. 명령어 조합
```
# 프로젝트 분석 → 웹 검색 → RAG 활용
/analyze
/search best practices for Python async
[프로젝트 문서 기반 질문]
```

---

## 실전 시나리오

### 시나리오 1: 새 기능 구현
```
1. /analyze  # 프로젝트 이해
2. /search [관련 라이브러리] documentation  # 최신 정보 확인
3. "이 기능을 구현해줘: [요구사항]"  # 코드 생성
4. "작성한 코드를 리뷰해줘"  # 코드 리뷰
5. "유닛 테스트를 작성해줘"  # 테스트 생성
```

### 시나리오 2: 버그 수정
```
1. "이 에러를 분석해줘: [에러 로그]"
2. /search [에러 메시지]  # 유사 사례 검색
3. "문제를 해결하는 코드를 작성해줘"
4. "수정 사항을 설명해줘"
```

### 시나리오 3: 코드 학습
```
1. "이 코드를 설명해줘: [복잡한 코드]"
2. "더 간단한 버전을 작성해줘"
3. "각 단계를 주석으로 설명해줘"
4. "이 패턴의 장단점은 뭐야?"
```

---

더 많은 예제와 팁이 필요하면 `/help` 명령을 사용하거나 자유롭게 질문하세요!
