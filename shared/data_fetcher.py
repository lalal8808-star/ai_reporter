import yfinance as yf # yfinance를 사용하여 Yahoo Finance에서 데이터를 가져옵니다.
import pandas as pd # pandas를 사용하여 데이터를 처리합니다.
import FinanceDataReader as fdr # FinanceDataReader를 사용하여 한국 주식 데이터를 가져옵니다.

def fetch_stock_data(ticker, period="1mo"): # 티커(심볼)의 주가 데이터를 가져옵니다. 
    """
    지정한 티커(심볼)의 주가 데이터를 가져옵니다. 
    ticker: 종목 코드 (예: AAPL, 005930.KS)
    period: 데이터 기간 (1mo, 6mo, 1y, max 등)
    """
    print(f"📡 {ticker}의 데이터를 가져오는 중...")
    
    # 1. 데이터 다운로드
    # yfinance를 사용하여 Yahoo Finance에서 데이터를 긁어옵니다.
    # 결과는 파이썬 데이터 분석의 핵심인 'DataFrame'(표 형태)으로 반환됩니다.
    df = yf.download(ticker, period=period)
    
    if df.empty:
        print(f"❌ {ticker} 데이터를 찾을 수 없습니다. 티커를 확인해 주세요.")
        return None
    
    # yfinance 0.2.x 이상에서 단일 종목 요청 시 컬럼이 MultiIndex(Price, Ticker)가 되는 경우가 있습니다.
    # 대시보드 코드가 헷갈리지 않게 'Price'만 남기고 컬럼을 단순하게 정리합니다.
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
        
    return df

def get_krx_tickers():
    """
    한국 거래소(KRX)의 전 종목 리스트를 가져옵니다.
    """
    try:
        df = fdr.StockListing('KRX')
        # 'Code'와 'Name'을 합쳐서 리스트를 만듭니다. (예: 005930 - 삼성전자)
        # yfinance용 기호를 만들기 위해 시장 구분(KOSPI/KOSDAQ) 정보를 활용합니다.
        ticker_list = []
        for _, row in df.iterrows(): # df.iterrows()는 DataFrame의 각 행을 순회합니다.
            market = ".KS" if row['Market'] == 'KOSPI' else ".KQ" # 시장 구분(KOSPI/KOSDAQ) 정보를 활용합니다.
            display_name = f"{row['Code']}{market} - {row['Name']}" # 티커와 이름을 합쳐서 리스트를 만듭니다.
            ticker_list.append(display_name)
        return ticker_list
    except Exception as e:
        print(f"❌ 종목 리스트를 가져오는 중 오류 발생: {e}")
        return []

def get_krx_etfs():
    """
    한국 거래소(KRX)의 ETF 리스트를 가져옵니다.
    """
    try:
        print("📡 한국 ETF 리스트를 가져오는 중...")
        df = fdr.StockListing('ETF/KR')
        ticker_list = []
        for _, row in df.iterrows():
            # ETF는 보통 .KS(코스피)에 상장되어 있습니다. 
            # FinanceDataReader의 ETF/KR 리스트는 'Symbol'과 'Name' 컬럼을 가집니다.
            display_name = f"{row['Symbol']}.KS - {row['Name']}"
            ticker_list.append(display_name)
        return ticker_list
    except Exception as e:
        print(f"❌ 한국 ETF 리스트를 가져오는 중 오류 발생: {e}")
        return []

def get_us_tickers():
    """
    미국 거래소(NASDAQ, NYSE)의 전 종목 리스트를 가져옵니다.
    """
    try:
        # 주요 시장 리스트 (NASDAQ, NYSE)
        exchanges = ['NASDAQ', 'NYSE']
        ticker_list = []
        
        for ex in exchanges:
            print(f"📡 {ex} 종목 리스트를 가져오는 중...")
            df = fdr.StockListing(ex)
            for _, row in df.iterrows():
                # 'Symbol'과 'Name'을 합침 (예: AAPL - Apple)
                display_name = f"{row['Symbol']} - {row['Name']}"
                ticker_list.append(display_name)
        return ticker_list
    except Exception as e:
        print(f"❌ 미국 종목 리스트를 가져오는 중 오류 발생: {e}")
        # 오류 시 기본 인기 종목이라도 반환하여 사용 중단을 방지합니다.
        return ["AAPL - Apple", "TSLA - Tesla", "NVDA - NVIDIA", "MSFT - Microsoft", "GOOGL - Google", "AMZN - Amazon"]

def get_us_etfs():
    """
    미국 시장의 ETF 리스트를 가져옵니다.
    """
    try:
        print("📡 미국 ETF 리스트를 가져오는 중...")
        df = fdr.StockListing('ETF/US')
        ticker_list = []
        for _, row in df.iterrows():
            # 미국 ETF (SPY, QQQ 등)
            display_name = f"{row['Symbol']} - {row['Name']}"
            ticker_list.append(display_name)
        return ticker_list
    except Exception as e:
        print(f"❌ 미국 ETF 리스트를 가져오는 중 오류 발생: {e}")
        return ["SPY - SPDR S&P 500 ETF Trust", "QQQ - Invesco QQQ Trust"]

def add_technical_indicators(df):
    """
    데이터프레임에 기술적 지표를 추가합니다.
    """
    if df is None or df.empty:
        return None
    
    # 2. 이동평균선(Moving Average) 계산
    # .rolling(window=20)은 '최근 20개 데이터를 묶어서'라는 뜻입니다.
    # .mean()은 그 20개의 평균을 내라는 뜻입니다.
    # 이를 통해 주가의 부드러운 흐름을 볼 수 있습니다. (MA20)
    df['MA20'] = df['Close'].rolling(window=20).mean()
    
    # 전일 대비 등락폭 계산
    df['Daily_Change'] = df['Close'].diff()
    
    return df

if __name__ == "__main__": # 테스트용 코드
    # 테스트: 애플(AAPL) 주가 데이터 가져오기
    # 분석을 위해 기간을 조금 더 넉넉히(6개월) 가져옵니다.
    ticker_symbol = "AAPL"
    data = fetch_stock_data(ticker_symbol, period="6mo")
    
    if data is not None:
        # 분석 기능 실행!
        data = add_technical_indicators(data)
        
        print("\n--- 분석 데이터 (최근 5행) ---")
        # 데이터프레임의 끝부분을 보여주는 .tail()을 써봅시다.
        print(data[['Close', 'MA20', 'Daily_Change']].tail())
