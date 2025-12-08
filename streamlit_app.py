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

# 로그인 페이지
def login_page():
    st.title("🔐 로그인")
    st.markdown("---")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        role = st.radio("역할 선택", ["관리자", "고객사"], horizontal=True)
        
        if role == "고객사":
            company_name = st.text_input("업체명")
            name = st.text_input("이름")
            if st.button("로그인", type="primary", use_container_width=True):
                if company_name and name:
                    st.session_state.authenticated = True
                    st.session_state.user_role = "CUSTOMER"
                    st.session_state.user_company = company_name
                    st.session_state.user_name = name
                    st.rerun()
        else:
            password = st.text_input("비밀번호", type="password")
            if st.button("로그인", type="primary", use_container_width=True):
                if password == "admin":  # 기본 비밀번호
                    st.session_state.authenticated = True
                    st.session_state.user_role = "ADMIN"
                    st.rerun()
                else:
                    st.error("비밀번호가 올바르지 않습니다.")

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


