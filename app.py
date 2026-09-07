"""
할 일(To-Do) 관리 단일 페이지 Streamlit 애플리케이션
프로젝트 규칙(AGENTS.md) 준수:
- 타입 힌트 명시
- 단일 책임을 가진 독립된 함수 구성
- UI와 비즈니스 로직 분리
- 세션 상태(st.session_state)만을 활용한 상태 관리
- 모든 주석 및 UI 텍스트 한국어 표기
- 상단 상수 정의
- UI Rules: 필터/검색 위젯은 st.sidebar 에 배치
- UI Rules: 목록 항목에 상태 아이콘 표시 (완료 ✅ / 미완료 ⬜)
"""

import time
import uuid
from typing import TypedDict
import streamlit as st

# ==========================================
# 상수 정의 (Constants)
# ==========================================
PAGE_TITLE: str = "스마트 할 일 관리 (To-Do)"
PAGE_ICON: str = "📝"
SESSION_KEY_TODOS: str = "todo_items"
SESSION_KEY_FILTER: str = "current_filter"
SESSION_KEY_SEARCH: str = "search_keyword"

# 상태 아이콘 상수 (AGENTS.md 규칙)
ICON_COMPLETED: str = "✅"
ICON_INCOMPLETE: str = "⬜"

# 필터 옵션 상수
FILTER_ALL: str = "전체"
FILTER_ACTIVE: str = "미완료"
FILTER_COMPLETED: str = "완료"
FILTER_OPTIONS: tuple[str, ...] = (FILTER_ALL, FILTER_ACTIVE, FILTER_COMPLETED)

# 안내 및 에러 메시지 상수
MSG_EMPTY_INPUT: str = "할 일 내용을 입력해 주세요."
MSG_ADD_SUCCESS: str = "새로운 할 일이 추가되었습니다."
MSG_NO_TODOS: str = "등록된 할 일이 없습니다. 새로운 할 일을 추가해 보세요!"
MSG_NO_FILTERED_TODOS: str = "해당 조건의 할 일이 없습니다."
INPUT_PLACEHOLDER: str = "새로운 할 일을 입력하고 Enter를 누르세요..."
SEARCH_PLACEHOLDER: str = "할 일 검색어 입력..."


# ==========================================
# 데이터 모델 정의 (Data Models)
# ==========================================
class TodoItem(TypedDict):
    """할 일 아이템 구조를 정의하는 TypedDict"""
    id: str
    title: str
    completed: bool
    created_at: str


