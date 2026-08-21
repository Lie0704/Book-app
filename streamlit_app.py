from datetime import date, timedelta
from html import escape

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
    :root { --ink: #3a2c25; --forest: #3f6653; --rust: #b85b3e; --gold: #d69b42; --paper: #fffaf0; }
    .stApp { background: linear-gradient(135deg, #f3dfc3 0%, #fffaf0 48%, #dce8d9 100%); color: var(--ink); }
    h1, h2, h3 { font-family: 'Jua', sans-serif !important; letter-spacing: 0 !important; color: var(--ink); }
    p, label, input, textarea, button, [data-testid='stMarkdownContainer'] { font-family: 'Gowun Dodum', sans-serif; }
    .hero { position: relative; min-height: 235px; overflow: hidden; padding: 2.2rem 2.2rem 1.8rem; border-bottom: 1px solid #d9cdbb; background: linear-gradient(180deg, rgba(255,250,240,.3), rgba(231,193,137,.25)); }
    .hero-copy { position: relative; z-index: 2; max-width: 58%; }
    .hero-art { position: absolute; right: 4%; bottom: 0; width: 360px; height: 220px; }
    .hill { position: absolute; right: -10%; bottom: -76px; width: 520px; height: 170px; border-radius: 50% 50% 0 0; background: #b6c49b; transform: rotate(-3deg); }
    .trunk { position: absolute; right: 42%; bottom: 30px; width: 25px; height: 125px; border-radius: 12px 12px 3px 3px; background: #79503a; transform: rotate(3deg); }
    .trunk:after { content: ''; position: absolute; left: -44px; top: 45px; width: 66px; height: 13px; border-radius: 50%; background: #79503a; transform: rotate(-35deg); }
    .canopy { position: absolute; right: 22%; bottom: 112px; width: 145px; height: 112px; border-radius: 52% 48% 45% 55%; background: #b84e32; box-shadow: -57px 25px 0 #d27a35, 48px 24px 0 #c76132, 3px -35px 0 #d99a3c; }
    .leaf { position: absolute; width: 13px; height: 22px; border-radius: 90% 10% 90% 10%; background: #b84e32; transform: rotate(35deg); }
    .leaf.one { right: 6%; top: 35px; } .leaf.two { right: 31%; top: 15px; background: #d99a3c; transform: rotate(90deg); }
    .leaf.three { right: 12%; top: 122px; background: #d27a35; transform: rotate(5deg); }
    .leaf.four { right: 49%; top: 82px; background: #e2ac49; transform: rotate(-35deg); }
    .picnic-book { position: absolute; right: 7%; bottom: 18px; width: 74px; height: 48px; border-radius: 3px 7px 7px 3px; background: #f6e8c8; border: 5px solid #6b4a3b; transform: rotate(-8deg); box-shadow: 8px 7px 0 rgba(107,74,59,.18); }
    .picnic-book:after { content: 'BOOK'; position: absolute; top: 11px; left: 12px; color: #b85b3e; font: 11px 'Jua', sans-serif; }
    .eyebrow { color: var(--rust); font-weight: 700; letter-spacing: .08em; }
    .hero h1 { font-size: clamp(2.2rem, 5vw, 4.2rem) !important; margin: .15rem 0 .4rem; }
    .hero p { font-size: 1.12rem; margin: 0; }
    .section-label { color: var(--forest); font-size: 1.45rem; font-weight: 700; margin: 1rem 0 .4rem; }
    .info-strip { background: rgba(255,250,240,.8); border-left: 4px solid var(--rust); padding: .9rem 1.1rem; margin: 1rem 0; }
    .slot { background: rgba(255,250,240,.85); border: 1px solid #d9cdbb; padding: .7rem 1rem; margin: .45rem 0; }
    .slot strong { color: var(--forest); }
    .calendar { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: .7rem; margin-top: .8rem; }
    .calendar-day { min-height: 115px; background: rgba(255,250,240,.82); border: 1px solid #d9cdbb; border-radius: 6px; padding: .75rem; }
    .calendar-day.booked { border: 2px solid var(--rust); box-shadow: 0 4px 14px rgba(111, 70, 43, .1); }
    .calendar-date { font-family: 'Jua', sans-serif; font-size: 1.15rem; color: var(--rust); }
    .calendar-meta { margin-top: .45rem; font-size: .82rem; line-height: 1.55; }
    div.stButton > button, div[data-testid='stFormSubmitButton'] button { border-radius: 6px; background: var(--forest); color: white; border: 0; }
    @media (max-width: 700px) { .calendar { grid-template-columns: repeat(2, minmax(0, 1fr)); } }
    @media (max-width: 700px) { .hero-copy { max-width: 100%; } .hero-art { right: -105px; opacity: .46; transform: scale(.82); transform-origin: bottom right; } }
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


def calendar_markup():
    day_names = "월화수목금토일"
    cells = []
    for calendar_date in event_dates():
        class_items = [
            item
            for period in CLASS_PERIODS
            for item in st.session_state.class_reservations.get(reservation_key(calendar_date, period), [])
        ]
        after_items = st.session_state.after_school_reservations.get(
            reservation_key(calendar_date, AFTER_SCHOOL_PERIOD), []
        )
        people = [f'{item["teacher"]} 선생님 · {item["classroom"]}' for item in class_items]
        people.extend(item["team"] for item in after_items)
        details = "<br>".join(escape(person) for person in people)
        status = f"수업 {len(class_items)}건 · 방과후 {len(after_items)}팀"
        cells.append(
            f'<div class="calendar-day {"booked" if people else ""}">'
            f'<div class="calendar-date">{calendar_date.month}/{calendar_date.day} ({day_names[calendar_date.weekday()]})</div>'
            f'<div class="calendar-meta">{escape(status)}'
            f'{"<br>" + details if details else "<br>예약 없음"}</div></div>'
        )
    return '<div class="calendar">' + "".join(cells) + "</div>"


if "class_reservations" not in st.session_state:
    st.session_state.class_reservations = {}
if "after_school_reservations" not in st.session_state:
    st.session_state.after_school_reservations = {}

st.markdown(
    """
    <div class="hero">
        <div class="hero-copy">
            <div class="eyebrow">LIBRARY BOOK PICNIC · 2026</div>
            <h1>도서관 북크닉</h1>
            <p>책 한 권과 함께, 도서관에서 보내는 작은 소풍</p>
        </div>
        <div class="hero-art" aria-hidden="true">
            <div class="hill"></div>
            <div class="trunk"></div>
            <div class="canopy"></div>
            <div class="leaf one"></div><div class="leaf two"></div>
            <div class="leaf three"></div><div class="leaf four"></div>
            <div class="picnic-book"></div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown('<div class="info-strip">📅 행사 기간 <b>9월 14일(월) ~ 9월 21일(월)</b> · 먼저 예약 종류를 선택한 뒤 날짜와 시간을 입력해 주세요.</div>', unsafe_allow_html=True)

class_tab, after_tab = st.tabs(["🏫 수업시간 예약", "🌿 방과후 예약"])

with class_tab:
    st.markdown('<div class="section-label">🏫 수업시간 예약</div>', unsafe_allow_html=True)
    st.caption("한 교시당 최대 2개 반, 총 60명까지 신청할 수 있습니다. 같은 날 여러 교시 신청도 가능합니다.")
    selected_date = st.date_input("수업 방문 날짜", value=EVENT_START, min_value=EVENT_START, max_value=EVENT_END, format="YYYY-MM-DD", key="class_date")
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

with after_tab:
    st.markdown('<div class="section-label">🌿 방과후 예약</div>', unsafe_allow_html=True)
    st.caption("방과후 1교시는 한 팀당 2~4명이 함께 신청할 수 있습니다.")
    selected_date = st.date_input("방과후 방문 날짜", value=EVENT_START, min_value=EVENT_START, max_value=EVENT_END, format="YYYY-MM-DD", key="after_date")
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
st.markdown('<div class="section-label">🍂 예약 달력</div>', unsafe_allow_html=True)
st.caption("예약이 있는 날짜는 테두리로 표시됩니다. 날짜 아래에서 예약한 선생님, 학급 또는 방과후 대표자를 확인할 수 있습니다.")
st.markdown(calendar_markup(), unsafe_allow_html=True)
st.divider()
st.caption("예약 정보는 현재 브라우저 세션에 임시로 저장됩니다.")
