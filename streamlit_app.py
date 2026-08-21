from datetime import date, timedelta

import streamlit as st


st.set_page_config(
    page_title="도서관 북크닉 예약",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Gowun+Dodum&family=Jua&display=swap');
    :root { --ink: #253238; --teal: #167d72; --coral: #e8755f; --paper: #fffdf8; }
    .stApp { background: linear-gradient(135deg, #f5eee2 0%, #fffdf8 48%, #e2f0eb 100%); color: var(--ink); }
    h1, h2, h3 { font-family: 'Jua', sans-serif !important; letter-spacing: 0 !important; color: var(--ink); }
    p, label, input, textarea, button, [data-testid='stMarkdownContainer'] { font-family: 'Gowun Dodum', sans-serif; }
    .hero { padding: 2rem 2.2rem 1.6rem; border-bottom: 1px solid #d9ded9; }
    .eyebrow { color: var(--coral); font-weight: 700; letter-spacing: .08em; }
    .hero h1 { font-size: clamp(2.2rem, 5vw, 4.2rem) !important; margin: .15rem 0 .4rem; }
    .hero p { font-size: 1.12rem; margin: 0; }
    .section-label { color: var(--teal); font-size: 1.45rem; font-weight: 700; margin: 1rem 0 .4rem; }
    .info-strip { background: rgba(255,253,248,.75); border-left: 4px solid var(--coral); padding: .9rem 1.1rem; margin: 1rem 0; }
    .slot { background: rgba(255,253,248,.85); border: 1px solid #d9ded9; padding: .7rem 1rem; margin: .45rem 0; }
    .slot strong { color: var(--teal); }
    div.stButton > button, div[data-testid='stFormSubmitButton'] button { border-radius: 6px; background: var(--teal); color: white; border: 0; }
    </style>
    """,
    unsafe_allow_html=True,
)


EVENT_START = date(2026, 9, 14)
EVENT_END = date(2026, 9, 21)
CLASS_PERIODS = [f"{period}교시" for period in range(1, 8)]
AFTER_SCHOOL_PERIOD = "방과후 1교시"
ALL_PERIODS = CLASS_PERIODS + [AFTER_SCHOOL_PERIOD]


def event_dates():
    return [EVENT_START + timedelta(days=offset) for offset in range((EVENT_END - EVENT_START).days + 1)]


def reservation_key(selected_date, period):
    return f"{selected_date.isoformat()}::{period}"


if "class_reservations" not in st.session_state:
    st.session_state.class_reservations = {}
if "after_school_reservations" not in st.session_state:
    st.session_state.after_school_reservations = {}

st.markdown(
    """
    <div class="hero">
        <div class="eyebrow">LIBRARY BOOK PICNIC · 2026</div>
        <h1>도서관 북크닉</h1>
        <p>책 한 권과 함께, 도서관에서 보내는 작은 소풍</p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown('<div class="info-strip">📅 행사 기간 <b>9월 14일(월) ~ 9월 21일(월)</b> · 원하는 날짜를 고른 뒤 수업 또는 방과후 시간을 예약해 주세요.</div>', unsafe_allow_html=True)

selected_date = st.date_input(
    "방문 날짜",
    value=EVENT_START,
    min_value=EVENT_START,
    max_value=EVENT_END,
    format="YYYY-MM-DD",
)
date_label = f"{selected_date.month}월 {selected_date.day}일 ({'월화수목금토일'[selected_date.weekday()]})"
st.subheader(f"{date_label} 예약 현황")

left, right = st.columns(2, gap="large")

with left:
    st.markdown('<div class="section-label">🏫 수업시간 예약</div>', unsafe_allow_html=True)
    st.caption("한 교시당 최대 2개 반, 총 60명까지 신청할 수 있습니다. 같은 날 여러 교시 신청도 가능합니다.")
    class_period = st.selectbox("수업 교시", CLASS_PERIODS, key="class_period")
    class_key = reservation_key(selected_date, class_period)
    class_items = st.session_state.class_reservations.get(class_key, [])
    class_count = sum(item["students"] for item in class_items)
    st.progress(min(class_count / 60, 1.0), text=f"{len(class_items)}개 반 · {class_count}/60명")

    with st.form("class_reservation_form", clear_on_submit=True):
        teacher = st.text_input("선생님 이름", placeholder="예: 김도서")
        classroom = st.text_input("학급", placeholder="예: 5학년 2반")
        subject = st.text_input("수업", placeholder="예: 국어")
        students = st.number_input("참여 인원", min_value=1, max_value=60, value=30, step=1)
        class_submitted = st.form_submit_button("수업 예약 추가", use_container_width=True)

    if class_submitted:
        if not all((teacher.strip(), classroom.strip(), subject.strip())):
            st.error("선생님 이름, 학급, 수업을 모두 입력해 주세요.")
        elif len(class_items) >= 2:
            st.error("이 교시는 이미 2개 반이 예약되었습니다.")
        elif class_count + students > 60:
            st.error(f"현재 잔여 인원은 {60 - class_count}명입니다.")
        else:
            st.session_state.class_reservations.setdefault(class_key, []).append(
                {"teacher": teacher.strip(), "classroom": classroom.strip(), "subject": subject.strip(), "students": students}
            )
            st.success("수업 예약이 추가되었습니다.")
            st.rerun()

    if class_items:
        st.markdown("**신청된 반**")
        for item in class_items:
            st.markdown(f'<div class="slot"><strong>{item["classroom"]}</strong> · {item["teacher"]} 선생님 · {item["subject"]} · {item["students"]}명</div>', unsafe_allow_html=True)
    else:
        st.caption("아직 신청된 반이 없습니다.")

with right:
    st.markdown('<div class="section-label">🌿 방과후 예약</div>', unsafe_allow_html=True)
    st.caption("방과후 1교시는 한 팀당 2~4명이 함께 신청할 수 있습니다.")
    after_key = reservation_key(selected_date, AFTER_SCHOOL_PERIOD)
    after_items = st.session_state.after_school_reservations.get(after_key, [])
    st.markdown(f"**현재 신청 팀** {len(after_items)}팀", unsafe_allow_html=False)

    with st.form("after_school_form", clear_on_submit=True):
        team_name = st.text_input("대표자 이름", placeholder="예: 이책벌")
        participant_count = st.number_input("참여 인원", min_value=2, max_value=4, value=2, step=1)
        participant_names = st.text_area("참여자 이름", placeholder="이름을 쉼표로 구분해 입력해 주세요", height=100)
        after_submitted = st.form_submit_button("방과후 예약 추가", use_container_width=True)

    if after_submitted:
        names = [name.strip() for name in participant_names.split(",") if name.strip()]
        if not team_name.strip():
            st.error("대표자 이름을 입력해 주세요.")
        elif len(names) != participant_count:
            st.error(f"참여자 이름을 {participant_count}명 입력해 주세요.")
        else:
            st.session_state.after_school_reservations.setdefault(after_key, []).append(
                {"team": team_name.strip(), "names": names}
            )
            st.success("방과후 예약이 추가되었습니다.")
            st.rerun()

    if after_items:
        st.markdown("**신청된 팀**")
        for item in after_items:
            st.markdown(f'<div class="slot"><strong>{item["team"]}</strong> · {len(item["names"])}명 · {", ".join(item["names"])}</div>', unsafe_allow_html=True)
    else:
        st.caption("아직 신청된 팀이 없습니다.")

st.divider()
st.caption("예약 정보는 현재 브라우저 세션에 임시로 저장됩니다.")
