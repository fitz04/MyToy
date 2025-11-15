# Gradio 마이그레이션 가이드 - 완벽한 대안

## 📋 개요

현재 Chainlit의 한계:
- ❌ 버튼이 채팅 메시지에 붙어있어 스크롤 시 접근 불가
- ❌ 고정된 사이드바나 툴바 부재
- ❌ 복잡한 레이아웃 커스터마이징 제한

**Gradio로 마이그레이션하면 얻는 이점:**
- ✅ 완전히 고정된 UI 컴포넌트 (사이드바, 버튼 패널 등)
- ✅ 자유로운 레이아웃 커스터마이징 (Blocks API)
- ✅ 더 풍부한 UI 컴포넌트 (탭, 아코디언, 데이터프레임 등)
- ✅ 스트리밍 채팅 지원
- ✅ HuggingFace Spaces에 무료 배포

---

## 🎯 마이그레이션 전략

### Phase 1: Gradio 앱 프로토타입 (2-3시간)
기본 채팅 + 고정 버튼 패널 구현

### Phase 2: 전체 기능 이식 (1-2일)
모든 Phase 2, 3 도구들을 Gradio UI로 이식

### Phase 3: UI 개선 및 배포 (1일)
레이아웃 최적화, 스타일링, HuggingFace Spaces 배포

---

## 💻 Gradio 앱 구조

### 1. 기본 레이아웃

```python
import gradio as gr
from agents import CodingAgent
from llm import LLMManager

# Global instances
agent = None
llm_manager = None

def create_ui():
    """Gradio UI 생성"""

    with gr.Blocks(theme=gr.themes.Soft(), title="AI Coding Agent") as app:

        # 상단: 프로젝트 설정
        with gr.Row():
            project_path = gr.Textbox(
                label="📁 프로젝트 경로",
                value=".",
                scale=3
            )
            auto_analyze = gr.Checkbox(label="🔍 자동 분석", value=True)
            load_btn = gr.Button("🚀 프로젝트 로드", variant="primary")

        # 메인 영역: 채팅 + 사이드바
        with gr.Row():
            # 왼쪽: 채팅 영역 (70%)
            with gr.Column(scale=7):
                chatbot = gr.Chatbot(
                    label="💬 대화",
                    height=600,
                    show_label=False,
                    bubble_full_width=False
                )

                with gr.Row():
                    msg = gr.Textbox(
                        label="메시지",
                        placeholder="무엇을 도와드릴까요?",
                        scale=9,
                        show_label=False
                    )
                    submit_btn = gr.Button("전송", scale=1, variant="primary")

            # 오른쪽: 고정 버튼 패널 (30%)
            with gr.Column(scale=3):
                gr.Markdown("## 🔧 도구")

                # Phase 2 도구들
                with gr.Accordion("🧪 테스트 & 품질", open=True):
                    test_btn = gr.Button("🧪 테스트 실행", size="sm")
                    quality_btn = gr.Button("🔍 코드 품질 검사", size="sm")
                    review_btn = gr.Button("📝 코드 리뷰", size="sm")

                # 프로젝트 관리
                with gr.Accordion("📊 프로젝트", open=False):
                    analyze_btn = gr.Button("📊 프로젝트 분석", size="sm")
                    save_session_btn = gr.Button("💾 세션 저장", size="sm")
                    create_project_btn = gr.Button("🏗️ 프로젝트 생성", size="sm")

                # 문서 & RAG
                with gr.Accordion("📚 문서 & RAG", open=False):
                    upload_docs_btn = gr.Button("📤 문서 업로드", size="sm")
                    rag_stats_btn = gr.Button("📈 RAG 통계", size="sm")

                # 설정
                with gr.Accordion("⚙️ 설정", open=False):
                    llm_dropdown = gr.Dropdown(
                        choices=["claude", "openai", "groq", "deepinfra"],
                        value="claude",
                        label="LLM 선택"
                    )
                    clear_btn = gr.Button("🗑️ 대화 초기화", size="sm")

        # 하단: 상태 표시
        status = gr.Textbox(label="상태", interactive=False, show_label=False)

        # 이벤트 핸들러 연결
        submit_btn.click(
            fn=chat,
            inputs=[msg, chatbot],
            outputs=[msg, chatbot, status]
        )

        test_btn.click(
            fn=run_tests,
            outputs=[chatbot, status]
        )

        quality_btn.click(
            fn=check_quality,
            outputs=[chatbot, status]
        )

        # ... 나머지 버튼 핸들러

    return app

# 이벤트 핸들러 함수들
async def chat(message, history):
    """채팅 메시지 처리"""
    global agent

    if not agent:
        return "", history + [("에러", "Agent not initialized")], "❌ 에이전트 초기화 필요"

    # 에이전트 응답 스트리밍
    response = ""
    async for chunk in agent.process_message(message, stream=True):
        response += chunk

    history.append((message, response))
    return "", history, "✅ 응답 완료"

async def run_tests():
    """테스트 실행"""
    from tools import TestRunner
    runner = TestRunner()
    result = await runner.run_tests()

    # 결과 포매팅
    msg = f"🧪 테스트 결과: {result['passed']}/{result['total']} 통과"

    return [(None, msg)], "✅ 테스트 완료"

async def check_quality():
    """코드 품질 검사"""
    from tools import CodeQuality
    checker = CodeQuality()
    result = await checker.check_all()

    msg = f"🔍 품질 검사 완료\n{result}"

    return [(None, msg)], "✅ 검사 완료"

# 앱 실행
if __name__ == "__main__":
    app = create_ui()
    app.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False
    )
```

