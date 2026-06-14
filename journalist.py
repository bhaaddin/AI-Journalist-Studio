import argparse
import json
import sys
import webbrowser
from pathlib import Path

from publisher import publish_article, _slugify
import researcher
import writer
import truth_loop
import image_collector


def main():
    parser = argparse.ArgumentParser(description="AI Journalist Studio")
    parser.add_argument("--topic", type=str, help="Article topic")
    parser.add_argument("--mode", type=str, choices=["fast", "deep"], default="fast")
    parser.add_argument("--type", type=str, choices=["analytical", "investigative", "feature", "breaking"], default="analytical")
    parser.add_argument("--output", type=str, help="Output directory override")
    parser.add_argument("--lang", type=str, default="english")
    args = parser.parse_args()

    with open("config.json", encoding="utf-8") as f:
        config = json.load(f)

    print("=" * 50)
    print("   AI JOURNALIST STUDIO")
    print("=" * 50)

    topic = args.topic
    if not topic:
        topic = input("\nEnter article topic: ").strip()
    if not topic:
        print("No topic provided. Exiting.")
        return

    article_type = args.type
    mode = args.mode
    slug = _slugify(topic)

    if args.output:
        out = Path(args.output)
        config["paths"]["articles_dir"] = str(out / "articles")
        config["paths"]["exports_dir"] = str(out / "exports")

    print(f"\n  Topic  : {topic}")
    print(f"  Type   : {article_type}")
    print(f"  Mode   : {mode}")
    print(f"  Slug   : {slug}")

    # Step 1 — Research
    print("\n[1/5] Researching topic...")
    research = None
    try:
        research = researcher.research_topic(topic, mode)
        print("  [OK] Research complete")
    except Exception as e:
        print(f"  [WARN] Research failed: {e}")
        research = {"summary": topic, "entities": [], "sources": []}

    # Step 2 — Writing
    print("\n[2/5] Writing article...")
    article = ""
    try:
        article = writer.write_article(research, topic, mode=mode)
        print("  [OK] Article written")
    except Exception as e:
        print(f"  [WARN] Writing failed: {e}")
        article = f"# {topic}\n\nArticle could not be generated."

    # Step 3 — Fact-checking
    print("\n[3/5] Auditing article...")
    revised_article = article
    audit = {}
    try:
        revised_article, audit = truth_loop.audit_article(article, topic, mode=mode)
        print("  [OK] Audit complete")
    except Exception as e:
        print(f"  [WARN] Audit failed: {e}")

    # Step 4 — Image collection
    print("\n[4/5] Collecting images...")
    images = []
    try:
        entities = research.get("entities", []) if research else []
        images = image_collector.collect_images(revised_article, entities, slug, topic=topic)
        print(f"  [OK] {len(images)} image(s) collected")
    except Exception as e:
        print(f"  [WARN] Image collection failed: {e}")

    # Step 5 — Publishing
    print()
    result = {}
    try:
        result = publish_article(revised_article, images, topic, article_type)
    except Exception as e:
        print(f"  [WARN] Publishing failed: {e}")

    print()
    print("=" * 50)
    print("   PUBLICATION SUMMARY")
    print("=" * 50)
    for fmt, path in result.items():
        if path:
            print(f"   {fmt.upper():>8}: {path}")
        else:
            print(f"   {fmt.upper():>8}: (skipped)")

    html_path = result.get("html")
    if html_path and Path(html_path).exists():
        try:
            uri = Path(html_path).resolve().as_uri()
            webbrowser.open(uri)
            print(f"\n  Browser opened: {uri}")
        except Exception as e:
            print(f"\n  [WARN] Could not open browser: {e}")

    print("\nDone.")


if __name__ == "__main__":
    if "--web" in sys.argv:
        from app import app
        app.run(host="127.0.0.1", port=5000, debug=False)
    else:
        main()
