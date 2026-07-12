from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup
import re
import logging
import os

app = Flask(__name__)
CORS(app)

# ============================================
# WEBSITE CONFIGURATIONS
# ============================================
MOVIESDA_BASE = "https://moviesda33.com"
MOVIESDA_2026 = "https://moviesda33.com/tamil-2026-movies/"
MOVIESDA_2025 = "https://moviesda33.com/tamil-2025-movies/"
MOVIESDA_2024 = "https://moviesda33.com/tamil-2024-movies/"
MOVIESDA_2023 = "https://moviesda33.com/tamil-2023-movies/"

ISAIDUB_BASE = "https://isaidub.guru"
ISAIDUB_2026 = "https://isaidub.guru/tamil-2026-dubbed-movies/"
ISAIDUB_2025 = "https://isaidub.guru/tamil-2025-dubbed-movies/"
ISAIDUB_2024 = "https://isaidub.guru/tamil-2024-dubbed-movies/"

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)


# ============================================
# HELPER FUNCTIONS
# ============================================

def slugify(text):
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s]+", "-", text)
    return text


def check_url_exists(url):
    try:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        response = requests.head(url, headers=headers, timeout=8, allow_redirects=True)
        return response.status_code == 200
    except:
        return False


def get_year_from_url(url):
    year_match = re.search(r"-(\d{4})-", url)
    if year_match:
        return year_match.group(1)
    return None


def generate_moviesda_urls(movie_name, year=None):
    slug = slugify(movie_name)
    urls = []
    if year:
        urls.append(f"{MOVIESDA_BASE}/{slug}-{year}-tamil-movie/")
        urls.append(f"{MOVIESDA_BASE}/{slug}-{year}/")
        urls.append(f"{MOVIESDA_BASE}/{slug}-{year}-720p-hd-movie/")
        urls.append(f"{MOVIESDA_BASE}/{slug}-{year}-1080p-hd-movie/")
    for y in ["2026", "2025", "2024", "2023", "2022", "2021", "2020", "2019", "2018"]:
        if y != year:
            urls.append(f"{MOVIESDA_BASE}/{slug}-{y}-tamil-movie/")
            urls.append(f"{MOVIESDA_BASE}/{slug}-{y}/")
    urls.append(f"{MOVIESDA_BASE}/{slug}-1080p-hd-movie/")
    urls.append(f"{MOVIESDA_BASE}/{slug}-720p-hd-movie/")
    urls.append(f"{MOVIESDA_BASE}/{slug}-480p-hd-movie/")
    urls.append(f"{MOVIESDA_BASE}/{slug}-1080p-hd-tamil-movie/")
    urls.append(f"{MOVIESDA_BASE}/{slug}-720p-hd-tamil-movie/")
    urls.append(f"{MOVIESDA_BASE}/{slug}-480p-hd-tamil-movie/")
    urls.append(f"{MOVIESDA_BASE}/{slug}-hd-movie/")
    urls.append(f"{MOVIESDA_BASE}/{slug}-hd-movies/")
    urls.append(f"{MOVIESDA_BASE}/{slug}-full-hd-movie/")
    urls.append(f"{MOVIESDA_BASE}/{slug}-tamil-hd-movie/")
    urls.append(f"{MOVIESDA_BASE}/{slug}-full-movie/")
    urls.append(f"{MOVIESDA_BASE}/{slug}-full-movies/")
    urls.append(f"{MOVIESDA_BASE}/{slug}-720p-hd-web-series/")
    urls.append(f"{MOVIESDA_BASE}/{slug}-1080p-hd-web-series/")
    urls.append(f"{MOVIESDA_BASE}/{slug}-480p-hd-web-series/")
    urls.append(f"{MOVIESDA_BASE}/{slug}-hd-web-series/")
    urls.append(f"{MOVIESDA_BASE}/{slug}-web-series/")
    urls.append(f"{MOVIESDA_BASE}/{slug}-season-01-720p-hd-web-series/")
    urls.append(f"{MOVIESDA_BASE}/{slug}-season-01-1080p-hd-web-series/")
    urls.append(f"{MOVIESDA_BASE}/{slug}-season-01/")
    urls.append(f"{MOVIESDA_BASE}/{slug}/")
    return urls