---

## 🎨 고급 기능

### 1. 파일 업로드 UI (코드 리뷰용)

```python
with gr.Accordion("📝 코드 리뷰", open=False):
    file_upload = gr.File(
        label="Python 파일 선택",
        file_types=[".py"],
        type="filepath"
    )
    review_btn = gr.Button("📝 리뷰 시작")
    review_output = gr.Markdown(label="리뷰 결과")

review_btn.click(
    fn=review_code,
    inputs=[file_upload],
    outputs=[review_output]
)

async def review_code(file_path):
    """코드 리뷰"""
    from agents import CodeReviewer

    reviewer = CodeReviewer(llm_manager)
    with open(file_path, 'r') as f:
        code = f.read()

    review = await reviewer.review_code(file_path, code)

    # 마크다운 포맷팅
    result = f"""# 📝 코드 리뷰 결과

**파일**: `{file_path}`
**점수**: {review['score']}/10

## 강점
{review['strengths']}

## 개선점
{review['weaknesses']}

## 코멘트
{review['comments']}
"""
    return result
```

### 2. 프로젝트 템플릿 생성 UI

```python
with gr.Accordion("🏗️ 프로젝트 생성", open=False):
    template_radio = gr.Radio(
        choices=["FastAPI", "Flask", "CLI", "Library"],
        label="템플릿 선택",
        value="FastAPI"
    )
    project_name = gr.Textbox(label="프로젝트 이름", placeholder="my-project")
    output_dir = gr.Textbox(label="출력 디렉토리", value="./projects")
    create_btn = gr.Button("🏗️ 생성", variant="primary")
    create_output = gr.Markdown()

create_btn.click(
    fn=create_project,
    inputs=[template_radio, project_name, output_dir],
    outputs=[create_output]
)

async def create_project(template, name, output):
    """프로젝트 생성"""
    from tools import ProjectTemplates

    templates = ProjectTemplates()
    result = await templates.create_project(
        template.lower(),
        name,
        output
    )

    return f"✅ 프로젝트 생성 완료!\n\n경로: `{result['path']}`"
```

### 3. 세션 관리 UI

```python
with gr.Accordion("💾 세션 관리", open=False):
    sessions_dropdown = gr.Dropdown(
        label="저장된 세션",
        choices=[],
        interactive=True
    )
    refresh_sessions_btn = gr.Button("🔄 새로고침", size="sm")
    load_session_btn = gr.Button("📂 세션 로드", size="sm")
    save_session_btn = gr.Button("💾 세션 저장", size="sm")

refresh_sessions_btn.click(
    fn=get_sessions,
    outputs=[sessions_dropdown]
)

def get_sessions():
    """세션 목록 조회"""
    sessions = session_manager.list_sessions()
    return gr.Dropdown(choices=sessions)
```

---

## 📊 Chainlit vs Gradio 비교

| 기능 | Chainlit | Gradio |
|------|----------|--------|
| **고정 UI** | ❌ 메시지 내 버튼만 | ✅ 완전히 고정 가능 |
| **레이아웃 자유도** | ⚠️ 제한적 | ✅ Blocks로 자유롭게 |
| **채팅 스트리밍** | ✅ 내장 | ✅ 지원 |
| **파일 업로드** | ✅ AskFileMessage | ✅ File 컴포넌트 |
| **UI 복잡도** | 🟢 간단 | 🟡 중간 |
| **커스터마이징** | 🔴 제한적 | 🟢 매우 자유로움 |
| **배포** | ⚠️ 직접 호스팅 | ✅ HF Spaces 무료 |
| **학습 곡선** | 🟢 낮음 | 🟡 중간 |
| **개발 속도** | 🟢 빠름 | 🟡 보통 |

