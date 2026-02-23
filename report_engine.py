from google import genai # Google GenAI 라이브러리 import
import pandas as pd # 데이터프레임 라이브러리 import

# API 키 설정 (기존 키 사용)
API_KEY = "AIzaSyBPwWz5T-XcvZxCtiNRHPh_ME2fFKQrU4I"
client = genai.Client(api_key=API_KEY)

def generate_financial_report(stock_name, price_data, news_list):
    """
    주가 데이터와 뉴스 목록을 결합하여 AI 리포트를 생성합니다.
    """
    if not news_list:
        news_text = "최근 관련 뉴스가 없습니다."
    else:
        news_text = "\n".join([f"- {n['title']}" for n in news_list]) # 뉴스 헤드라인을 문자열로 변환
    
    # 주가 정보 요약 (최근 종가, 변동폭 등)
    current_price = price_data['Close'].iloc[-1] # 최근 종가
    prev_price = price_data['Close'].iloc[-2] # 전일 종가
    change_pct = ((current_price - prev_price) / prev_price) * 100 # 변동율
    ma20 = price_data['MA20'].iloc[-1] # 20일 이동평균
    
    # AI에게 보낼 프롬프트 구성
    prompt = f"""
    당신은 전문 금융 분석가입니다. 아래 제공된 '{stock_name}'의 주가 데이터와 최신 뉴스를 바탕으로 투자 분석 리포트를 작성해 주세요.
    
    [주가 지표]
    - 현재가: {current_price:,.2f}
    - 전일 대비 변동: {change_pct:+.2f}%
    - 20일 이동평균선(MA20): {ma20:,.2f}
    
    [최신 뉴스 뉴스 헤드라인]
    {news_text}
    
    [리포트 작성 지침]
    1. 현재 주가 흐름(상승/하락/횡보)을 기술적으로 분석해줘.
    2. 최신 뉴스가 주가에 미칠 영향을 분석해줘.
    3. 결론적으로 투자자들이 주의해야 할 점이나 향후 전망을 딱 3문장으로 요약해줘.
    4. 아주 전문적이면서도 신뢰감 있는 말투를 사용해줘.
    """
    
    try:
        print(f"🤖 AI가 '{stock_name}' 리포트를 분석 중입니다...")
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt
        )
        return response.text
        
    except Exception as e:
        if "429" in str(e): # API 사용량 초과
            return "⚠️ AI 사용량이 초과되었습니다. 잠시 후 다시 시도해 주세요."
        return f"⚠️ 리포트 생성 중 오류 발생: {str(e)}"

if __name__ == "__main__":
    # 테스트용 가짜 데이터
    test_stock = "삼성전자"
    # 간단한 데이터프레임 시뮬레이션
    test_data = pd.DataFrame({
        'Close': [70000, 71000],
        'MA20': [69500, 69800]
    })
    test_news = [
        {"title": "삼성전자, 역대급 실적 발표 임박"},
        {"title": "반도체 업황 회복세 뚜렷"}
    ]
    
    report = generate_financial_report(test_stock, test_data, test_news)
    print("\n" + "="*50)
    print(f"📑 {test_stock} AI 분석 리포트")
    print("="*50)
    print(report)
