import streamlit as st # Streamlit 라이브러리 import
import sys # 시스템 모듈 import
import os # 운영체제 모듈 import

# 부모 디렉토리의 stock_dashboard 폴더를 참조할 수 있도록 설정합니다.
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))

from stock_dashboard import data_fetcher
import news_scraper
import report_engine
import plotly.graph_objects as go

# --- UI 설정 ---
st.set_page_config(page_title="🤖 AI Financial Advisor", layout="wide")

st.title("🤖 AI Financial Report Generator")
st.markdown("주가 데이터와 실시간 뉴스를 결합하여 AI가 전문적인 투자 리포트를 작성합니다.")

# --- 데이터 캐싱 (종목 리스트) ---
@st.cache_data
def load_all_tickers():
    # 1. 한국 종목 및 ETF 가져오기
    krx_list = data_fetcher.get_krx_tickers()
    kr_etfs = data_fetcher.get_krx_etfs()
    
    # 2. 미국 종목 및 ETF 가져오기
    us_list = data_fetcher.get_us_tickers()
    us_etfs = data_fetcher.get_us_etfs()
    
    # 3. 리스트 합치기
    return us_list + us_etfs + krx_list + kr_etfs

# --- 사이드바: 설정 ---
with st.sidebar:
    st.header("⚙️ 설정")
    all_tickers = load_all_tickers()
    
    # 세션 상태로 선택 박스 값 관리
    def on_ticker_change():
        # 종목이 바뀌면 기존에 생성된 리스트와 리포트 상태를 초기화합니다.
        if "current_report" in st.session_state:
            del st.session_state.current_report

    selected_full = st.selectbox(
        "🔎 분석할 종목 선택", 
        all_tickers, 
        index=None, 
        placeholder="종목명 또는 심볼 검색...",
        key="ticker_choice",
        on_change=on_ticker_change
    )
    
    period = st.selectbox("데이터 기간", ["1mo", "3mo", "6mo", "1y", "max"], index=1)
    
    st.divider()
    st.info("💡 종목을 선택하면 차트와 최신 뉴스, 그리고 AI 리포트 분석이 시작됩니다.")

# --- 메인 로직 ---
if selected_full:
    ticker = selected_full.split(" - ")[0]
    stock_name = selected_full.split(" - ")[1]
    
    # 1. 데이터 가져오기
    with st.spinner("데이터를 로드하는 중..."):
        df = data_fetcher.fetch_stock_data(ticker, period=period)
        
    if df is not None and not df.empty:
        df = data_fetcher.add_technical_indicators(df)
        
        # 레이아웃 구성: 왼쪽(차트/뉴스), 오른쪽(AI 리포트)
        col_left, col_right = st.columns([1.2, 0.8])
        
        with col_left:
            st.subheader(f"📈 {stock_name} ({ticker}) 주가 흐름")
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=df.index, y=df['Close'], name='종가', line=dict(color='#00CC96', width=2)))
            fig.add_trace(go.Scatter(x=df.index, y=df['MA20'], name='MA20', line=dict(color='#EF553B', width=1.5, dash='dot')))
            fig.update_layout(template="plotly_dark", height=400, margin=dict(l=0, r=0, t=20, b=0))
            st.plotly_chart(fig, use_container_width=True)
            
            # 뉴스 분석 결과
            st.subheader("📰 최신 관련 뉴스")
            news_data = news_scraper.get_stock_news(stock_name)
            if news_data:
                for n in news_data:
                    st.markdown(f"- [{n['title']}]({n['link']})")
            else:
                st.write("관련 뉴스를 찾을 수 없습니다.")

        with col_right:
            st.subheader("🤖 AI 전문 분석 리포트")
            
            # 리포트 생성 버튼 (과도한 API 호출 방지)
            if st.button("✨ 리포트 생성/갱신하기", use_container_width=True):
                with st.spinner("AI 분석가가 리포트를 작성 중입니다..."):
                    report = report_engine.generate_financial_report(stock_name, df, news_data)
                    st.session_state.current_report = report
            
            # 리포트 표시
            if "current_report" in st.session_state and st.session_state.ticker_choice == selected_full:
                st.markdown("---")
                st.markdown(st.session_state.current_report)
                
                # 저장/복사 버튼 안내
                st.caption("💡 리포트 내용을 드래그하여 복사할 수 있습니다.")
            else:
                st.warning("상단의 '리포트 생성' 버튼을 눌러 AI의 분석을 확인하세요.")

    else:
        st.error("데이터를 가져오는 중 오류가 발생했습니다.")
else:
    # 웰컴 화면
    st.container()
    st.info("👈 왼쪽 사이드바에서 분석을 시작할 종목을 선택해 주세요.")
    st.image("https://images.unsplash.com/photo-1590283603385-17ffb3a7f29f?auto=format&fit=crop&q=80&w=1000", caption="Comprehensive AI Financial Analysis")

# --- 푸터 ---
st.divider()
st.caption("© 2026 AI Financial Advisor - Powered by Gemini AI & Streamlit")