---

## 🚀 마이그레이션 체크리스트

### 준비 단계
- [ ] Gradio 설치: `pip install gradio`
- [ ] 기본 레이아웃 프로토타입 작성 (`app_gradio.py`)
- [ ] 채팅 기능 테스트

### 핵심 기능 이식
- [ ] CodingAgent 통합
- [ ] LLMManager 통합
- [ ] SessionManager 통합
- [ ] 채팅 스트리밍 구현

### Phase 2 도구 통합
- [ ] 테스트 실행 버튼 + UI
- [ ] 코드 품질 검사 (5가지 옵션)
- [ ] 코드 리뷰 (파일 업로드 UI)
- [ ] 프로젝트 생성 (템플릿 선택 UI)

### Phase 3 기능 통합
- [ ] 프로젝트 로딩
- [ ] 세션 관리 UI
- [ ] RAG 문서 업로드
- [ ] RAG 통계 표시

### UI/UX 개선
- [ ] 테마 커스터마이징
- [ ] 반응형 레이아웃
- [ ] 에러 핸들링 UI
- [ ] 로딩 상태 표시

### 배포
- [ ] HuggingFace Spaces 설정
- [ ] 환경 변수 관리 (Secrets)
- [ ] README 작성
- [ ] 배포 및 테스트

---

## 💡 마이그레이션 팁

### 1. 점진적 마이그레이션
Chainlit과 Gradio를 병행 운영:
```bash
# Chainlit 버전
chainlit run app.py -w

# Gradio 버전
python app_gradio.py
```

### 2. 공통 코드 재사용
에이전트, 도구, LLM 로직은 그대로 재사용:
```
project/
├── agents/         # 공통 사용
├── tools/          # 공통 사용
├── llm/            # 공통 사용
├── app.py          # Chainlit UI
└── app_gradio.py   # Gradio UI
```

### 3. 설정 파일 통합
`.env`와 `config.py`는 양쪽에서 동일하게 사용

---

## 🎯 예상 소요 시간

| 단계 | 시간 | 난이도 |
|------|------|--------|
| Gradio 프로토타입 | 2-3시간 | 🟢 쉬움 |
| 핵심 기능 이식 | 4-6시간 | 🟡 보통 |
| Phase 2 도구 통합 | 4-6시간 | 🟡 보통 |
| Phase 3 기능 통합 | 2-4시간 | 🟢 쉬움 |
| UI/UX 개선 | 4-6시간 | 🟡 보통 |
| **총 예상 시간** | **16-25시간** | **🟡 보통** |

---

## 📚 참고 자료

- [Gradio 공식 문서](https://www.gradio.app/docs/)
- [Gradio Blocks 가이드](https://www.gradio.app/guides/blocks-and-event-listeners)
- [Gradio Chatbot 예제](https://www.gradio.app/guides/creating-a-chatbot-fast)
- [HuggingFace Spaces 배포](https://huggingface.co/docs/hub/spaces-overview)

---

## 🤔 언제 마이그레이션할까?

### 지금 당장 마이그레이션하는 것이 좋은 경우:
- ✅ 고정 버튼 패널이 필수적인 경우
- ✅ 복잡한 레이아웃이 필요한 경우
- ✅ HuggingFace Spaces에 배포하고 싶은 경우
- ✅ 시간 투자 가능 (2-3일)

### Chainlit을 계속 사용하는 것이 좋은 경우:
- ✅ 현재 하이브리드 방식으로 충분한 경우
- ✅ 빠른 프로토타이핑이 우선인 경우
- ✅ 마이그레이션 시간이 부족한 경우
- ✅ 채팅 중심 UI가 주요 목적인 경우

---

## ✨ 결론

**현재 상황**: Chainlit + 하이브리드 버튼 시스템으로 실용적인 해결책 구현 완료

**향후 계획**:
1. 현재 시스템으로 개발 진행
2. UI 한계가 명확해지면 Gradio로 마이그레이션
3. 이 가이드를 따라 2-3일 내 완료 가능

**추천**:
- 지금은 Chainlit으로 기능 개발에 집중
- Phase 4-5 완성 후 Gradio 마이그레이션 검토
- 사용자 피드백 수집 후 결정
