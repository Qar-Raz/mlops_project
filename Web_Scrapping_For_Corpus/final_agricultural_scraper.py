import time
import json
import random
import trafilatura
from tqdm import tqdm
import os
import re
from duckduckgo_search import DDGS

# Configuration
OUTPUT_DIR = "dataset_rich"
CLASS_FILE = "class_names.txt"
RESULTS_PER_QUERY = 6
MIN_CONTENT_LENGTH = 300


def load_classes(file_path):
    """Load class names from text file"""
    if not os.path.exists(file_path):
        print(f"Error: {file_path} not found.")
        return []
    with open(file_path, "r") as f:
        return [line.strip() for line in f if line.strip()]


def clean_class_name(class_name):
    """Extract plant name and disease from class name"""
    parts = class_name.split("___")
    if len(parts) != 2:
        return class_name, "unknown", False

    plant = parts[0].replace("_", " ")
    plant = plant.replace("(maize)", "corn")
    plant = plant.replace("(including sour)", "")
    plant = plant.replace(",", "")
    plant = plant.strip()

    disease = parts[1].replace("_", " ").strip()
    is_healthy = "healthy" in disease.lower()

    return plant, disease, is_healthy


def generate_agricultural_search_queries(plant, disease, is_healthy):
    """Generate specific agricultural/plant pathology queries"""
    queries = []

    if is_healthy:
        queries.extend(
            [
                f"{plant} plant cultivation agriculture guide",
                f"growing {plant} farming practices",
                f"{plant} plant care agricultural methods",
                f"{plant} crop production agriculture",
            ]
        )
    else:
        queries.extend(
            [
                f'"{plant} {disease}" plant disease agriculture',
                f"plant pathology {plant} {disease} symptoms",
                f'"{disease}" {plant} treatment plant disease',
                f"agricultural {plant} {disease} management",
                f"{plant} {disease} identification control",
                f"{plant} disease {disease} prevention",
            ]
        )

    return queries


def search_agricultural_content(query, max_results=RESULTS_PER_QUERY):
    """Search for agricultural content using DDGS"""
    try:
        print(f"    🔍 Searching: {query}")

        with DDGS() as ddgs:
            results = list(
                ddgs.text(
                    query,
                    region="us-en",
                    safesearch="moderate",
                    max_results=max_results,
                )
            )

        urls = []
        for result in results:
            if "href" in result:
                url = result["href"]
                # Filter out obvious tech Apple URLs unless they contain agricultural terms
                if "apple.com" in url.lower() and not any(
                    term in url.lower()
                    for term in ["agriculture", "plant", "disease", "scab", "pathology"]
                ):
                    continue
                urls.append(url)

        print(f"    ✅ Found {len(urls)} URLs")
        return urls

    except Exception as e:
        print(f"    ❌ Search error: {e}")
        return []


def clean_content_comprehensive(text):
    """Comprehensive content cleaning including reference removal"""
    if not text:
        return None

    # Remove URLs and links
    text = re.sub(r"http[s]?://\S+", "", text)
    text = re.sub(r"www\.\S+", "", text)

    # Remove email addresses
    text = re.sub(r"\S+@\S+\.\S+", "", text)

    # Remove reference sections and citations
    reference_patterns = [
        r"References?[\s\S]*$",
        r"Bibliography[\s\S]*$",
        r"Sources?[\s\S]*$",
        r"Further [Rr]eading[\s\S]*$",
        r"External [Ll]inks[\s\S]*$",
        r"See [Aa]lso[\s\S]*$",
        r"\[\d+\]",  # Citation numbers like [1], [2], etc.
        r"\([^)]*\d{4}[^)]*\)",  # Publication years in parentheses
        r"doi:\S+",  # DOI links
        r"ISBN[\s-]*\d+[\d\s-]*",  # ISBN numbers
    ]

    for pattern in reference_patterns:
        text = re.sub(pattern, "", text, flags=re.IGNORECASE | re.MULTILINE)

    # Remove common unwanted phrases
    unwanted_phrases = [
        r"cookie policy.*?(?=\.|$)",
        r"privacy policy.*?(?=\.|$)",
        r"terms of service.*?(?=\.|$)",
        r"subscribe.*?newsletter.*?(?=\.|$)",
        r"follow us on.*?(?=\.|$)",
        r"share this.*?(?=\.|$)",
        r"related articles.*?(?=\.|$)",
        r"you may also like.*?(?=\.|$)",
        r"advertisement.*?(?=\.|$)",
        r"sponsored.*?(?=\.|$)",
        r"click here.*?(?=\.|$)",
        r"read more.*?(?=\.|$)",
        r"learn more.*?(?=\.|$)",
        r"contact us.*?(?=\.|$)",
        r"about us.*?(?=\.|$)",
        r"copyright.*?(?=\.|$)",
        r"all rights reserved.*?(?=\.|$)",
    ]

    for pattern in unwanted_phrases:
        text = re.sub(pattern, "", text, flags=re.IGNORECASE)

    # Clean up whitespace
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"\n\s*\n", "\n", text)
    text = re.sub(r"^\s+|\s+$", "", text, flags=re.MULTILINE)

    return text.strip()


def extract_agricultural_content(url):
    """Extract and clean content with focus on agricultural information"""
    try:
        print(f"      📄 Extracting: {url[:60]}...")

        # Use trafilatura for reliable extraction
        downloaded = trafilatura.fetch_url(url)
        if downloaded:
            content = trafilatura.extract(
                downloaded,
                include_comments=False,
                include_tables=True,
                include_formatting=False,
                include_links=False,  # Don't include links in content
            )

            if content and len(content) > MIN_CONTENT_LENGTH:
                cleaned = clean_content_comprehensive(content)
                if cleaned and len(cleaned) > MIN_CONTENT_LENGTH:
                    return cleaned

        return None

    except Exception as e:
        print(f"      ❌ Extraction error: {e}")
        return None


