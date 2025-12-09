import streamlit as st
import pandas as pd
import json
from datetime import datetime
from typing import List, Dict
import os
from io import BytesIO

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

# 사용자 데이터 로드 및 초기화
USERS_FILE = 'users.json'

def load_users():
    """사용자 데이터 로드 - 기존 데이터 절대 덮어쓰지 않음"""
    # 파일이 존재하면 무조건 읽기 시도
    if os.path.exists(USERS_FILE):
        try:
            with open(USERS_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # 기존 데이터 구조 확인 및 보존
                if isinstance(data, dict):
                    # 기본 구조가 없으면 추가
                    if 'admins' not in data:
                        data['admins'] = []
                    if 'customers' not in data:
                        data['customers'] = []
                    return data
        except json.JSONDecodeError:
            # JSON 파싱 오류 - 파일 백업 후 빈 구조 반환
            try:
                backup_file = f"{USERS_FILE}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                import shutil
                shutil.copy2(USERS_FILE, backup_file)
            except:
                pass
            # 손상된 파일이어도 기존 파일은 유지
            return {
                'admins': [],
                'customers': []
            }
        except Exception as e:
            # 기타 오류 - 파일은 유지하고 빈 구조만 반환
            return {
                'admins': [],
                'customers': []
            }
    
    # 파일이 없을 때만 빈 구조 반환 (파일 생성은 하지 않음)
    return {
        'admins': [],
        'customers': []
    }

def save_users(users_data):
    """사용자 데이터 저장 - 기존 파일 백업 후 저장"""
    try:
        # 기존 파일이 있으면 백업
        if os.path.exists(USERS_FILE):
            try:
                backup_file = f"{USERS_FILE}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                import shutil
                shutil.copy2(USERS_FILE, backup_file)
                # 오래된 백업 파일 정리 (최근 5개만 유지)
                import glob
                backups = sorted(glob.glob(f"{USERS_FILE}.backup_*"), reverse=True)
                for old_backup in backups[5:]:
                    try:
                        os.remove(old_backup)
                    except:
                        pass
            except:
                pass
        
        # 새 데이터 저장
        with open(USERS_FILE, 'w', encoding='utf-8') as f:
            json.dump(users_data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        # 저장 실패 시에도 기존 파일은 유지됨
        if 'st' in globals():
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

# 로그인 정보 영구 저장을 위한 파일
LOGIN_INFO_FILE = 'login_info.json'

def load_login_info():
    """저장된 로그인 정보 로드 - 기존 데이터 절대 덮어쓰지 않음"""
    if os.path.exists(LOGIN_INFO_FILE):
        try:
            with open(LOGIN_INFO_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # 필수 필드 확인
                if isinstance(data, dict) and 'role' in data:
                    return data
        except json.JSONDecodeError:
            # JSON 파싱 오류 - 파일 백업
            try:
                backup_file = f"{LOGIN_INFO_FILE}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                import shutil
                shutil.copy2(LOGIN_INFO_FILE, backup_file)
            except:
                pass
            # 손상된 파일이어도 기존 파일은 유지
            return None
        except Exception:
            # 기타 오류 - 파일은 유지
            return None
    return None

def save_login_info(role, username=None, company_name=None, name=None):
    """로그인 정보 저장"""
    try:
        login_info = {
            'role': role,
            'username': username,
            'company_name': company_name,
            'name': name,
            'saved_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        with open(LOGIN_INFO_FILE, 'w', encoding='utf-8') as f:
            json.dump(login_info, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        return False

def clear_login_info():
    """로그인 정보 삭제"""
    try:
        if os.path.exists(LOGIN_INFO_FILE):
            os.remove(LOGIN_INFO_FILE)
    except:
        pass

# 저장된 로그인 정보가 있으면 자동 로그인
if 'authenticated' not in st.session_state:
    saved_login = load_login_info()
    if saved_login:
        # 저장된 정보로 자동 로그인 (이미 인증된 사용자로 간주)
        if saved_login['role'] == 'ADMIN':
            # 관리자 정보 확인
            users = load_users()
            admin = next((u for u in users['admins'] 
                         if u['username'] == saved_login.get('username')), None)
            if admin:
                st.session_state.authenticated = True
                st.session_state.user_role = "ADMIN"
                st.session_state.username = saved_login.get('username')
        elif saved_login['role'] == 'CUSTOMER':
            # 고객사는 업체명과 이름으로 확인
            users = load_users()
            customer = next((u for u in users['customers'] 
                           if u['companyName'] == saved_login.get('company_name') 
                           and u['name'] == saved_login.get('name')), None)
            if customer:
                st.session_state.authenticated = True
                st.session_state.user_role = "CUSTOMER"
                st.session_state.user_company = saved_login.get('company_name')
                st.session_state.user_name = saved_login.get('name')
    else:
        st.session_state.authenticated = False

if 'user_role' not in st.session_state:
    st.session_state.user_role = None


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
                            # 로그인 정보 저장
                            save_login_info('CUSTOMER', company_name=company_name, name=name)
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
                                        # 로그인 정보 저장
                                        save_login_info('CUSTOMER', company_name=company_name, name=name)
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
                            # 로그인 정보 저장
                            save_login_info('ADMIN', username=username)
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
        view_option = st.radio("보기", ["대시보드", "원장", "새 요청 등록"])
        
        if st.button("로그아웃", use_container_width=True):
            st.session_state.authenticated = False
            st.session_state.user_role = None
            # 저장된 로그인 정보 삭제
            clear_login_info()
            st.rerun()
        
        st.markdown("---")
        st.caption(f"역할: {st.session_state.user_role}")
        if st.session_state.user_role == "CUSTOMER":
            st.caption(f"업체: {st.session_state.get('user_company', '')}")
            st.caption(f"이름: {st.session_state.get('user_name', '')}")
        elif st.session_state.user_role == "ADMIN":
            st.caption(f"아이디: {st.session_state.get('username', '')}")
    
    # 대시보드
    if view_option == "대시보드":
        st.markdown("""
        <style>
            .dashboard-header {
                background: #1A202C;
                padding: 1.5rem 2rem;
                border-radius: 8px;
                color: white;
                margin-bottom: 1.5rem;
                border-left: 4px solid #4A90E2;
            }
            .metric-card {
                background: white;
                padding: 1rem 1.25rem;
                border-radius: 6px;
                box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
                border-left: 3px solid #4A90E2;
            }
            .summary-table {
                background: white;
                padding: 0.75rem;
                border-radius: 6px;
                box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
                border: 1px solid #E2E8F0;
            }
            .summary-title {
                font-size: 0.85rem;
                font-weight: 600;
                color: #4A5568;
                margin-bottom: 0.5rem;
                padding-bottom: 0.25rem;
                border-bottom: 1px solid #E2E8F0;
            }
        </style>
        """, unsafe_allow_html=True)
        
        st.markdown('<div class="dashboard-header"><h1 style="margin:0; color:white; font-size:1.5rem;">📊 대시보드</h1></div>', unsafe_allow_html=True)
        
        # 데이터프레임 생성
        df = pd.DataFrame(st.session_state.requests)
        
        if not df.empty:
            # 주요 지표 카드 (상단)
            metric_col1, metric_col2, metric_col3, metric_col4, metric_col5 = st.columns(5)
            
            with metric_col1:
                total = len(df)
                st.markdown(f"""
                <div class="metric-card">
                    <div style="font-size: 0.75rem; color: #718096; margin-bottom: 0.25rem;">전체 요청</div>
                    <div style="font-size: 1.5rem; font-weight: 700; color: #2D3748;">{total}</div>
                    <div style="font-size: 0.7rem; color: #A0AEC0;">건</div>
                </div>
                """, unsafe_allow_html=True)
            
            with metric_col2:
                if 'status' in df.columns:
                    in_progress = len(df[df['status'] == '진행 중'])
                else:
                    in_progress = 0
                st.markdown(f"""
                <div class="metric-card" style="border-left-color: #3182CE;">
                    <div style="font-size: 0.75rem; color: #718096; margin-bottom: 0.25rem;">진행 중</div>
                    <div style="font-size: 1.5rem; font-weight: 700; color: #3182CE;">{in_progress}</div>
                    <div style="font-size: 0.7rem; color: #A0AEC0;">건</div>
                </div>
                """, unsafe_allow_html=True)
            
            with metric_col3:
                if 'status' in df.columns:
                    completed = len(df[df['status'] == '출하 완료'])
                else:
                    completed = 0
                st.markdown(f"""
                <div class="metric-card" style="border-left-color: #38A169;">
                    <div style="font-size: 0.75rem; color: #718096; margin-bottom: 0.25rem;">완료</div>
                    <div style="font-size: 1.5rem; font-weight: 700; color: #38A169;">{completed}</div>
                    <div style="font-size: 0.7rem; color: #A0AEC0;">건</div>
                </div>
                """, unsafe_allow_html=True)
            
            with metric_col4:
                if 'status' in df.columns:
                    delayed = len(df[df['status'] == '지연'])
                else:
                    delayed = 0
                st.markdown(f"""
                <div class="metric-card" style="border-left-color: #E53E3E;">
                    <div style="font-size: 0.75rem; color: #718096; margin-bottom: 0.25rem;">지연</div>
                    <div style="font-size: 1.5rem; font-weight: 700; color: #E53E3E;">{delayed}</div>
                    <div style="font-size: 0.7rem; color: #A0AEC0;">건</div>
                </div>
                """, unsafe_allow_html=True)
            
            with metric_col5:
                if 'quantity' in df.columns:
                    total_qty = df['quantity'].sum()
                else:
                    total_qty = 0
                st.markdown(f"""
                <div class="metric-card" style="border-left-color: #805AD5;">
                    <div style="font-size: 0.75rem; color: #718096; margin-bottom: 0.25rem;">총 수량</div>
                    <div style="font-size: 1.5rem; font-weight: 700; color: #805AD5;">{total_qty:,}</div>
                    <div style="font-size: 0.7rem; color: #A0AEC0;">EA</div>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            # 요약집계표를 한 줄에 6개 배치
            summary_col1, summary_col2, summary_col3, summary_col4, summary_col5, summary_col6 = st.columns(6)
            
            with summary_col1:
                st.markdown('<div class="summary-title">상태별</div>', unsafe_allow_html=True)
                if 'status' in df.columns:
                    status_summary = df['status'].value_counts().reset_index()
                    status_summary.columns = ['상태', '건수']
                    st.markdown('<div class="summary-table">', unsafe_allow_html=True)
                    st.dataframe(
                        status_summary,
                        use_container_width=True,
                        hide_index=True,
                        height=120
                    )
                    st.markdown('</div>', unsafe_allow_html=True)
                else:
                    st.info("", icon="")
            
            with summary_col2:
                st.markdown('<div class="summary-title">업체별</div>', unsafe_allow_html=True)
                if 'companyName' in df.columns:
                    company_summary = df.groupby('companyName').agg({
                        'id': 'count',
                        'quantity': 'sum' if 'quantity' in df.columns else 'count'
                    }).reset_index()
                    company_summary.columns = ['업체명', '건수', '수량']
                    company_summary = company_summary.sort_values('건수', ascending=False).head(5)
                    st.markdown('<div class="summary-table">', unsafe_allow_html=True)
                    st.dataframe(
                        company_summary,
                        use_container_width=True,
                        hide_index=True,
                        height=120
                    )
                    st.markdown('</div>', unsafe_allow_html=True)
                else:
                    st.info("", icon="")
            
            with summary_col3:
                st.markdown('<div class="summary-title">담당자별</div>', unsafe_allow_html=True)
                if 'contactPerson' in df.columns:
                    contact_summary = df.groupby('contactPerson').agg({
                        'id': 'count',
                        'quantity': 'sum' if 'quantity' in df.columns else 'count'
                    }).reset_index()
                    contact_summary.columns = ['담당자', '건수', '수량']
                    contact_summary = contact_summary.sort_values('건수', ascending=False).head(5)
                    st.markdown('<div class="summary-table">', unsafe_allow_html=True)
                    st.dataframe(
                        contact_summary,
                        use_container_width=True,
                        hide_index=True,
                        height=120
                    )
                    st.markdown('</div>', unsafe_allow_html=True)
                else:
                    st.info("", icon="")
            
            with summary_col4:
                st.markdown('<div class="summary-title">부서별</div>', unsafe_allow_html=True)
                if 'department' in df.columns:
                    dept_summary = df.groupby('department').agg({
                        'id': 'count',
                        'quantity': 'sum' if 'quantity' in df.columns else 'count'
                    }).reset_index()
                    dept_summary.columns = ['부서', '건수', '수량']
                    dept_summary = dept_summary.sort_values('건수', ascending=False)
                    st.markdown('<div class="summary-table">', unsafe_allow_html=True)
                    st.dataframe(
                        dept_summary,
                        use_container_width=True,
                        hide_index=True,
                        height=120
                    )
                    st.markdown('</div>', unsafe_allow_html=True)
                else:
                    st.info("", icon="")
            
            with summary_col5:
                st.markdown('<div class="summary-title">회수현황</div>', unsafe_allow_html=True)
                if 'paymentStatus' in df.columns:
                    payment_summary = df['paymentStatus'].value_counts().reset_index()
                    payment_summary.columns = ['회수여부', '건수']
                    st.markdown('<div class="summary-table">', unsafe_allow_html=True)
                    st.dataframe(
                        payment_summary,
                        use_container_width=True,
                        hide_index=True,
                        height=120
                    )
                    st.markdown('</div>', unsafe_allow_html=True)
                else:
                    st.info("", icon="")
            
            with summary_col6:
                st.markdown('<div class="summary-title">차종별</div>', unsafe_allow_html=True)
                if 'carModel' in df.columns:
                    car_summary = df.groupby('carModel').agg({
                        'id': 'count',
                        'quantity': 'sum' if 'quantity' in df.columns else 'count'
                    }).reset_index()
                    car_summary.columns = ['차종', '건수', '수량']
                    car_summary = car_summary.sort_values('건수', ascending=False).head(5)
                    st.markdown('<div class="summary-table">', unsafe_allow_html=True)
                    st.dataframe(
                        car_summary,
                        use_container_width=True,
                        hide_index=True,
                        height=120
                    )
                    st.markdown('</div>', unsafe_allow_html=True)
                else:
                    st.info("", icon="")
            
            # 최근 요청 현황
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown('<div style="font-size: 0.95rem; font-weight: 600; color: #2D3748; margin: 1rem 0 0.5rem 0;">최근 요청 현황 (최근 5건)</div>', unsafe_allow_html=True)
            if 'requestDate' in df.columns:
                df_sorted = df.copy()
                df_sorted['requestDate'] = pd.to_datetime(df_sorted['requestDate'], errors='coerce')
                df_recent = df_sorted.sort_values('requestDate', ascending=False).head(5)
                
                recent_cols = ['id', 'requestDate', 'companyName', 'partNumber', 'partName', 'status', 'quantity']
                recent_cols = [col for col in recent_cols if col in df_recent.columns]
                
                st.dataframe(
                    df_recent[recent_cols],
                    use_container_width=True,
                    hide_index=True,
                    height=180
                )
            else:
                st.info("날짜 데이터가 없습니다.")
                
        else:
            st.info("등록된 요청이 없습니다.")
    
    # 원장 보기
    elif view_option == "원장":
        st.header("📋 샘플 요청 원장")
        
        # 검색
        search_term = st.text_input("🔍 검색", placeholder="업체명, 품번, 품명으로 검색...")
        
        # 데이터프레임 생성
        df = pd.DataFrame(st.session_state.requests)
        
        if not df.empty:
            # 표시할 컬럼 선택
            display_cols = [
                'id', 'requestDate', 'companyName', 'department', 'contactPerson',
                'carModel', 'partNumber', 'partName', 'quantity', 'dueDate',
                'status', 'sampleCompletionDate', 'shipDate', 'paymentStatus'
            ]
            
            # 존재하는 컬럼만 선택
            available_cols = [col for col in display_cols if col in df.columns]
            df_display = df[available_cols].copy()
            
            # 컬럼명 한글 매핑 (표시용)
            column_mapping_display = {
                'id': '번호',
                'requestDate': '접수일',
                'companyName': '회사명',
                'department': '부서',
                'contactPerson': '요청자',
                'carModel': '차종',
                'partNumber': '품번',
                'partName': '부품명',
                'quantity': '수량',
                'dueDate': '납기일',
                'status': '상태',
                'sampleCompletionDate': '자재완료일',
                'shipDate': '납품일',
                'paymentStatus': '대금회수'
            }
            
            # 검색 필터링 (영어 컬럼명으로)
            if search_term:
                mask = (
                    df_display['companyName'].astype(str).str.contains(search_term, case=False, na=False) |
                    df_display['partNumber'].astype(str).str.contains(search_term, case=False, na=False) |
                    df_display['partName'].astype(str).str.contains(search_term, case=False, na=False)
                )
                df_display = df_display[mask]
            
            # 표시용 데이터프레임 생성 (한글 컬럼명)
            df_display_kr = df_display.copy()
            df_display_kr.columns = [column_mapping_display.get(col, col) for col in df_display_kr.columns]
            
            # 열별 필터 추가 - 한 줄에 모두 표시
            st.subheader("🔽 필터")
            
            # 필터 레이블 표시 (위에)
            label_cols = st.columns(8)
            with label_cols[0]:
                st.caption("**업체명**")
            with label_cols[1]:
                st.caption("**부서**")
            with label_cols[2]:
                st.caption("**상태**")
            with label_cols[3]:
                st.caption("**담당자**")
            with label_cols[4]:
                st.caption("**차종**")
            with label_cols[5]:
                st.caption("**회수여부**")
            with label_cols[6]:
                st.caption("**품번**")
            with label_cols[7]:
                st.caption("**초기화**")
            
            filter_cols = st.columns(8)
            filters = {}
            
            with filter_cols[0]:
                if 'companyName' in df_display.columns:
                    companies = ['전체'] + sorted(df_display['companyName'].dropna().unique().tolist())
                    selected_company = st.selectbox("업체명", companies, key="filter_company", label_visibility="collapsed")
                    if selected_company != '전체':
                        filters['companyName'] = selected_company
            
            with filter_cols[1]:
                if 'department' in df_display.columns:
                    departments = ['전체'] + sorted(df_display['department'].dropna().unique().tolist())
                    selected_dept = st.selectbox("부서", departments, key="filter_department", label_visibility="collapsed")
                    if selected_dept != '전체':
                        filters['department'] = selected_dept
            
            with filter_cols[2]:
                if 'status' in df_display.columns:
                    statuses = ['전체'] + sorted(df_display['status'].dropna().unique().tolist())
                    selected_status = st.selectbox("상태", statuses, key="filter_status", label_visibility="collapsed")
                    if selected_status != '전체':
                        filters['status'] = selected_status
            
            with filter_cols[3]:
                if 'contactPerson' in df_display.columns:
                    contacts = ['전체'] + sorted(df_display['contactPerson'].dropna().unique().tolist())
                    selected_contact = st.selectbox("담당자", contacts, key="filter_contact", label_visibility="collapsed")
                    if selected_contact != '전체':
                        filters['contactPerson'] = selected_contact
            
            with filter_cols[4]:
                if 'carModel' in df_display.columns:
                    car_models = ['전체'] + sorted(df_display['carModel'].dropna().unique().tolist())
                    selected_car = st.selectbox("차종", car_models, key="filter_car", label_visibility="collapsed")
                    if selected_car != '전체':
                        filters['carModel'] = selected_car
            
            with filter_cols[5]:
                if 'paymentStatus' in df_display.columns:
                    payments = ['전체'] + sorted(df_display['paymentStatus'].dropna().unique().tolist())
                    selected_payment = st.selectbox("회수여부", payments, key="filter_payment", label_visibility="collapsed")
                    if selected_payment != '전체':
                        filters['paymentStatus'] = selected_payment
            
            with filter_cols[6]:
                if 'partNumber' in df_display.columns:
                    part_numbers = ['전체'] + sorted(df_display['partNumber'].dropna().unique().tolist())
                    selected_part = st.selectbox("품번", part_numbers, key="filter_part", label_visibility="collapsed")
                    if selected_part != '전체':
                        filters['partNumber'] = selected_part
            
            with filter_cols[7]:
                if st.button("초기화", use_container_width=True, key="reset_filter"):
                    filters = {}
                    st.rerun()
            
            # 필터 적용 (영어 컬럼명으로 필터링)
            df_filtered = df_display.copy()
            for col, value in filters.items():
                if col in df_filtered.columns:
                    df_filtered = df_filtered[df_filtered[col] == value]
            
            # 필터링된 데이터를 한글 컬럼명으로 변환
            df_filtered_kr = df_filtered.copy()
            df_filtered_kr.columns = [column_mapping_display.get(col, col) for col in df_filtered_kr.columns]
            
            # 필터링된 데이터 표시
            if not df_filtered.empty:
                # 엑셀 다운로드 버튼
                download_col1, download_col2 = st.columns([1, 5])
                with download_col1:
                    # 엑셀 다운로드 - 컬럼명 한글로 변환
                    def to_excel(df):
                        output = BytesIO()
                        # 컬럼명 한글 매핑
                        column_mapping = {
                            'id': '번호',
                            'requestDate': '접수일',
                            'companyName': '회사명',
                            'department': '부서',
                            'contactPerson': '요청자',
                            'carModel': '차종',
                            'partNumber': '품번',
                            'partName': '부품명',
                            'quantity': '수량',
                            'dueDate': '납기일',
                            'status': '상태',
                            'sampleCompletionDate': '자재완료일',
                            'shipDate': '납품일',
                            'paymentStatus': '대금회수'
                        }
                        df_export = df.copy()
                        df_export.columns = [column_mapping.get(col, col) for col in df_export.columns]
                        
                        with pd.ExcelWriter(output, engine='openpyxl') as writer:
                            df_export.to_excel(writer, index=False, sheet_name='원장')
                        output.seek(0)
                        return output.getvalue()
                    
                    excel_data = to_excel(df_filtered)
                    filename = f"원장_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
                    st.download_button(
                        label="📥 엑셀 다운로드",
                        data=excel_data,
                        file_name=filename,
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        use_container_width=True
                    )
                
                st.dataframe(
                    df_filtered_kr,
                    use_container_width=True,
                    hide_index=True,
                    height=400
                )
                
                # 통계
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("전체", len(df_display))
                with col2:
                    st.metric("필터링 결과", len(df_filtered))
                with col3:
                    if 'status' in df_filtered.columns:
                        in_progress = len(df_filtered[df_filtered['status'] == '진행 중'])
                        st.metric("진행 중", in_progress)
                    else:
                        st.metric("진행 중", 0)
                with col4:
                    if 'status' in df_filtered.columns:
                        completed = len(df_filtered[df_filtered['status'] == '출하 완료'])
                        st.metric("완료", completed)
                    else:
                        st.metric("완료", 0)
            else:
                st.info("필터 조건에 맞는 데이터가 없습니다.")
        else:
            st.info("등록된 요청이 없습니다.")
    
    # 새 요청 등록
    elif view_option == "새 요청 등록":
        st.header("➕ 새 샘플 요청 등록")
        
        # 엑셀 업로드 탭 추가
        tab1, tab2 = st.tabs(["📝 개별 등록", "📤 엑셀 일괄 등록"])
        
        with tab1:
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
        
        with tab2:
            st.subheader("📤 엑셀 파일로 일괄 등록")
            st.info("💡 엑셀 파일 형식: 번호, 접수일, 회사명, 부서, 요청자, 차종, 품번, 부품명, 수량, 납기일, 상태, 자재완료일, 납품일, 대금회수")
            
            uploaded_file = st.file_uploader(
                "엑셀 파일 선택 (.xlsx, .xls)",
                type=['xlsx', 'xls'],
                help="엑셀 파일을 업로드하면 일괄 등록됩니다."
            )
            
            if uploaded_file is not None:
                try:
                    # 엑셀 파일 읽기
                    df_upload = pd.read_excel(uploaded_file)
                    
                    # 컬럼명 한글 -> 영어 매핑
                    column_mapping = {
                        '번호': 'id',
                        '접수일': 'requestDate',
                        '회사명': 'companyName',
                        '부서': 'department',
                        '요청자': 'contactPerson',
                        '차종': 'carModel',
                        '품번': 'partNumber',
                        '부품명': 'partName',
                        '수량': 'quantity',
                        '납기일': 'dueDate',
                        '상태': 'status',
                        '자재완료일': 'sampleCompletionDate',
                        '납품일': 'shipDate',
                        '대금회수': 'paymentStatus'
                    }
                    
                    # 컬럼명 변환
                    df_upload.columns = [column_mapping.get(col, col) for col in df_upload.columns]
                    
                    # 미리보기
                    st.subheader("📋 업로드 데이터 미리보기")
                    st.dataframe(df_upload, use_container_width=True, hide_index=True)
                    
                    if st.button("✅ 일괄 등록", type="primary", use_container_width=True):
                        # 기존 최대 ID 찾기
                        max_id = max([r['id'] for r in st.session_state.requests], default=0)
                        
                        # 데이터 변환 및 추가
                        added_count = 0
                        for idx, row in df_upload.iterrows():
                            try:
                                # 필수 필드 확인
                                if pd.notna(row.get('companyName')) and pd.notna(row.get('partNumber')):
                                    new_id = max_id + idx + 1
                                    
                                    # 날짜 형식 변환
                                    def format_date(val):
                                        if pd.isna(val) or val == '':
                                            return ''
                                        if isinstance(val, str):
                                            return val
                                        if hasattr(val, 'strftime'):
                                            return val.strftime('%Y-%m-%d')
                                        return str(val)
                                    
                                    new_request = {
                                        'id': int(new_id),
                                        'requestDate': format_date(row.get('requestDate', datetime.now().date())),
                                        'companyName': str(row.get('companyName', '')),
                                        'department': str(row.get('department', '')) if pd.notna(row.get('department')) else '',
                                        'contactPerson': str(row.get('contactPerson', '')) if pd.notna(row.get('contactPerson')) else '',
                                        'carModel': str(row.get('carModel', '')) if pd.notna(row.get('carModel')) else '',
                                        'partNumber': str(row.get('partNumber', '')),
                                        'partName': str(row.get('partName', '')) if pd.notna(row.get('partName')) else '',
                                        'quantity': int(row.get('quantity', 1)) if pd.notna(row.get('quantity')) else 1,
                                        'dueDate': format_date(row.get('dueDate')),
                                        'requirements': str(row.get('requirements', '')) if pd.notna(row.get('requirements')) else '',
                                        'status': str(row.get('status', '접수 대기')) if pd.notna(row.get('status')) else '접수 대기',
                                        'drawingStatus': format_date(row.get('drawingStatus', '')),
                                        'materialRequestDate': str(row.get('materialRequestDate', '')) if pd.notna(row.get('materialRequestDate')) else '',
                                        'expectedCompletionDate': format_date(row.get('expectedCompletionDate', '')),
                                        'materialArrivalDate': str(row.get('materialArrivalDate', '')) if pd.notna(row.get('materialArrivalDate')) else '',
                                        'sampleCompletionDate': format_date(row.get('sampleCompletionDate', '')),
                                        'shipDate': format_date(row.get('shipDate', '')),
                                        'paymentStatus': str(row.get('paymentStatus', '')) if pd.notna(row.get('paymentStatus')) else '',
                                        'remarks': str(row.get('remarks', '')) if pd.notna(row.get('remarks')) else '',
                                    }
                                    
                                    st.session_state.requests.append(new_request)
                                    added_count += 1
                            except Exception as e:
                                st.warning(f"행 {idx + 1} 처리 중 오류: {str(e)}")
                                continue
                        
                        if added_count > 0:
                            st.success(f"✅ {added_count}건의 샘플 요청이 등록되었습니다!")
                            st.rerun()
                        else:
                            st.error("등록된 데이터가 없습니다. 필수 필드(회사명, 품번)를 확인해주세요.")
                
                except Exception as e:
                    st.error(f"엑셀 파일 읽기 오류: {str(e)}")
                    st.info("💡 엑셀 파일 형식을 확인해주세요. 다운로드한 엑셀 파일 형식을 참고하세요.")
    

# 메인 실행
if not st.session_state.authenticated:
    login_page()
else:
    main_dashboard()


