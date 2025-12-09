import streamlit as st
import pandas as pd
import json
from datetime import datetime
from typing import List, Dict
import google.generativeai as genai
import os

# 페이지 설정
st.set_page_config(
    page_title="신성EP - 샘플 관리 시스템",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS - 전문적이고 세련된 그레이/블루 계열
st.markdown("""
    <style>
        /* 메인 배경 설정 */
        .stApp {
            background: linear-gradient(135deg, #F5F7FA 0%, #E8ECF1 100%);
        }
        
        /* 헤더 스타일링 */
        h1, h2, h3 {
            color: #1A202C;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen', 'Ubuntu', 'Cantarell', sans-serif;
            font-weight: 600;
            letter-spacing: -0.02em;
        }
        
        h1 {
            border-bottom: 3px solid #4A5568;
            padding-bottom: 12px;
            margin-bottom: 24px;
            color: #2D3748;
        }
        
        h2 {
            color: #2D3748;
            margin-top: 24px;
            margin-bottom: 16px;
        }
        
        /* 버튼 스타일링 - 블루 계열 */
        .stButton > button {
            background: linear-gradient(135deg, #4A90E2 0%, #357ABD 100%);
            color: white;
            border-radius: 6px;
            border: none;
            padding: 0.625rem 1.5rem;
            font-weight: 500;
            transition: all 0.2s ease;
            box-shadow: 0 2px 4px rgba(74, 144, 226, 0.2);
        }
        
        .stButton > button:hover {
            background: linear-gradient(135deg, #357ABD 0%, #2E6DA4 100%);
            box-shadow: 0 4px 8px rgba(74, 144, 226, 0.3);
            transform: translateY(-1px);
        }

        /* 입력 필드 스타일링 - 그레이 계열 */
        .stTextInput > div > div > input,
        .stDateInput > div > div > input,
        .stSelectbox > div > div > div,
        .stTextArea > div > div > textarea {
            border-radius: 6px;
            border: 1.5px solid #CBD5E0;
            background-color: #FFFFFF;
            transition: all 0.2s ease;
        }
        
        .stTextInput > div > div > input:focus,
        .stDateInput > div > div > input:focus,
        .stTextArea > div > div > textarea:focus {
            border-color: #4A90E2;
            box-shadow: 0 0 0 3px rgba(74, 144, 226, 0.1);
            outline: none;
        }

        /* 데이터프레임 스타일링 */
        [data-testid="stDataFrame"] {
            border: 1px solid #E2E8F0;
            border-radius: 8px;
            overflow: hidden;
            background-color: #FFFFFF;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
        }

        /* 사이드바 스타일링 - 그레이 계열 */
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #F7FAFC 0%, #EDF2F7 100%);
            border-right: 2px solid #E2E8F0;
        }
        
        [data-testid="stSidebar"] .stRadio > div {
            background-color: #FFFFFF;
            padding: 8px;
            border-radius: 6px;
            border: 1px solid #E2E8F0;
        }

        /* 메트릭 카드 스타일링 */
        [data-testid="stMetricValue"] {
            color: #2C5282;
            font-weight: 700;
            font-size: 1.5rem;
        }
        [data-testid="stMetricLabel"] {
            color: #718096;
            font-weight: 500;
        }

        /* 탭 스타일링 */
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
            background-color: #F7FAFC;
            padding: 4px;
            border-radius: 8px;
        }
        .stTabs [data-baseweb="tab"] {
            height: 48px;
            white-space: pre-wrap;
            background-color: transparent;
            border-radius: 6px;
            color: #718096;
            font-weight: 500;
            transition: all 0.2s ease;
        }
        .stTabs [data-baseweb="tab"]:hover {
            background-color: #EDF2F7;
            color: #4A5568;
        }
        .stTabs [aria-selected="true"] {
            color: #2C5282;
            background-color: #FFFFFF;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
        }

        /* 성공/에러 메시지 스타일링 */
        .stSuccess {
            background-color: #F0F9FF;
            border-left: 4px solid #4A90E2;
            padding: 12px;
            border-radius: 4px;
        }
        
        .stError {
            background-color: #FEF2F2;
            border-left: 4px solid #E53E3E;
            padding: 12px;
            border-radius: 4px;
        }
        
        .stInfo {
            background-color: #EBF8FF;
            border-left: 4px solid #3182CE;
            padding: 12px;
            border-radius: 4px;
        }

        /* 라디오 버튼 스타일링 */
        .stRadio > label {
            color: #4A5568;
            font-weight: 500;
        }

        /* 구분선 스타일링 */
        hr {
            border: none;
            border-top: 1px solid #E2E8F0;
            margin: 20px 0;
        }
    </style>
 """, unsafe_allow_html=True)

# 세션 상태 초기화
if 'requests' not in st.session_state:
    st.session_state.requests = [
        {
            'id': 1,
            'requestDate': '2024-10-29',
            'companyName': 'INFAC 일렉스',
            'department': '개발',
            'contactPerson': '신동규 책임',
            'carModel': 'YB CUV PE2',
            'partNumber': 'PWA2024018',
            'partName': 'WIRE ASSY_TOUCH+NFC(LHD)',
            'quantity': 360,
            'dueDate': '2024-12-02',
            'requirements': '1. 검사성적서, 2. 3EA 별도 포장',
            'status': '출하 완료',
            'drawingStatus': '2024-10-29',
            'materialRequestDate': 'HOLDER WIRE 항공으로 발송됨',
            'expectedCompletionDate': '2024-11-21',
            'materialArrivalDate': '입고 완료',
            'sampleCompletionDate': '2024-11-23',
            'shipDate': '2024-11-23',
            'paymentStatus': '회수 완료',
            'remarks': 'EOL 성적서(별도), 종이 성적서',
        },
        {
            'id': 2,
            'requestDate': '2024-10-29',
            'companyName': 'INFAC 일렉스',
            'department': '개발',
            'contactPerson': '신동규 책임',
            'carModel': 'YB CUV PE2',
            'partNumber': 'PWA2024032',
            'partName': 'WIRE ASSY_TOUCH+NFC(RHD)',
            'quantity': 360,
            'dueDate': '2024-12-02',
            'requirements': '1. 검사성적서, 2. 3EA 별도 포장',
            'status': '출하 완료',
            'drawingStatus': '2024-10-29',
            'materialRequestDate': 'HOLDER WIRE 항공으로 발송됨',
            'expectedCompletionDate': '2024-11-21',
            'materialArrivalDate': '입고 완료',
            'sampleCompletionDate': '2024-11-23',
            'shipDate': '2024-11-23',
            'paymentStatus': '회수 완료',
            'remarks': 'EOL 성적서(별도), 종이 성적서',
        },
        {
            'id': 3,
            'requestDate': '2024-11-05',
            'companyName': 'INFAC 일렉스',
            'department': '개발',
            'contactPerson': '신동규 책임',
            'carModel': 'QU2I',
            'partNumber': '96240-BQ000',
            'partName': 'ANTENNA ASSY - CRASH PAD',
            'quantity': 33,
            'dueDate': '2024-11-18',
            'requirements': '3EA는 별도',
            'status': '출하 완료',
            'drawingStatus': '2024-11-05',
            'materialRequestDate': '',
            'expectedCompletionDate': '2024-11-14',
            'materialArrivalDate': '입고 완료',
            'sampleCompletionDate': '2024-11-15',
            'shipDate': '2024-11-15',
            'paymentStatus': '미회수',
            'remarks': 'EOL 성적서(별도), 종이 성적서',
        },
        {
            'id': 4,
            'requestDate': '2024-11-05',
            'companyName': 'INFAC 일렉스',
            'department': '구매',
            'contactPerson': '박환희 책임',
            'carModel': 'ME 차종 상대물',
            'partNumber': '-',
            'partName': '-',
            'quantity': 50,
            'dueDate': '2024-11-18',
            'requirements': '300mm: 35EA, 2M: 15EA, 3,4 TWIST',
            'status': '지연',
            'drawingStatus': '2024-11-05',
            'materialRequestDate': '인팩 일렉스에서 송부 AIR 송부',
            'expectedCompletionDate': '2024-11-26',
            'materialArrivalDate': '입고 완료',
            'sampleCompletionDate': '2024-11-15',
            'shipDate': '일부 2024.11.15',
            'paymentStatus': '-',
            'remarks': '터미널 부족으로 300mm만 출하됨',
        },
        {
            'id': 5,
            'requestDate': '2024-11-07',
            'companyName': 'INFAC 일렉스',
            'department': '개발',
            'contactPerson': '임현재 책임',
            'carModel': 'SG2 PE',
            'partNumber': 'PWA2024030',
            'partName': 'WIRE ASSY TOUCH+NFC',
            'quantity': 200,
            'dueDate': '당사 가능일정 회신',
            'requirements': '견적 및 HOLDER 제외',
            'status': '진행 중',
            'drawingStatus': '2024-11-07',
            'materialRequestDate': '',
            'expectedCompletionDate': '2024-11-21',
            'materialArrivalDate': '부자재 없음',
            'sampleCompletionDate': '2024-11-23',
            'shipDate': '',
            'paymentStatus': '-',
            'remarks': '4M 신뢰성 샘플, CABLE 자체 개발건',
        },
    ]

if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

if 'user_role' not in st.session_state:
    st.session_state.user_role = None

# 사용자 데이터 로드 및 초기화
USERS_FILE = 'users.json'

def load_users():
    """사용자 데이터 로드"""
    try:
        if os.path.exists(USERS_FILE):
            with open(USERS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
    except:
        pass
    return {
        'admins': [],
        'customers': []
    }

def save_users(users_data):
    """사용자 데이터 저장"""
    try:
        with open(USERS_FILE, 'w', encoding='utf-8') as f:
            json.dump(users_data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        st.error(f"사용자 데이터 저장 실패: {str(e)}")
        return False

def register_user(role, username, password, company_name=None, name=None):
    """사용자 등록"""
    users = load_users()
    
    if role == 'ADMIN':
        # 중복 확인
        if any(u['username'] == username for u in users['admins']):
            return False, "이미 등록된 관리자 아이디입니다."
        users['admins'].append({
            'username': username,
            'password': password,
            'registered_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })
    else:  # CUSTOMER
        # 중복 확인 (업체명 + 이름)
        if any(u['companyName'] == company_name and u['name'] == name for u in users['customers']):
            return False, "이미 등록된 고객사입니다."
        users['customers'].append({
            'companyName': company_name,
            'name': name,
            'password': password,
            'registered_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })
    
    if save_users(users):
        return True, "등록이 완료되었습니다!"
    else:
        return False, "등록 중 오류가 발생했습니다."

def verify_user(role, username=None, password=None, company_name=None, name=None):
    """사용자 인증"""
    users = load_users()
    
    if role == 'ADMIN':
        admin = next((u for u in users['admins'] if u['username'] == username and u['password'] == password), None)
        return admin is not None
    else:  # CUSTOMER
        customer = next((u for u in users['customers'] 
                        if u['companyName'] == company_name and u['name'] == name and u['password'] == password), None)
        return customer is not None

# Gemini AI 설정
def setup_gemini():
    api_key = os.getenv('GEMINI_API_KEY') or st.secrets.get('GEMINI_API_KEY', '')
    if api_key:
        genai.configure(api_key=api_key)
        return True
    return False

# AI 분석 함수
def analyze_risks(requests):
    try:
        if not setup_gemini():
            return "API 키가 설정되지 않았습니다. 환경 변수 GEMINI_API_KEY를 설정해주세요."
        
        model = genai.GenerativeModel('gemini-2.0-flash-exp')
        
        # 문제가 있는 요청만 필터링
        problem_requests = [r for r in requests if r.get('remarks') or r.get('status') == '지연']
        
        prompt = f"""
        제조 생산 관리자 어시스턴트로서 다음 샘플 요청 원장 데이터를 검토하세요.
        "remarks" 또는 "materialArrivalDate"에 명시된 문제(예: "부족", "누락", "지연")가 있는 행을 식별하세요.
        
        다음을 간결한 불릿 포인트로 요약하세요:
        1. 중요한 위험 사항 (예: 터미널 부족)
        2. 생산 팀을 위한 권장 조치 사항
        
        전문적이고 간결하게 작성하세요 (150단어 이하). 언어: 한국어.
        
        데이터:
        {json.dumps(problem_requests, ensure_ascii=False, indent=2)}
        """
        
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"AI 분석 중 오류가 발생했습니다: {str(e)}"

# 로그인/등록 페이지
def login_page():
    st.title("🔐 로그인 / 회원가입")
    st.markdown("---")
    
    # 탭 선택
    tab1, tab2 = st.tabs(["로그인", "회원가입"])
    
    with tab1:
        st.subheader("로그인")
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            role = st.radio("역할 선택", ["관리자", "고객사"], horizontal=True)
            
            if role == "고객사":
                company_name = st.text_input("업체명 *")
                name = st.text_input("이름 *")
                password = st.text_input("비밀번호 *", type="password", help="처음 로그인하시면 자동으로 회원가입됩니다.")
                if st.button("로그인", type="primary", use_container_width=True):
                    if company_name and name and password:
                        # 먼저 기존 사용자 확인
                        if verify_user('CUSTOMER', company_name=company_name, name=name, password=password):
                            st.session_state.authenticated = True
                            st.session_state.user_role = "CUSTOMER"
                            st.session_state.user_company = company_name
                            st.session_state.user_name = name
                            st.success("로그인 성공!")
                            st.rerun()
                        else:
                            # 등록되지 않은 사용자면 자동 등록
                            users = load_users()
                            # 중복 확인 (업체명 + 이름)
                            existing = next((u for u in users['customers'] 
                                           if u['companyName'] == company_name and u['name'] == name), None)
                            
                            if existing:
                                # 같은 업체명+이름이 있지만 비밀번호가 다른 경우
                                st.error("비밀번호가 올바르지 않습니다.")
                            else:
                                # 신규 사용자 자동 등록
                                if len(password) < 4:
                                    st.error("비밀번호는 4자 이상이어야 합니다.")
                                else:
                                    success, message = register_user('CUSTOMER', None, password, company_name, name)
                                    if success:
                                        st.session_state.authenticated = True
                                        st.session_state.user_role = "CUSTOMER"
                                        st.session_state.user_company = company_name
                                        st.session_state.user_name = name
                                        st.success(f"회원가입 및 로그인 완료! {message}")
                                        st.rerun()
                                    else:
                                        st.error(message)
                    else:
                        st.error("모든 필드를 입력해주세요.")
            else:  # 관리자
                username = st.text_input("아이디 *")
                password = st.text_input("비밀번호 *", type="password")
                if st.button("로그인", type="primary", use_container_width=True):
                    if username and password:
                        if verify_user('ADMIN', username=username, password=password):
                            st.session_state.authenticated = True
                            st.session_state.user_role = "ADMIN"
                            st.session_state.username = username
                            st.success("로그인 성공!")
                            st.rerun()
                        else:
                            st.error("아이디 또는 비밀번호가 올바르지 않습니다.")
                    else:
                        st.error("아이디와 비밀번호를 입력해주세요.")
    
    with tab2:
        st.subheader("회원가입")
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            reg_role = st.radio("역할 선택", ["관리자", "고객사"], horizontal=True, key="reg_role")
            
            if reg_role == "고객사":
                reg_company_name = st.text_input("업체명 *", key="reg_company")
                reg_name = st.text_input("이름 *", key="reg_name")
                reg_password = st.text_input("비밀번호 *", type="password", key="reg_customer_pw")
                reg_password_confirm = st.text_input("비밀번호 확인 *", type="password", key="reg_customer_pw_confirm")
                
                if st.button("회원가입", type="primary", use_container_width=True, key="reg_customer_btn"):
                    if reg_company_name and reg_name and reg_password:
                        if reg_password != reg_password_confirm:
                            st.error("비밀번호가 일치하지 않습니다.")
                        elif len(reg_password) < 4:
                            st.error("비밀번호는 4자 이상이어야 합니다.")
                        else:
                            success, message = register_user('CUSTOMER', None, reg_password, reg_company_name, reg_name)
                            if success:
                                st.success(message)
                                st.info("회원가입이 완료되었습니다. 로그인 탭에서 로그인해주세요.")
                            else:
                                st.error(message)
                    else:
                        st.error("모든 필드를 입력해주세요.")
            else:  # 관리자
                reg_username = st.text_input("아이디 *", key="reg_username")
                reg_password = st.text_input("비밀번호 *", type="password", key="reg_admin_pw")
                reg_password_confirm = st.text_input("비밀번호 확인 *", type="password", key="reg_admin_pw_confirm")
                
                if st.button("회원가입", type="primary", use_container_width=True, key="reg_admin_btn"):
                    if reg_username and reg_password:
                        if reg_password != reg_password_confirm:
                            st.error("비밀번호가 일치하지 않습니다.")
                        elif len(reg_password) < 4:
                            st.error("비밀번호는 4자 이상이어야 합니다.")
                        elif len(reg_username) < 3:
                            st.error("아이디는 3자 이상이어야 합니다.")
                        else:
                            success, message = register_user('ADMIN', reg_username, reg_password)
                            if success:
                                st.success(message)
                                st.info("회원가입이 완료되었습니다. 로그인 탭에서 로그인해주세요.")
                            else:
                                st.error(message)
                    else:
                        st.error("아이디와 비밀번호를 입력해주세요.")

# 메인 대시보드
def main_dashboard():
    st.title("📦 신성EP - 샘플 관리 시스템")
    st.markdown("---")
    
    # 사이드바
    with st.sidebar:
        st.header("메뉴")
        view_option = st.radio("보기", ["원장", "새 요청 등록", "AI 분석"])
        
        if st.button("로그아웃", use_container_width=True):
            st.session_state.authenticated = False
            st.session_state.user_role = None
            st.rerun()
        
        st.markdown("---")
        st.caption(f"역할: {st.session_state.user_role}")
        if st.session_state.user_role == "CUSTOMER":
            st.caption(f"업체: {st.session_state.get('user_company', '')}")
            st.caption(f"이름: {st.session_state.get('user_name', '')}")
        elif st.session_state.user_role == "ADMIN":
            st.caption(f"아이디: {st.session_state.get('username', '')}")
    
    # 원장 보기
    if view_option == "원장":
        st.header("📋 샘플 요청 원장")
        
        # 검색
        search_term = st.text_input("🔍 검색", placeholder="업체명, 품번, 품명으로 검색...")
        
        # 필터링
        filtered_requests = st.session_state.requests
        if search_term:
            filtered_requests = [
                r for r in filtered_requests
                if search_term.lower() in str(r.get('companyName', '')).lower() or
                   search_term.lower() in str(r.get('partNumber', '')).lower() or
                   search_term.lower() in str(r.get('partName', '')).lower()
            ]
        
        # 데이터프레임 생성
        if filtered_requests:
            df = pd.DataFrame(filtered_requests)
            
            # 표시할 컬럼 선택
            display_cols = [
                'id', 'requestDate', 'companyName', 'department', 'contactPerson',
                'carModel', 'partNumber', 'partName', 'quantity', 'dueDate',
                'status', 'sampleCompletionDate', 'shipDate', 'paymentStatus'
            ]
            
            # 존재하는 컬럼만 선택
            available_cols = [col for col in display_cols if col in df.columns]
            df_display = df[available_cols]
            
            st.dataframe(
                df_display,
                use_container_width=True,
                hide_index=True,
                height=400
            )
            
            # 통계
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("전체", len(df))
            with col2:
                st.metric("진행 중", len(df[df['status'] == '진행 중']))
            with col3:
                st.metric("완료", len(df[df['status'] == '출하 완료']))
            with col4:
                st.metric("지연", len(df[df['status'] == '지연']))
        else:
            st.info("검색 결과가 없습니다.")
    
    # 새 요청 등록
    elif view_option == "새 요청 등록":
        st.header("➕ 새 샘플 요청 등록")
        
        with st.form("new_request_form"):
            col1, col2 = st.columns(2)
            with col1:
                request_date = st.date_input("접수일", value=datetime.now().date())
                company_name = st.text_input("업체명 *", value=st.session_state.get('user_company', ''))
                department = st.text_input("부서")
                contact_person = st.text_input("담당자 *")
                car_model = st.text_input("차종")
            
            with col2:
                part_number = st.text_input("품번 *")
                part_name = st.text_input("품명 *")
                quantity = st.number_input("주문수량 *", min_value=1, value=1)
                due_date = st.date_input("납기")
                requirements = st.text_area("요청사항")
            
            attachment = st.file_uploader("첨부파일", type=['pdf', 'xlsx', 'xls', 'jpg', 'png'])
            
            submitted = st.form_submit_button("등록", type="primary", use_container_width=True)
            
            if submitted:
                if company_name and contact_person and part_number and part_name:
                    new_id = max([r['id'] for r in st.session_state.requests], default=0) + 1
                    new_request = {
                        'id': new_id,
                        'requestDate': request_date.strftime('%Y-%m-%d'),
                        'companyName': company_name,
                        'department': department,
                        'contactPerson': contact_person,
                        'carModel': car_model,
                        'partNumber': part_number,
                        'partName': part_name,
                        'quantity': int(quantity),
                        'dueDate': due_date.strftime('%Y-%m-%d') if due_date else '',
                        'requirements': requirements,
                        'status': '접수 대기',
                        'attachmentName': attachment.name if attachment else None,
                    }
                    st.session_state.requests.append(new_request)
                    st.success("샘플 요청이 등록되었습니다!")
                    st.rerun()
                else:
                    st.error("필수 항목(*)을 모두 입력해주세요.")
    
    # AI 분석
    elif view_option == "AI 분석":
        st.header("🤖 AI 리스크 분석")
        
        if st.button("분석 실행", type="primary"):
            with st.spinner("AI가 데이터를 분석 중입니다..."):
                analysis = analyze_risks(st.session_state.requests)
                st.markdown("### 분석 결과")
                st.markdown(analysis)
        
        st.markdown("---")
        st.info("💡 AI 분석은 Gemini API를 사용합니다. 환경 변수 GEMINI_API_KEY를 설정해주세요.")

# 메인 실행
if not st.session_state.authenticated:
    login_page()
else:
    main_dashboard()