def generate_isaidub_urls(movie_name, year=None):
    slug = slugify(movie_name)
    urls = []
    if year:
        urls.append(f"{ISAIDUB_BASE}/movie/{slug}-{year}-tamil-dubbed-web-series/")
        urls.append(f"{ISAIDUB_BASE}/movie/{slug}-{year}-tamil-dubbed-movie/")
        urls.append(f"{ISAIDUB_BASE}/movie/{slug}-{year}-tamil-dubbed/")
    for y in ["2026", "2025", "2024", "2023", "2022", "2021", "2020", "2019", "2018"]:
        if y != year:
            urls.append(f"{ISAIDUB_BASE}/movie/{slug}-{y}-tamil-dubbed-web-series/")
            urls.append(f"{ISAIDUB_BASE}/movie/{slug}-{y}-tamil-dubbed-movie/")
            urls.append(f"{ISAIDUB_BASE}/movie/{slug}-{y}-tamil-dubbed/")
    urls.append(f"{ISAIDUB_BASE}/movie/{slug}-tamil-dubbed/")
    urls.append(f"{ISAIDUB_BASE}/movie/{slug}-hd-tamil-dubbed/")
    return urls


def extract_info_from_text(page_text, keyword_patterns):
    lines = page_text.splitlines()
    for line in lines:
        line_stripped = line.strip()
        line_lower = line_stripped.lower()
        for pattern in keyword_patterns:
            if pattern in line_lower:
                if ":" in line_stripped:
                    return line_stripped.split(":", 1)[1].strip()
                elif "by" in line_lower:
                    parts = line_stripped.split("by", 1)
                    if len(parts) > 1:
                        return parts[1].strip()
    return None