def scrape_all_plant_diseases():
    """Main function to scrape all 38 plant disease classes"""
    classes = load_classes(CLASS_FILE)
    if not classes:
        print("❌ No classes found!")
        return

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    print("🚀 Starting Comprehensive Plant Disease Data Scraping")
    print(f"📊 Classes to process: {len(classes)}")
    print("🎯 Target: 8-12 articles per class")
    print(f"📁 Output directory: {OUTPUT_DIR}")
    print("🧹 Content cleaning: URLs, references, citations removed")

    overall_stats = {
        "total_classes": len(classes),
        "successful_classes": 0,
        "total_articles": 0,
        "failed_classes": [],
    }

    for idx, class_name in enumerate(
        tqdm(classes, desc="Processing plant disease classes")
    ):
        plant, disease, is_healthy = clean_class_name(class_name)
        queries = generate_agricultural_search_queries(plant, disease, is_healthy)

        class_results = []
        seen_urls = set()
        total_scraped = 0

        print(f"\n[{idx+1}/{len(classes)}] {class_name}")
        print(f"  🌱 Plant: {plant}")
        print(f"  🦠 Condition: {disease}")
        print(f"  ✅ Healthy: {is_healthy}")

        for query_idx, query in enumerate(queries):
            if total_scraped >= 12:  # Max 12 articles per class
                break

            print(f"  📝 Query {query_idx+1}/{len(queries)}")

            # Get URLs for this query
            urls = search_agricultural_content(query, RESULTS_PER_QUERY)

            if not urls:
                print("    ❌ No URLs found")
                continue

            # Process each URL
            for url in urls[:4]:  # Max 4 URLs per query
                if url in seen_urls or total_scraped >= 12:
                    continue

                seen_urls.add(url)

                try:
                    content = extract_agricultural_content(url)

                    if content and len(content) > MIN_CONTENT_LENGTH:
                        # Validate agricultural relevance
                        agricultural_keywords = [
                            "plant",
                            "disease",
                            "symptom",
                            "leaf",
                            "agriculture",
                            "crop",
                            "treatment",
                            "pathogen",
                            "infection",
                            "control",
                        ]
                        content_lower = content.lower()
                        relevance_score = sum(
                            1
                            for keyword in agricultural_keywords
                            if keyword in content_lower
                        )

                        if relevance_score >= 2:  # At least 2 agricultural keywords
                            class_results.append(
                                {
                                    "model_class": class_name,
                                    "plant_name": plant,
                                    "disease_condition": disease,
                                    "is_healthy": is_healthy,
                                    "search_query": query,
                                    "source_type": "Agricultural_Rich_Content",
                                    "source_url": url,
                                    "content": content,
                                    "content_length": len(content),
                                    "agricultural_relevance": relevance_score,
                                    "scraped_at": time.strftime("%Y-%m-%d %H:%M:%S"),
                                }
                            )

                            total_scraped += 1
                            print(
                                f"    ✅ Article {total_scraped}: {url[:50]}... ({len(content)} chars, relevance: {relevance_score}/10)"
                            )
                        else:
                            print(f"    ⚠️ Low agricultural relevance: {url[:50]}...")
                    else:
                        print(f"    ⚠️ Content insufficient: {url[:50]}...")

                except Exception as e:
                    print(f"    ❌ Processing error: {e}")

                # Be respectful with delays
                time.sleep(random.uniform(2, 4))

            # Delay between queries
            time.sleep(random.uniform(3, 5))

        # Save results for this class
        if class_results:
            json_path = os.path.join(OUTPUT_DIR, f"{class_name}.json")
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(class_results, f, indent=2, ensure_ascii=False)

            overall_stats["successful_classes"] += 1
            overall_stats["total_articles"] += len(class_results)

            print(
                f"  💾 SUCCESS: Saved {len(class_results)} articles to {class_name}.json"
            )
        else:
            overall_stats["failed_classes"].append(class_name)
            print(f"  ❌ FAILED: No data collected for {class_name}")

        # Rest between classes to be respectful
        if idx < len(classes) - 1:
            print("  ⏳ Resting before next class...")
            time.sleep(random.uniform(5, 8))

    # Final comprehensive summary
    print("\n" + "=" * 80)
    print("🎉 COMPREHENSIVE PLANT DISEASE SCRAPING COMPLETED!")
    print("=" * 80)
    print("📊 FINAL STATISTICS:")
    print(f"   • Total classes: {overall_stats['total_classes']}")
    print(f"   • Successful classes: {overall_stats['successful_classes']}")
    print(f"   • Failed classes: {len(overall_stats['failed_classes'])}")
    print(f"   • Total articles scraped: {overall_stats['total_articles']}")

    if overall_stats["successful_classes"] > 0:
        avg_per_class = (
            overall_stats["total_articles"] / overall_stats["successful_classes"]
        )
        print(f"   • Average articles per successful class: {avg_per_class:.1f}")

    print(f"\n📁 All data saved to: {OUTPUT_DIR}/")
    print("🧹 Content cleaned: References, URLs, citations removed")
    print("🎯 Agricultural focus: High relevance filtering applied")

    if overall_stats["failed_classes"]:
        print(f"\n⚠️ Failed classes: {', '.join(overall_stats['failed_classes'])}")

    print("\n✅ Ready for RAG system integration!")


if __name__ == "__main__":
    print("🌾 Agricultural Plant Disease Data Scraper")
    print("=" * 50)
    scrape_all_plant_diseases()
