import streamlit as st
import requests
import xml.etree.ElementTree as ET

st.set_page_config(page_title="Who What Wear Discover Monitor", page_icon="✨", layout="wide")

st.title("✨ Who What Wear - Monitor Sitemap & Discover")
st.markdown("Automatyczny monitor najnowszych publikacji ze strony **whowhatwear.com**.")

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
                    urls.append({
                        "url": loc.text,
                        "lastmod": lastmod.text if lastmod is not None else "Brak daty"
                    })
            return urls
    except Exception as e:
        st.error(f"Błąd pobierania sitemapy: {e}")
    return []

data = fetch_sitemap()

if data:
    st.success(f"Pomyślnie pobrano {len(data)} adresów z sitemapy whowhatwear.com!")
    st.subheader("Ostatnie wpisy z sitemapy:")
    for item in data[:20]:
        st.markdown(f"- [{item['url']}]({item['url']}) *(Ostatnia modyfikacja: {item['lastmod']})*")
else:
    st.warning("Nie udało się pobrać danych z sitemapy.")
