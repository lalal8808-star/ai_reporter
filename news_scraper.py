import requests
from bs4 import BeautifulSoup # BeautifulSoup 라이브러리 import

def get_stock_news(query):
    """
    네이버 뉴스 검색을 통해 특정 종목의 최신 뉴스를 가져옵니다.
    query: 검색어 (예: 삼성전자, 애플, 테슬라)
    """
    print(f"📡 '{query}' 관련 뉴스를 찾는 중...")
    
    # 네이버 뉴스 검색 URL (최신순 정렬: &sort=1)
    url = f"https://search.naver.com/search.naver?where=news&query={query}&sort=1"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    } # User-Agent 설정
    
    try:
        response = requests.get(url, headers=headers)
        response.encoding = 'utf-8'
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser") # BeautifulSoup 객체 생성
            
            # 네이버 검색 뉴스 아이템 추출
            # .news_tit는 최신 UI에서 사라졌을 수 있습니다. 
            # 더 안정적인 'a[data-heatmap-target=".tit"]' 셀렉터를 사용합니다.
            news_items = soup.select('a[data-heatmap-target=".tit"]')
            
            results = []
            for item in news_items[:10]: # 최신 뉴스 5개만 추출
                title = item.get_text().strip() # 제목 추출
                link = item.get("href") # 링크 추출
                results.append({"title": title, "link": link})
            
            return results
        else:
            print(f"❌ 뉴스 검색 실패 (상태 코드: {response.status_code})")
            return []
            
    except Exception as e:
        print(f"❌ 뉴스 스크래핑 중 오류 발생: {e}")
        return []

if __name__ == "__main__":
    # 테스트: 삼성전자 뉴스 가져오기
    search_term = "삼성전자"
    news = get_stock_news(search_term)
    
    if news:
        print(f"\n--- '{search_term}' 최신 뉴스 ---")
        for i, n in enumerate(news, 1):
            print(f"{i}. {n['title']}") # 뉴스 제목 출력
            print(f"   링크: {n['link']}") # 뉴스 링크 출력
    else:
        print("검색된 뉴스가 없습니다.")
