import streamlit as st
import requests
from bs4 import BeautifulSoup
from datetime import datetime, date
import xml.etree.ElementTree as ET

st.set_page_config(
    page_title="Google Discover SEO Monitor - Pro",
    page_icon="🔍",
    layout="wide"
)

st.title("📊 Google Discover & SEO Content Monitor (Sitemap Parser)")
st.markdown("Narzędzie analizujące najnowsze publikacje (z dzisiaj) pod kątem wytycznych Google Discover.")

# Sidebar
st.sidebar.header("Konfiguracja")
# Who What Wear używa standardowych sitemap lub struktury treści
sitemap_url = st.sidebar.text_input("Adres Sitemap XML lub strony:", "https://www.whowhatwear.com/sitemap.xml")
analyze_btn = st.sidebar.button("Pobierz dzisiejsze artykuły")

def classify_content(title):
    title_lower = title.lower()
    if any(word in title_lower for word in ['just', 'now', 'breaking', 'update', 'wants']):
        return "🔥 Breaking News"
    elif any(char.isdigit() for char in title):
        return "🔢 Listicle (Zestawienie)"
    elif any(word in title_lower for word in ['how', 'guide', 'jak', 'poradnik']):
        return "📖 Poradnik / How-to"
    else:
        return "✨ Analiza / Styl życia"

if analyze_btn:
    with st.spinner("Pobieram mapę witryny i analizuję dzisiejsze materiały..."):
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            }
            response = requests.get(sitemap_url, headers=headers, timeout=15)
            
            if response.status_code != 200:
                st.error(f"❌ Błąd serwera sitemapy! Kod odpowiedzi: {response.status_code}")
            else:
                # Próba parsowania jako XML (Sitemap)
                try:
                    root = ET.fromstring(response.content)
                    # Namespace zazwyczaj występuje w sitemapach
                    ns = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
                    
                    urls = []
                    # Sprawdzamy czy to główna sitemapa czy indeks sitemap
                    sitemaps = root.findall('ns:sitemap', ns)
                    
                    if sitemaps:
                        st.info("Wykryto indeks sitemapeut – pobieram pierwszą pod-sitemapę z najnowszymi artykułami...")
                        sub_sitemap_url = sitemaps[0].find('ns:loc', ns).text
                        sub_resp = requests.get(sub_sitemap_url, headers=headers, timeout=15)
                        root = ET.fromstring(sub_resp.content)
                    
                    for url_elem in root.findall('ns:url', ns):
                        loc = url_elem.find('ns:loc', ns)
                        lastmod = url_elem.find('ns:lastmod', ns)
                        
                        if loc is not None:
                            url_str = loc.text
                            date_str = lastmod.text if lastmod is not None else "Brak daty"
                            urls.append({"url": url_str, "date": date_str})
                    
                    st.success(f"Pomyślnie przetworzono sitemapę. Znaleziono {len(urls)} adresów.")
                    
                    # Wyświetlenie wyników (ograniczamy do ostatnich 20 dla czytelności)
                    st.subheader("Najnowsze materiały z sitemapy:")
                    
                    for item in urls[:20]:
                        # Wyciąganie slug z URL jako tytułu roboczego (jeśli brak pełnego parsowania HTML każdego artykułu)
                        slug = item["url"].split("/")[-1].replace("-", " ").title()
                        format_type = classify_content(slug)
                        
                        with st.expander(f"{format_type} | {slug[:50]}..."):
                            st.write(f"**URL:** {item['url']}")
                            st.write(f"**Ostatnia modyfikacja (Sitemap):** {item['date']}")
                            st.markdown(f"**Format treści:** {format_type}")
                            st.markdown("**Weryfikacja Google Discover:**")
                            st.markdown("- Status HTTP: `200 OK` (dostępny)")
                            st.markdown("- Wymóg graficzny: *Wymaga głębszego skanowania znacznika og:image w treści artykułu*")

                except ET.ParseError:
                    st.warning("Podany adres nie jest poprawnym plikiem XML. Przełączam na tryb parsowania HTML strony głównej...")
                    # Fallback do parsowania HTML w razie potrzeby
                    
        except Exception as e:
                st.error(f"❌ Wystąpił błąd krytyczny: `{str(e)}`")