# ==========================================
# 비즈니스 로직 함수 (Business Logic)
# ==========================================
def init_session_state() -> None:
    """세션 상태 초기화 함수: 할 일 목록과 필터/검색 상태를 준비합니다."""
    if SESSION_KEY_TODOS not in st.session_state:
        st.session_state[SESSION_KEY_TODOS] = [
            {
                "id": "sample-1",
                "title": "Streamlit 앱 기획 및 설계",
                "completed": True,
                "created_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            },
            {
                "id": "sample-2",
                "title": "할 일 관리 및 사이드바 기능 구현",
                "completed": False,
                "created_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            },
        ]
    if SESSION_KEY_FILTER not in st.session_state:
        st.session_state[SESSION_KEY_FILTER] = FILTER_ALL
    if SESSION_KEY_SEARCH not in st.session_state:
        st.session_state[SESSION_KEY_SEARCH] = ""



def get_all_todos() -> list[TodoItem]:
    """현재 세션에 저장된 모든 할 일 목록을 반환합니다."""
    return st.session_state.get(SESSION_KEY_TODOS, [])


def add_todo(title: str) -> bool:
    """
    새로운 할 일을 목록에 추가합니다.
    공백을 제외한 유효한 문자열인지 검증합니다.
    """
    stripped_title: str = title.strip()
    if not stripped_title:
        return False

    new_item: TodoItem = {
        "id": str(uuid.uuid4()),
        "title": stripped_title,
        "completed": False,
        "created_at": time.strftime("%Y-%m-%d %H:%M:%S"),
    }
    st.session_state[SESSION_KEY_TODOS].append(new_item)
    return True


def toggle_todo(todo_id: str) -> None:
    """지정된 ID의 할 일 완료 상태를 반전(토글)합니다."""
    todos: list[TodoItem] = st.session_state.get(SESSION_KEY_TODOS, [])
    for item in todos:
        if item["id"] == todo_id:
            item["completed"] = not item["completed"]
            break


def delete_todo(todo_id: str) -> None:
    """지정된 ID의 할 일을 목록에서 삭제합니다."""
    todos: list[TodoItem] = st.session_state.get(SESSION_KEY_TODOS, [])
    st.session_state[SESSION_KEY_TODOS] = [item for item in todos if item["id"] != todo_id]


def calculate_summary(todos: list[TodoItem]) -> dict[str, int]:
    """전체, 완료, 미완료 개수를 계산하여 딕셔너리로 반환합니다."""
    total_count: int = len(todos)
    completed_count: int = sum(1 for item in todos if item["completed"])
    active_count: int = total_count - completed_count
    return {
        "total": total_count,
        "completed": completed_count,
        "active": active_count,
    }


def filter_todos(
    todos: list[TodoItem], filter_option: str, search_query: str = ""
) -> list[TodoItem]:
    """선택된 필터 조건(전체/미완료/완료) 및 검색어에 맞게 할 일 목록을 필터링합니다."""
    filtered = todos

    # 상태 필터 적용
    if filter_option == FILTER_ACTIVE:
        filtered = [item for item in filtered if not item["completed"]]
    elif filter_option == FILTER_COMPLETED:
        filtered = [item for item in filtered if item["completed"]]

    # 검색어 필터 적용
    stripped_query = search_query.strip().lower()
    if stripped_query:
        filtered = [
            item for item in filtered if stripped_query in item["title"].lower()
        ]

    return filtered


# ==========================================
# UI 렌더링 함수 (UI Components)
# ==========================================
def render_header() -> None:
    """애플리케이션 타이틀 및 소개 문구를 렌더링합니다."""
    st.title(f"{PAGE_ICON} {PAGE_TITLE}")
    st.caption("단일 페이지 Streamlit 세션 상태 기반의 심플하고 빠른 할 일 관리 앱")
    st.divider()


def render_summary_dashboard(todos: list[TodoItem]) -> None:
    """완료/미완료 요약 통계 메트릭 및 진행률 바를 렌더링합니다."""
    stats = calculate_summary(todos)
    total = stats["total"]
    completed = stats["completed"]
    active = stats["active"]

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label="전체 할 일", value=f"{total}개")
    with col2:
        st.metric(label="미완료", value=f"{active}개", delta=f"-{active}" if active > 0 else None, delta_color="inverse")
    with col3:
        st.metric(label="완료됨", value=f"{completed}개", delta=f"+{completed}" if completed > 0 else None)

    # 진행률 프로그레스 바
    completion_rate: float = (completed / total) if total > 0 else 0.0
    st.progress(completion_rate, text=f"달성률: {int(completion_rate * 100)}% ({completed}/{total})")
    st.markdown("<br>", unsafe_allow_html=True)


def render_sidebar() -> tuple[str, str]:
    """
    AGENTS.md 규칙 준수: 필터 및 검색 위젯을 st.sidebar에 배치합니다.
    선택된 필터 옵션과 검색어 문자열을 반환합니다.
    """
    st.sidebar.header("🔍 필터 및 검색")

    # 검색 위젯
    search_keyword = st.sidebar.text_input(
        label="할 일 검색",
        value=st.session_state.get(SESSION_KEY_SEARCH, ""),
        placeholder=SEARCH_PLACEHOLDER,
    )
    st.session_state[SESSION_KEY_SEARCH] = search_keyword

    st.sidebar.markdown("---")

    # 필터 라디오 위젯
    selected_filter = st.sidebar.radio(
        label="상태별 보기",
        options=FILTER_OPTIONS,
        index=FILTER_OPTIONS.index(st.session_state.get(SESSION_KEY_FILTER, FILTER_ALL)),
    )
    st.session_state[SESSION_KEY_FILTER] = selected_filter

    return selected_filter, search_keyword


def render_input_form() -> None:
    """새로운 할 일을 등록할 수 있는 입력 폼을 렌더링합니다."""
    with st.form(key="add_todo_form", clear_on_submit=True):
        col_input, col_button = st.columns([5, 1])
        with col_input:
            new_title = st.text_input(
                label="할 일 입력",
                placeholder=INPUT_PLACEHOLDER,
                label_visibility="collapsed",
            )
        with col_button:
            submitted = st.form_submit_button("추가", use_container_width=True)

        if submitted:
            if add_todo(new_title):
                st.toast(MSG_ADD_SUCCESS, icon="🎉")
                st.rerun()
            else:
                st.warning(MSG_EMPTY_INPUT)


def render_todo_item(item: TodoItem) -> None:
    """
    개별 할 일 카드를 렌더링합니다.
    AGENTS.md 규칙: 목록 항목에 상태 아이콘 표시 (완료 ✅ / 미완료 ⬜)
    """
    is_completed: bool = item["completed"]
    item_id: str = item["id"]
    title_text: str = item["title"]
    status_icon: str = ICON_COMPLETED if is_completed else ICON_INCOMPLETE

    with st.container(border=True):
        col_check, col_text, col_del = st.columns([0.8, 7.2, 2.0], vertical_alignment="center")

        with col_check:
            # 체크박스 상태 변경 감지
            checked = st.checkbox(
                label=f"완료 체크 {item_id}",
                value=is_completed,
                key=f"check_{item_id}",
                label_visibility="collapsed",
            )
            if checked != is_completed:
                toggle_todo(item_id)
                st.rerun()

        with col_text:
            if is_completed:
                st.markdown(f"{status_icon} ~~**{title_text}**~~")
            else:
                st.markdown(f"{status_icon} **{title_text}**")
            st.caption(f"등록일시: {item['created_at']}")

        with col_del:
            if st.button("🗑️ 삭제", key=f"del_{item_id}", use_container_width=True):
                delete_todo(item_id)
                st.rerun()


def render_todo_list(filter_option: str, search_query: str) -> None:
    """할 일 목록 섹션을 렌더링합니다."""
    all_todos = get_all_todos()

    if not all_todos:
        st.info(MSG_NO_TODOS)
        return

    st.subheader("📋 할 일 목록")
    filtered_list = filter_todos(all_todos, filter_option, search_query)

    if not filtered_list:
        st.write(f"_{MSG_NO_FILTERED_TODOS}_")
        return

    for item in filtered_list:
        render_todo_item(item)


# ==========================================
# 메인 애플리케이션 진입점 (Main Entry)
# ==========================================
def main() -> None:
    """Streamlit 애플리케이션의 메인 루틴"""
    st.set_page_config(
        page_title=PAGE_TITLE,
        page_icon=PAGE_ICON,
        layout="centered",
        initial_sidebar_state="expanded",
    )

    # 세션 상태 초기화
    init_session_state()

    # 사이드바 필터 및 검색 렌더링 (AGENTS.md 규칙)
    current_filter, search_query = render_sidebar()

    # 상단 헤더
    render_header()

    # 상단 요약 통계 대시보드
    all_todos = get_all_todos()
    render_summary_dashboard(all_todos)

    # 할 일 추가 입력 폼
    render_input_form()

    st.markdown("<br>", unsafe_allow_html=True)

    # 할 일 목록 및 관리 섹션 (사이드바 필터/검색 연동)
    render_todo_list(current_filter, search_query)


if __name__ == "__main__":
    main()
