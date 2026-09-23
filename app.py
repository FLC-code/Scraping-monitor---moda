import streamlit as st
import requests
from datetime import datetime
import xml.etree.ElementTree as ET

st.set_page_config(
    page_title="Google Discover SEO Monitor - Multi-Site Pro",
    page_icon="🔍",
    layout="wide"
)

st.title("📊 Google Discover & SEO Content Monitor")
st.markdown("Monitor najnowszych publikacji z wiodących serwisów modowych i lifestyle'owych pod kątem Google Discover.")

# Sidebar - Wybór serwisu
st.sidebar.header("Konfiguracja Monitora")

sites = {
    "Who What Wear": "https://www.whowhatwear.com/sitemap.xml",
    "Harper's Bazaar": "https://www.harpersbazaar.com/sitemap.xml",
    "Vogue UK": "https://www.vogue.co.uk/sitemap.xml",
    "Elle": "https://www.elle.com/sitemap.xml",
    "Cosmopolitan": "https://www.cosmopolitan.com/sitemap.xml",
    "Marie Claire": "https://www.marieclaire.com/sitemap.xml"
}

selected_site_name = st.sidebar.selectbox("Wybierz serwis do analizy:", list(sites.keys()))
sitemap_url = sites[selected_site_name]

# Możliwość wpisania własnego linku opcjonalnie
custom_sitemap = st.sidebar.text_input("Lub podaj własny adres sitemap.xml:", sitemap_url)
if custom_sitemap:
    sitemap_url = custom_sitemap

def translate_title(title):
    dictionary = {
        "Trend": "Trend", "Boot": "Buty", "Boots": "Buty", "Shoe": "Buty", "Shoes": "Buty",
        "Denim": "Dżinsy", "Jeans": "Dżinsy", "Jacket": "Kurtka", "Skirt": "Spódnica",
        "Pants": "Spodnie", "Bag": "Torebka", "Bags": "Torebki", "Sweater": "Sweter",
        "Sweaters": "Swetry", "Nails": "Paznokcie", "Blush": "Róż do policzków",
        "Outfit": "Stylizacja", "Outfits": "Stylizacje", "Fall": "Jesienne",
        "Winter": "Zimowe", "Spring": "Wiosenne", "Summer": "Letnie",
        "Style": "Styl", "Celebrity": "Gwiazda", "Red Carpet": "Czerwony Dywan",
        "Wearing": "noszenia", "Are Replacing": "zastępują", "The Best": "Najlepsze",
        "How To": "Jak", "Why": "Dlaczego"
    }

    translated = title
    for en, pl in dictionary.items():
        translated = translated.replace(en, pl)
        translated = translated.replace(en.lower(), pl.lower())

    if "Trend" in translated and not translated.startswith("Trend"):
        parts = translated.split(" Trend")
        if len(parts) == 2 and parts[1].strip():
            translated = f"Trend na: {parts[0]} ({parts[1].strip()})"
        else:
            translated = f"Trend: {parts[0]}"
            
    return f"[PL] {translated}"

def classify_content(title):
    title_lower = title.lower()
    if any(word in title_lower for word in ['just', 'now', 'breaking', 'update', 'wants', 'cemented', 'exclusive']):
        return "🔥 Breaking News / Hity"
    elif any(char.isdigit() for char in title):
        return "🔢 Zestawienie (Listicle)"
    elif any(word in title_lower for word in ['how', 'guide', 'jak', 'poradnik']):
        return "📖 Poradnik / How-to"
    elif any(word in title_lower for word in ['boot', 'shoe', 'denim', 'jeans', 'jacket', 'trend', 'skirt', 'nails', 'blush']):
        return "✨ Trendy Modowe"
    else:
        return "💎 Styl Życia / Gwiazdy"

# Inicjalizacja pamięci sesji
if "processed_items" not in st.session_state:
    st.session_state.processed_items = []
if "current_site" not in st.session_state:
    st.session_state.current_site = ""

