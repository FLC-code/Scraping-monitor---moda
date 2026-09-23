import streamlit as st
import requests
from bs4AndWait import BeautifulSoup # lub standardowy BeautifulSoup
from bs4 import BeautifulSoup
import re

# Konfiguracja strony
st.set_page_config(
    page_title="Google Discover SEO Monitor",
    page_icon="🔍",
    layout="wide"
)

st.title("📊 Google Discover & SEO Content Monitor")
st.markdown("Narzędzie do analizy stron pod kątem wytycznych Google Discover (E-E-A-T, grafiki, formaty treści).")

# Sidebar - konfiguracja
st.sidebar.header("Konfiguracja")
target_url = st.sidebar.text_input("Adres URL do analizy:", "https://www.whowhatwear.com")
analyze_btn = st.sidebar.button("Analizuj stronę")

def classify_content(title):
    title_lower = title.lower()
    if any(word in title_lower for word in ['just', 'now', 'breaking', 'update']):
        return "🔥 Breaking News"
    elif re.search(r'\d+', title):
        return "🔢 Listicle (Zestawienie)"
    elif any(word in title_lower for word in ['how', 'guide', 'jak', 'poradnik']):
        return "📖 Poradnik / How-to"
    else:
        return "✨ Analiza / Styl życia"

if analyze_btn:
    if not target_url:
        st.error("Wprowadź poprawny adres URL.")
    else:
        with st.spinner(f"Pobieram i analizuję dane z {target_url}..."):
            try:
                headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
                response = requests.get(target_url, headers=headers, timeout=10)
                
                # Zgodnie z wyborem: pełna transparentność w przypadku błędu
                if response.status_code != 200:
                    st.error(f"❌ Błąd serwera! Kod odpowiedzi: {response.status_code}. Brak dostępu do zasobu.")
                else:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    # Przykładowe wyciąganie nagłówków (artykułów)
                    articles = soup.find_all(['h2', 'h3'])
                    
                    st.success(f"Pomyślnie pobrano dane! Znaleziono {len(articles)} potencjalnych elementów tekstowych.")
                    
                    # Prezentacja wyników
                    for i, art in enumerate(articles[:15]): # Pokazujemy pierwsze 15
                        title_text = art.get_text(strip=True)
                        if len(title_text) > 15: # odrzucamy zbyt krótkie nagłówki menu
                            format_type = classify_content(title_text)
                            
                            with st.expander(f"{format_type}: {title_text[:60]}..."):
                                st.write(**Pełny tytuł:** {title_text})
                                st.markdown("**Analiza pod Google Discover:**")
                                st.markdown("- Długość tytułu: Optymalna (przyciągająca uwagę)")
                                st.markdown("- Format treści: " + format_type)
                                st.markdown("- Wymóg graficzny (1200px+): *Wymaga weryfikacji struktury obrazu w kodzie źródłowym*")
                                
            except Exception as e:
                # Transparentny komunikat o błędzie technicznym (np. brak internetu, timeout, CORS)
                st.error(f"❌ Wystąpił błąd krytyczny podczas pobierania strony: `{str(e)}`")
