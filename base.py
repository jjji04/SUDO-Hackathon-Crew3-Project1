import streamlit as st
import google.generativeai as genai
import time
import key  # key.py 파일에 GEMINI_API_KEY 변수가 있어야 합니다.

# ==========================================
# [담당 1(박진영): 총괄/QA] GEMINI 클라이언트 설정
# 미션: 에러 메시지를 "⚠️ API 키가 없어요! key.py를 확인해주세요."로 수정완료
# ==========================================
try:
    genai.configure(api_key=key.GEMINI_API_KEY)
except Exception as e:
    st.error("⚠️ API 키가 없어요! key.py를 확인해주세요.")

# ==========================================
# [담당 2(이민근): 프론트엔드1] 앱 디자인 및 레이아웃
# 미션: 이름 입력 칸 추가 및 맞춤형 환영 인사말을 추가해주세요.
# ==========================================
st.set_page_config(page_title="업무 비서 AI", page_icon="💼")
st.title("💼 스마트 일정 관리 비서")
st.caption("업무 일정 정리와 할 일 목록 작성을 도와드립니다.")

# ==========================================
# [담당 3(김재범): 프롬프트 엔지니어] 비서 페르소나 설정
# 미션: 답변 끝에 항상 응원문구 붙이도록 수정, 일정을 입력하면 무조건 표로 정리해주게 수정해주세요.
# ==========================================
SYSTEM_PROMPT = {
    "role": "system", 
    "content": (
        "너는 유능한 일정 관리 비서야. 항상 정중하고 명확하게 답변해."
    )
}

# ==========================================
# [담당 4(김민주): 데이터 엔지니어] 세션 및 기록 관리
# 미션: 사이드바에 st.sidebar.info("대화 기록이 안전하게 보관 중입니다.") 한 줄을 추가해주세요.
# ==========================================
if "messages" not in st.session_state:
    st.session_state.messages = [SYSTEM_PROMPT]

if st.sidebar.button("🧹 대화 기록 초기화"):
    st.session_state.messages = [SYSTEM_PROMPT]
    st.rerun()

# ==========================================
# [담당 5(박진영): 프론트엔드2] 메시지 렌더링
# 미션: 사용자(else 부분)의 avatar 아이콘을 "👤"에서 "👨‍💻"로 수정완료
# ==========================================
for message in st.session_state.messages:
    if message["role"] != "system":
        avatar = "🤖" if message["role"] == "assistant" else "👨‍💻"
        with st.chat_message(message["role"], avatar=avatar):
            st.markdown(message["content"])

# ==========================================
# [담당 6(황정원): 백엔드] API 호출 및 답변 생성 엔진
# 미션: 타이핑 효과 로직을 추가완료
# [담당 5(박진영): 프론트엔드2]: 사용자의 avatar 아이콘을 "👤"에서 "👨‍💻"로 수정완료
# ==========================================
if prompt := st.chat_input("오늘의 일정을 알려주세요."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="👨‍💻"):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar="🤖"):
        try:
            with st.spinner("생각 중..."):
                system_content = next(
                    (m["content"] for m in st.session_state.messages if m["role"] == "system"), None
                )
                history = [
                    {"role": "user" if m["role"] == "user" else "model", "parts": [m["content"]]}
                    for m in st.session_state.messages
                    if m["role"] in ("user", "assistant") and m["content"] != prompt
                ]
                model = genai.GenerativeModel("gemini-2.5-flash-lite", system_instruction=system_content)
                chat = model.start_chat(history=history)
                response = chat.send_message(prompt).text

            # ✅ 타이핑 효과 추가
            placeholder = st.empty()
            displayed = ""
            for char in response:
                displayed += char
                placeholder.markdown(displayed)
                time.sleep(0.02)  # 속도 조절

            st.session_state.messages.append({"role": "assistant", "content": response})

        except Exception as e:
            st.error(f"서버 연결 오류: {e}")