if st.sidebar.button("Pobierz i analizuj artykuły"):
    with st.spinner(f"Pobieram sitemapę dla {selected_site_name}..."):
        try:
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            response = requests.get(sitemap_url, headers=headers, timeout=15)
            
            if response.status_code == 200:
                root = ET.fromstring(response.content)
                
                # Obsługa namespace'ów i sitemap indeksowych
                ns_uri = root.tag.split('}')[0].strip('{') if '}' in root.tag else 'http://www.sitemaps.org/schemas/sitemap/0.9'
                ns = {'ns': ns_uri}
                
                urls = []
                sitemaps = root.findall('ns:sitemap', ns)
                
                # Jeśli to sitemap index, pobieramy pierwszą podmapę (zazwyczaj najświeższą)
                if sitemaps:
                    sub_sitemap_elem = sitemaps[0].find('ns:loc', ns)
                    if sub_sitemap_elem is not None:
                        sub_resp = requests.get(sub_sitemap_elem.text, headers=headers, timeout=15)
                        if sub_resp.status_code == 200:
                            root = ET.fromstring(sub_resp.content)
                            ns_uri = root.tag.split('}')[0].strip('{') if '}' in root.tag else ns_uri
                            ns = {'ns': ns_uri}
                
                for url_elem in root.findall('ns:url', ns):
                    loc = url_elem.find('ns:loc', ns)
                    lastmod = url_elem.find('ns:lastmod', ns)
                    if loc is not None and loc.text:
                        urls.append({
                            "url": loc.text,
                            "date": lastmod.text if lastmod is not None and lastmod.text else "Brak daty"
                        })
                
                processed = []
                # Przetwarzamy do 60 najnowszych wpisów
                for item in urls[:60]:
                    clean_url = item["url"]
                    slug_part = clean_url.rstrip("/").split("/")[-1]
                    slug = slug_part.replace("-", " ").replace("_", " ").title()
                    
                    # Jeśli slug jest pusty lub jest domeną, bierzemy przedostatni człon
                    if not slug or len(slug) < 3:
                        parts = [p for p in clean_url.split("/") if p]
                        if len(parts) >= 2:
                            slug = parts[-2].replace("-", " ").title()
                            
                    category = classify_content(slug)
                    
                    # Formatowanie daty
                    raw_date = item["date"]
                    try:
                        dt_obj = datetime.fromisoformat(raw_date.replace('Z', '+00:00'))
                        formatted_date = dt_obj.strftime("%Y-%m-%d %H:%M")
                    except:
                        formatted_date = raw_date
                        
                    processed.append({
                        "url": clean_url,
                        "title": slug,
                        "translated_title": translate_title(slug),
                        "date": formatted_date,
                        "category": category
                    })
                    
                st.session_state.processed_items = processed
                st.session_state.current_site = selected_site_name
                st.success(f"Pobrano i przeanalizowano {len(processed)} artykułów z {selected_site_name}!")
            else:
                st.error(f"Błąd pobierania sitemapy. Kod: {response.status_code}")
        except Exception as e:
            st.error(f"Błąd krytyczny podczas parsowania: {e}")

# Wyświetlanie wyników, jeśli są w sesji
if st.session_state.processed_items:
    st.markdown(f"### Aktualnie analizowany serwis: `{st.session_state.current_site}`")
    st.subheader("Filtrowanie zawartości")
    
    categories = ["Wszystkie"] + sorted(list(set(i["category"] for i in st.session_state.processed_items)))
    selected_category = st.selectbox("Wybierz kategorię tematyczną Discover:", categories)
    
    filtered = st.session_state.processed_items
    if selected_category != "Wszystkie":
        filtered = [i for i in st.session_state.processed_items if i["category"] == selected_category]
        
    st.info(f"Wyświetlam {len(filtered)} artykułów po przefiltrowaniu.")
    
    for item in filtered:
        with st.expander(f"{item['category']} | {item['title'][:50]}..."):
            st.markdown(f"**Tytuł oryginalny:** {item['title']}")
            st.markdown(f"**Tytuł przetłumaczony:** `{item['translated_title']}`")
            st.write(f"**URL:** {item['url']}")
            st.markdown(f"⏱️ **Data i godzina publikacji:** `{item['date']}`")
            st.markdown(f"📂 **Kategoria Discover:** {item['category']}")
            st.markdown("---")
            st.markdown("**Analiza pod Google Discover:**")
            st.markdown("- Potencjał algorytmiczny: Wysoki (serwis wspierany w kanałach feedowych)")
            st.markdown("- Optymalizacja mobilna i graficzna: Wymagana weryfikacja tagu `max-image-preview:large`")
