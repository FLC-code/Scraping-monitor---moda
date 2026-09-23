import streamlit as st
import requests
import xml.etree.ElementTree as ET
from datetime import datetime

# Konfiguracja strony
st.set_page_config(
    page_title="Who What Wear - Discover & SEO Monitor", 
    page_icon="✨", 
    layout="wide"
)

st.title("✨ Who What Wear - Monitor Sitemap & Google Discover SEO")
st.markdown("Profesjonalne narzędzie do analizy treści, filtrowania i optymalizacji pod kątem **Google Discover**.")

# Pobieranie sitemapy z cache (odświeżanie co 1 godzinę)
@st.cache_data(ttl=3600)
def fetch_sitemap():
    url = "https://www.whowhatwear.com/sitemap.xml"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            root = ET.fromstring(response.content)
            namespace = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
            urls = []
            for child in root.findall('ns:url', namespace):
                loc = child.find('ns:loc', namespace)
                lastmod = child.find('ns:lastmod', namespace)
                if loc is not None:
                    # Wyciąganie slug-a jako tytułu roboczego
                    url_string = loc.text
                    slug = url_string.split('/')[-1].replace('-', ' ').title()
                    if not slug:
                        slug = "Strona główna / Inne"
                        
                    urls.append({
                        "url": url_string,
                        "title": slug,
                        "lastmod": lastmod.text if lastmod is not None else "Brak daty"
                    })
            return urls
    except Exception as e:
        st.error(f"Błąd pobierania sitemapy: {e}")
    return []

with st.spinner("Pobieranie i analiza sitemapy whowhatwear.com..."):
    data = fetch_sitemap()

if data:
    st.success(f"Pomyślnie załadowano {len(data)} adresów URL z sitemapy!")
    
    # --- PANEL BOCZNY (FILTRY I WYSZUKIWANIE - PUNKT 1) ---
    st.sidebar.header("🔍 Filtry i Wyszukiwanie")
    search_query = st.sidebar.text_input("Szukaj frazy w adresie/tytule:", "").lower()
    
    # Opcja filtrowania tylko najnowszych (PUNKT 2)
    today_str = datetime.now().strftime("%Y-%m-%d")
    only_today = st.sidebar.checkbox("Pokaż tylko dzisiejsze wpisy", value=False)
    
    # Filtrowanie danych
    filtered_data = []
    for item in data:
        match_search = search_query in item['title'].lower() or search_query in item['url'].lower()
        match_date = True
        if only_today:
            match_date = today_str in item['lastmod']
            
        if match_search and match_date:
            filtered_data.append(item)
            
    st.sidebar.markdown(f"Znaleziono pasujących wpisów: **{len(filtered_data)}**")
    
    # --- GŁÓWNA LISTA ORAZ ANALIZA Discover (PUNKT 3) ---
    st.subheader("📋 Lista artykułów i audyt pod Google Discover")
    st.info("Poniżej znajdziesz analizę nagłówków pod kątem algorytmów Google Discover (m.in. długość tytułu, obecność liczb/listicles, chwytliwość).")

    for idx, item in enumerate(filtered_data[:50]): # Wyświetlamy pierwsze 50 pasujących
        with st.expander(f"📌 {item['title']} (Aktualizacja: {item['lastmod']})"):
            st.markdown(ర్శ**Link:** [{item['url']}]({item['url']}))
            
            # Algorytm oceniający nagłówek pod Google Discover (PUNKT 3)
            title_len = len(item['title'])
            has_numbers = any(char.isdigit() for char in item['title'])
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Długość tytułu", f"{title_len} znaków", 
                          delta="Optymalnie (40-75)" if 40 <= title_len <= 75 else "Do poprawy")
            with col2:
                st.metric("Format Listicle (Liczby)", "Tak" if has_numbers else "Brak", 
                          delta="Wysoki CTR w Discover" if has_numbers else "Standard")
            with col3:
                # Szacowany potencjał Discover na podstawie cech nagłówka
                score = 70
                if 40 <= title_len <= 75: score += 15
                if has_numbers: score += 15
                st.metric("Potencjał Discover", f"{score} / 100 pkt")
                
            # Wskazówki SEO dedykowane pod Discover
            if title_len < 40:
                st.warning("⚠️ Tytuł jest stosunkowo krótki. W Discover lepiej sprawdzają się bardziej opisowe i emocjonalne nagłówki.")
            elif title_len > 85:
                st.warning("⚠️ Tytuł może zostać przycięty na urządzeniach mobilnych.")
            else:
                st.success("✅ Długość tytułu idealna pod smartfony.")
                
else:
    st.warning("Nie udało się pobrać danych z sitemapy.")