def fetch_movie_poster(movie_name, year=None):
    """Fetch movie poster from OMDB API (free tier) or fallback to TMDB"""
    try:
        # Try OMDB API (free, no key needed for basic)
        search_query = movie_name.replace(" ", "+")
        omdb_url = f"https://www.omdbapi.com/?t={search_query}&y={year or ''}&apikey=aa9e49f"
        resp = requests.get(omdb_url, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            if data.get("Poster") and data["Poster"] != "N/A":
                return data["Poster"]
    except:
        pass

    # Fallback: try to get from movie page itself
    return None


def scrape_movie_page(url, base_url):
    try:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        response = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(response.content, "html.parser")

        # Get title
        title_tag = soup.find("title")
        movie_title = "Unknown Movie"
        if title_tag:
            title_text = title_tag.text
            if "Download" in title_text:
                movie_title = title_text.split("Download")[0].strip()
            else:
                movie_title = title_text.strip()

        # Find poster image - ENHANCED with multiple methods
        poster_url = None

        # Method 1: og:image meta tag
        og_image = soup.find("meta", property="og:image")
        if og_image and og_image.get("content"):
            poster_url = og_image["content"]

        # Method 2: twitter:image
        if not poster_url:
            tw_image = soup.find("meta", attrs={"name": "twitter:image"})
            if tw_image and tw_image.get("content"):
                poster_url = tw_image["content"]

        # Method 3: Look for poster images with movie-related keywords
        if not poster_url:
            for img in soup.find_all("img"):
                src = img.get("src", "")
                alt = img.get("alt", "").lower()
                class_name = " ".join(img.get("class", [])).lower()
                if src and ("poster" in src.lower() or "movie" in alt or "film" in alt or 
                           "poster" in class_name or "thumb" in class_name or
                           ("upload" in src.lower() and (".jpg" in src.lower() or ".png" in src.lower()))):
                    poster_url = src if src.startswith("http") else base_url + src
                    break

        # Method 4: Any image with substantial size
        if not poster_url:
            for img in soup.find_all("img"):
                src = img.get("src", "")
                width = img.get("width", "")
                if src and (".jpg" in src.lower() or ".png" in src.lower() or ".jpeg" in src.lower()):
                    if "logo" not in src.lower() and "icon" not in src.lower() and "banner" not in src.lower():
                        # Prefer larger images
                        if width and int(width) if width.isdigit() else True:
                            poster_url = src if src.startswith("http") else base_url + src
                            break

        # Method 5: Try OMDB API for poster
        if not poster_url:
            clean_title = movie_title.replace("Download", "").replace("Tamil", "").replace("Movie", "").strip()
            api_poster = fetch_movie_poster(clean_title)
            if api_poster:
                poster_url = api_poster

        # Find download links - ENHANCED to find DIRECT download links
        download_links = []
        direct_downloads = []  # New: separate list for direct file links

        quality_keywords = {
            "1080p": "1080p", "720p": "720p", "480p": "480p", "360p": "360p",
            "240p": "240p", "hd": "HD", "full-hd": "Full HD", "bluray": "BluRay",
            "dvd": "DVD", "webrip": "WebRip", "web-dl": "Web-DL", "download": "Download"
        }

        for link in soup.find_all("a", href=True):
            href = link["href"]
            text = link.get_text(strip=True)
            href_lower = href.lower()
            text_lower = text.lower()

            # Check for direct file links (.mp4, .mkv, etc.)
            is_direct_file = any(ext in href_lower for ext in [".mp4", ".mkv", ".avi", ".mov", ".wmv"])
            is_quality_link = any(kw in href_lower for kw in ["download", "720p", "1080p", "480p", "360p", "mp4", "hd", "mkv", "webrip", "bluray"])

            if is_quality_link or is_direct_file:
                full_url = href if href.startswith("http") else base_url + href
                if full_url not in [d["url"] for d in download_links]:
                    detected_quality = "Download"
                    for kw, label in quality_keywords.items():
                        if kw in href_lower or kw in text_lower:
                            detected_quality = label
                            break

                    btn_text = text[:30] if text and len(text) > 2 else f"Download {detected_quality}"

                    link_data = {"text": btn_text, "url": full_url, "quality": detected_quality}
                    download_links.append(link_data)

                    # If direct file link, add to direct downloads
                    if is_direct_file:
                        direct_downloads.append(link_data)

        # Also look for iframe/embed video sources
        video_sources = []
        for iframe in soup.find_all("iframe", src=True):
            src = iframe["src"]
            if src:
                video_sources.append(src if src.startswith("http") else base_url + src)

        for embed in soup.find_all("embed", src=True):
            src = embed["src"]
            if src:
                video_sources.append(src if src.startswith("http") else base_url + src)

        # Extract movie info
        page_text = soup.get_text()
        movie_info = {}

        director = extract_info_from_text(page_text, ["director", "directed by"])
        if director:
            movie_info["Director"] = director[:50]

        cast = extract_info_from_text(page_text, ["starring", "cast", "actors"])
        if cast:
            movie_info["Starring"] = cast[:100]

        rating_match = re.search(r"(?:Rating|IMDb)[\s:]+([\d.]+)", page_text, re.I)
        if rating_match:
            movie_info["Rating"] = rating_match.group(1)

        genre = extract_info_from_text(page_text, ["genre", "category"])
        if genre:
            movie_info["Genre"] = genre[:50]

        # Find synopsis
        synopsis = ""
        for header in soup.find_all(["h2", "h3", "h4", "strong", "b"]):
            header_text = header.get_text(strip=True).lower()
            if any(word in header_text for word in ["synopsis", "story", "plot", "description", "about"]):
                next_elem = header.find_next_sibling()
                if next_elem:
                    synopsis = next_elem.get_text(strip=True)[:300]
                    break
                parent = header.parent
                if parent:
                    next_sib = parent.find_next_sibling()
                    if next_sib:
                        synopsis = next_sib.get_text(strip=True)[:300]
                        break

        if not synopsis:
            for p in soup.find_all("p"):
                p_text = p.get_text(strip=True)
                if len(p_text) > 50:
                    synopsis = p_text[:300]
                    break

        return {
            "title": movie_title,
            "url": url,
            "poster_url": poster_url,
            "download_links": download_links[:8],  # Increased limit
            "direct_downloads": direct_downloads[:5],  # New field
            "video_sources": video_sources[:3],  # New field for watch links
            "info": movie_info,
            "synopsis": synopsis
        }
    except Exception as e:
        logger.error(f"Scrape error: {e}")
        return None


def scrape_moviesda_year(year):
    try:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        response = requests.get(f"{MOVIESDA_BASE}/tamil-{year}-movies/", headers=headers, timeout=15)
        soup = BeautifulSoup(response.content, "html.parser")
        movies = []
        for link in soup.find_all("a", href=True):
            href = link["href"]
            text = link.get_text(strip=True)
            if year in text and len(text) > 3 and text[0].isalpha():
                if any(skip in href.lower() for skip in ["tamil-202", "dubbed", "collection", "mobile", "home"]):
                    continue
                full_url = href if href.startswith("http") else MOVIESDA_BASE + href
                movies.append({"name": text, "url": full_url})
        return movies[:20]
    except:
        return []


def scrape_isaidub_year(year):
    try:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        response = requests.get(f"{ISAIDUB_BASE}/tamil-{year}-dubbed-movies/", headers=headers, timeout=15)
        soup = BeautifulSoup(response.content, "html.parser")
        movies = []
        for link in soup.find_all("a", href=True):
            href = link["href"]
            text = link.get_text(strip=True)
            if len(text) > 3 and text[0].isalpha():
                if any(skip in href.lower() for skip in ["tamil-202", "collection", "mobile", "home"]):
                    continue
                if "/movie/" in href:
                    full_url = href if href.startswith("http") else ISAIDUB_BASE + href
                    movies.append({"name": text, "url": full_url})
        return movies[:20]
    except:
        return []


def search_movie(movie_name, year=None):
    results = []
    md_urls = generate_moviesda_urls(movie_name, year)
    for url in md_urls:
        if check_url_exists(url):
            movie_data = scrape_movie_page(url, MOVIESDA_BASE)
            if movie_data:
                found_year = get_year_from_url(url) or "Unknown"
                results.append({
                    "name": movie_name.title(),
                    "url": url,
                    "poster_url": movie_data.get("poster_url"),
                    "download_links": movie_data.get("download_links", []),
                    "direct_downloads": movie_data.get("direct_downloads", []),
                    "video_sources": movie_data.get("video_sources", []),
                    "info": movie_data.get("info", {}),
                    "synopsis": movie_data.get("synopsis", ""),
                    "source": "Moviesda",
                    "type": "Tamil",
                    "year": found_year
                })
                break

    id_urls = generate_isaidub_urls(movie_name, year)
    for url in id_urls:
        if check_url_exists(url):
            movie_data = scrape_movie_page(url, ISAIDUB_BASE)
            if movie_data:
                found_year = get_year_from_url(url) or "Unknown"
                results.append({
                    "name": movie_name.title(),
                    "url": url,
                    "poster_url": movie_data.get("poster_url"),
                    "download_links": movie_data.get("download_links", []),
                    "direct_downloads": movie_data.get("direct_downloads", []),
                    "video_sources": movie_data.get("video_sources", []),
                    "info": movie_data.get("info", {}),
                    "synopsis": movie_data.get("synopsis", ""),
                    "source": "IsaiDub",
                    "type": "Tamil Dubbed",
                    "year": found_year
                })
                break

    return results


def generate_direct_quality_urls(movie_name):
    slug = slugify(movie_name)
    return {
        "1080p_movie": f"{MOVIESDA_BASE}/{slug}-1080p-hd-movie/",
        "720p_movie": f"{MOVIESDA_BASE}/{slug}-720p-hd-movie/",
        "480p_movie": f"{MOVIESDA_BASE}/{slug}-480p-hd-movie/",
        "hd_movie": f"{MOVIESDA_BASE}/{slug}-hd-movie/",
        "hd_movies": f"{MOVIESDA_BASE}/{slug}-hd-movies/",
        "full_hd": f"{MOVIESDA_BASE}/{slug}-full-hd-movie/",
        "full_movie": f"{MOVIESDA_BASE}/{slug}-full-movie/",
        "full_movies": f"{MOVIESDA_BASE}/{slug}-full-movies/",
        "movie": f"{MOVIESDA_BASE}/{slug}-movie/",
        "movies": f"{MOVIESDA_BASE}/{slug}-movies/",
        "1080p_web_series": f"{MOVIESDA_BASE}/{slug}-1080p-hd-web-series/",
        "720p_web_series": f"{MOVIESDA_BASE}/{slug}-720p-hd-web-series/",
        "480p_web_series": f"{MOVIESDA_BASE}/{slug}-480p-hd-web-series/",
        "hd_web_series": f"{MOVIESDA_BASE}/{slug}-hd-web-series/",
        "web_series": f"{MOVIESDA_BASE}/{slug}-web-series/",
        "1080p_season": f"{MOVIESDA_BASE}/{slug}-season-01-1080p-hd-web-series/",
        "720p_season": f"{MOVIESDA_BASE}/{slug}-season-01-720p-hd-web-series/",
        "480p_season": f"{MOVIESDA_BASE}/{slug}-season-01-480p-hd-web-series/",
        "season": f"{MOVIESDA_BASE}/{slug}-season-01/",
        "1080p_tamil": f"{MOVIESDA_BASE}/{slug}-1080p-hd-tamil-movie/",
        "720p_tamil": f"{MOVIESDA_BASE}/{slug}-720p-hd-tamil-movie/",
        "480p_tamil": f"{MOVIESDA_BASE}/{slug}-480p-hd-tamil-movie/",
        "tamil_movie": f"{MOVIESDA_BASE}/{slug}-tamil-movie/",
        "tamil_hd": f"{MOVIESDA_BASE}/{slug}-tamil-hd-movie/",
    }


def find_best_quality_links(movie_name):
    quality_urls = generate_direct_quality_urls(movie_name)
    found_links = []
    priority_order = [
        ("1080p_movie", "1080p HD Movie", "1080p"),
        ("1080p_tamil", "1080p Tamil HD", "1080p"),
        ("1080p_web_series", "1080p Web Series", "1080p"),
        ("1080p_season", "S01 1080p", "1080p"),
        ("720p_movie", "720p HD Movie", "720p"),
        ("720p_tamil", "720p Tamil HD", "720p"),
        ("720p_web_series", "720p Web Series", "720p"),
        ("720p_season", "S01 720p", "720p"),
        ("480p_movie", "480p HD Movie", "480p"),
        ("480p_tamil", "480p Tamil HD", "480p"),
        ("480p_web_series", "480p Web Series", "480p"),
        ("480p_season", "S01 480p", "480p"),
        ("full_hd", "Full HD Movie", "hd"),
        ("hd_movie", "HD Movie", "hd"),
        ("hd_movies", "HD Movies", "hd"),
        ("tamil_hd", "Tamil HD", "hd"),
        ("hd_web_series", "HD Web Series", "hd"),
        ("full_movie", "Full Movie", "full"),
        ("full_movies", "Full Movies", "full"),
        ("movie", "Movie", "movie"),
        ("movies", "Movies", "movie"),
        ("tamil_movie", "Tamil Movie", "tamil"),
        ("web_series", "Web Series", "web"),
        ("season", "Season 01", "season"),
    ]
    checked_urls = set()
    for key, label, quality in priority_order:
        url = quality_urls.get(key)
        if url and url not in checked_urls:
            checked_urls.add(url)
            if check_url_exists(url):
                found_links.append({"url": url, "label": label, "quality": quality})
    return found_links


# ============================================
# FLASK ROUTES
# ============================================

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/search")
def api_search():
    query = request.args.get("query", "").strip()
    year = request.args.get("year", "").strip()
    if not query:
        return jsonify({"error": "No query provided"}), 400
    results = search_movie(query, year if year else None)
    return jsonify({"results": results})


@app.route("/api/tamil/<year>")
def api_tamil(year):
    movies = scrape_moviesda_year(year)
    return jsonify({"movies": movies, "year": year})


@app.route("/api/dubbed/<year>")
def api_dubbed(year):
    movies = scrape_isaidub_year(year)
    return jsonify({"movies": movies, "year": year})


@app.route("/api/movie/details")
def api_movie_details():
    url = request.args.get("url", "")
    source = request.args.get("source", "Moviesda")
    if not url:
        return jsonify({"error": "No URL provided"}), 400
    base = MOVIESDA_BASE if source == "Moviesda" else ISAIDUB_BASE
    details = scrape_movie_page(url, base)
    if details:
        movie_name = details["title"].replace("Download", "").strip()
        best_links = find_best_quality_links(movie_name)
        details["best_links"] = best_links
        return jsonify(details)
    return jsonify({"error": "Could not fetch details"}), 404


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5001))
    app.run(host="0.0.0.0", port=port, debug=True)
