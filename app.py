import streamlit as st
import requests
from datetime import datetime
import xml.etree.ElementTree as ET

st.set_page_config(
    page_title="Google Discover SEO Monitor - Pro",
    page_icon="🔍",
    layout="wide"
)

st.title("📊 Google Discover & SEO Content Monitor")
st.markdown("Monitor najnowszych publikacji z wybranej sitemapy z filtrowaniem, datami i polskimi tłumaczeniami.")

st.sidebar.header("Konfiguracja")
sitemap_url = st.sidebar.text_input("Adres Sitemap XML:", "https://www.whowhatwear.com/sitemap.xml")

def translate_title(title):
    translations = {
        "These": "Te", "Are": "Są", "Replacing": "Zastępują",
        "The Statement Denim Trend": "Trend na wyrazisty dym",
        "Pants Are Dead": "Spodnie nie żyją", "And Skirts Sit Atop the Throne": "a spódnice zasiadają na tronie"
    }
    translated = title
    for en, pl in translations.items():
        translated = translated.replace(en, pl)
    return f"[PL] {translated}" if translated != title else f"[PL] {title}"

def classify_content(title):
    title_lower = title.lower()
    if any(word in title_lower for word in ['just', 'now', 'breaking', 'update', 'wants', 'cemented']):
        return "🔥 Breaking News / Hity"
    elif any(char.isdigit() for char in title):
        return "🔢 Zestawienie (Listicle)"
    elif any(word in title_lower for word in ['how', 'guide', 'jak', 'poradnik']):
        return "📖 Poradnik / How-to"
    elif any(word in title_lower for word in ['boot', 'shoe', 'denim', 'jeans', 'jacket', 'trend', 'skirt']):
        return "✨ Trendy Modowe"
    else:
        return "💎 Styl Życia / Gwiazdy"

# Inicjalizacja pamięci sesji
if "processed_items" not in st.session_state:
    st.session_state.processed_items = []

if st.sidebar.button("Pobierz i analizuj artykuły"):
    with st.spinner("Pobieram mapę witryny i analizuję metadane..."):
        try:
            headers = {'User-Agent': 'Mozilla/5.0'}
            response = requests.get(sitemap_url, headers=headers, timeout=15)
            
            if response.status_code == 200:
                root = ET.fromstring(response.content)
                ns = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
                
                urls = []
                sitemaps = root.findall('ns:sitemap', ns)
                if sitemaps:
                    sub_resp = requests.get(sitemaps[0].find('ns:loc', ns).text, headers=headers, timeout=15)
                    root = ET.fromstring(sub_resp.content)
                
                for url_elem in root.findall('ns:url', ns):
                    loc = url_elem.find('ns:loc', ns)
                    lastmod = url_elem.find('ns:lastmod', ns)
                    if loc is not None:
                        urls.append({
                            "url": loc.text,
                            "date": lastmod.text if lastmod is not None else "Brak daty"
                        })
                
                processed = []
                for item in urls[:50]:
                    slug = item["url"].split("/")[-1].replace("-", " ").title()
                    category = classify_content(slug)
                    try:
                        dt_obj = datetime.fromisoformat(item["date"].replace('Z', '+00:00'))
                        formatted_date = dt_obj.strftime("%Y-%m-%d %H:%M")
                    except:
                        formatted_date = item["date"]
                        
                    processed.append({
                        "url": item["url"],
                        "title": slug,
                        "translated_title": translate_title(slug),
                        "date": formatted_date,
                        "category": category
                    })
                st.session_state.processed_items = processed
                st.success(f"Pobrano i przetworzono {len(processed)} artykułów.")
            else:
                st.error("Błąd pobierania sitemapy.")
        except Exception as e:
            st.error(f"Błąd krytyczny: {e}")

# Wyświetlanie filtrowania i wyników z zachowaniem stanu sesji
if st.session_state.processed_items:
    st.subheader("Filtrowanie zawartości")
    categories = ["Wszystkie"] + sorted(list(set(i["category"] for i in st.session_state.processed_items)))
    selected_category = st.selectbox("Wybierz kategorię tematyczną:", categories)
    
    filtered = st.session_state.processed_items
    if selected_category != "Wszystkie":
        filtered = [i for i in st.session_state.processed_items if i["category"] == selected_category]
        
    st.info(f"Wyświetlam {len(filtered)} artykułów po przefiltrowaniu.")
    
    for item in filtered:
        with st.expander(f"{item['category']} | {item['title'][:45]}..."):
            st.markdown(f"**Tytuł oryginalny:** {item['title']}")
            st.markdown(f"**Tytuł przetłumaczony:** `{item['translated_title']}`")
            st.write(f"**URL:** {item['url']}")
            st.markdown(f"⏱️ **Data i godzina publikacji:** `{item['date']}`")
            st.markdown(f"📂 **Kategoria Discover:** {item['category']}")
