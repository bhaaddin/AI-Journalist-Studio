import json
import os
import time
import requests
from ddgs import DDGS, exceptions as ddgs_exceptions
from PIL import Image
from io import BytesIO


def _load_config():
    config_path = os.path.join(os.path.dirname(__file__), "config.json")
    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)


def _search_images(query_text, max_results=3):
    delays = [5, 10]
    for attempt, delay in enumerate(delays):
        try:
            with DDGS(timeout=10) as ddgs:
                results = list(ddgs.images(query_text, max_results=max_results))
            return results
        except ddgs_exceptions.RatelimitException:
            if attempt < len(delays) - 1:
                print(f"  Rate limited, retry in {delay}s...")
                time.sleep(delay)
        except Exception as e:
            print(f"  Search failed: {e}")
            return []
    return []


def _download_image(url, save_path):
    try:
        resp = requests.get(url, timeout=15, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        })
        resp.raise_for_status()
        img = Image.open(BytesIO(resp.content))
        img.verify()
        with open(save_path, "wb") as f:
            f.write(resp.content)
        return True
    except Exception:
        return False


def _is_valid_image(filepath):
    ext = os.path.splitext(filepath)[1].lower()
    if ext not in (".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp"):
        return False
    try:
        with Image.open(filepath) as img:
            img.verify()
        return True
    except Exception:
        return False


def collect_images(article_text, research_entities, article_slug, topic=""):
    config = _load_config()
    ic = config["image_collector"]
    max_per_entity = ic.get("max_images_per_entity", 3)
    delay = ic.get("delay_between_searches", 2.0)

    entities = research_entities[:3] if research_entities else []
    images_dir = os.path.join(os.path.dirname(__file__), "images", article_slug)
    os.makedirs(images_dir, exist_ok=True)

    collected = []
    seen_urls = set()

    for i, entity in enumerate(entities):
        query = entity if not topic else f"{topic} {entity}"
        print(f"[{i + 1}/{len(entities)}] Searching images for: {query}")
        try:
            results = _search_images(query, max_results=max_per_entity * 2)
        except Exception as e:
            print(f"  Search failed for '{query}': {e}")
            continue

        skip_keywords = ["logo", "icon", "wallpaper", "printable", "calendar", "vector"]
        downloaded = 0
        for result in results:
            if downloaded >= max_per_entity:
                break

            image_url = result.get("image")
            title = (result.get("title") or "").lower()
            if not image_url or image_url in seen_urls:
                continue
            if any(k in title for k in skip_keywords):
                continue
            seen_urls.add(image_url)

            ext = os.path.splitext(image_url.split("?")[0])[1] or ".jpg"
            filename = f"{entity.replace(' ', '_')[:40]}_{downloaded + 1}{ext}"
            save_path = os.path.join(images_dir, filename)

            ok = _download_image(image_url, save_path)
            if not ok or not _is_valid_image(save_path):
                if os.path.exists(save_path):
                    os.remove(save_path)
                continue

            collected.append({
                "filename": save_path,
                "caption": result.get("title", entity) or entity,
                "source": image_url
            })
            downloaded += 1

        if i < len(entities) - 1:
            time.sleep(delay)

    print(f"  Collected {len(collected)} images to {images_dir}")
    return collected


if __name__ == "__main__":
    test_entities = ["Eiffel Tower", "Louvre Museum", "Seine River"]
    result = collect_images("Paris travel guide", test_entities, "test-paris")
    print(json.dumps(result, indent=2))
