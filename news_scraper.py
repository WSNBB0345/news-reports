"""
news_scraper.py

This module defines functions to fetch and aggregate news items from a set of
international RSS feeds and produce brief summaries for each item. It avoids
external dependencies beyond the standard library (plus `requests`) and can be
extended by adding more sources. RSS feed URLs and their associated source
names are defined in the FEED_SOURCES list. Each news item is returned as a
dictionary with the keys: `source`, `title`, `link`, and `summary`.
"""

from __future__ import annotations

import json
import os
import re
import time
import xml.etree.ElementTree as ET
from collections import Counter
from typing import List, Tuple, Dict

import requests

from config import FEED_SOURCES, FEED_SOURCES_BY_REGION, CACHE_DIR, CACHE_DURATION, MAX_ITEMS_PER_SOURCE, REQUEST_TIMEOUT
from sample_data import get_sample_data_by_region
from database import (
    insert_articles_batch, get_all_articles_by_region, get_articles_by_region,
    update_source_stats, get_database_stats, cleanup_old_articles
)


# RSS feed sources are now managed in config.py


def get_cache_file_path(source_name: str) -> str:
    """Get the cache file path for a specific news source.

    Args:
        source_name: Name of the news source.

    Returns:
        Path to the cache file.
    """
    if not os.path.exists(CACHE_DIR):
        os.makedirs(CACHE_DIR)
    return os.path.join(CACHE_DIR, f"{source_name.lower().replace(' ', '_')}_cache.json")


def is_cache_valid(cache_file: str) -> bool:
    """Check if cache file exists and is still valid.

    Args:
        cache_file: Path to the cache file.

    Returns:
        True if cache is valid, False otherwise.
    """
    if not os.path.exists(cache_file):
        return False

    cache_time = os.path.getmtime(cache_file)
    current_time = time.time()
    return (current_time - cache_time) < CACHE_DURATION


def load_from_cache(cache_file: str) -> List[Dict[str, str]]:
    """Load news items from cache file.

    Args:
        cache_file: Path to the cache file.

    Returns:
        List of cached news items.
    """
    try:
        with open(cache_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return []


def save_to_cache(cache_file: str, items: List[Dict[str, str]]) -> None:
    """Save news items to cache file.

    Args:
        cache_file: Path to the cache file.
        items: List of news items to cache.
    """
    try:
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(items, f, ensure_ascii=False, indent=2)
    except OSError:
        pass  # Silently ignore cache write errors


def fetch_feed(url: str) -> List[Dict[str, str]]:
    """Retrieve and parse an RSS feed into a list of news item dicts.

    Each dict has keys `title`, `link`, and `description`. Missing fields are
    skipped. Returns an empty list on errors.

    Args:
        url: RSS feed URL.

    Returns:
        List of news item dictionaries.
    """
    try:
        response = requests.get(url, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
    except requests.RequestException:
        # Failed to fetch feed; return empty list
        return []

    items: List[Dict[str, str]] = []
    try:
        root = ET.fromstring(response.content)
    except ET.ParseError:
        return []

    # RSS feeds usually have structure <rss><channel><item>...</item></channel></rss>
    channel = root.find('channel')
    if channel is None:
        return []

    for item in channel.findall('item'):
        title_el = item.find('title')
        link_el = item.find('link')
        desc_el = item.find('description')
        title = title_el.text.strip() if title_el is not None and title_el.text else None
        link = link_el.text.strip() if link_el is not None and link_el.text else None
        desc = desc_el.text.strip() if desc_el is not None and desc_el.text else None
        if not title or not link or not desc:
            continue
        items.append({'title': title, 'link': link, 'description': desc})
    return items


def clean_html_tags(text: str) -> str:
    """Remove basic HTML tags from a string.

    Args:
        text: Input string possibly containing HTML tags.

    Returns:
        String with tags stripped.
    """
    return re.sub(r'<[^>]+>', '', text)


def summarize_text(text: str, num_sentences: int = 2) -> str:
    """Generate a simple summary for a given text.

    The algorithm splits the input text into sentences, builds a word frequency
    table, scores each sentence by the sum of its word frequencies, and then
    selects the highest scoring sentences (up to `num_sentences`). This is a
    rudimentary approach but useful for quick summaries.

    Args:
        text: Input text to summarize.
        num_sentences: Number of sentences to include in the summary.

    Returns:
        A summary consisting of the top-scoring sentences.
    """
    # Remove any residual HTML tags
    clean_text = clean_html_tags(text)
    # Split into sentences using punctuation marks. Allow both Western and full-width punctuation.
    sentences = re.split(r'(?<=[。！？.!?])\s+', clean_text)
    if len(sentences) <= num_sentences:
        return clean_text

    # Tokenize words (letters and digits only) and build frequency table
    words = re.findall(r'\b\w+\b', clean_text.lower())
    freq = Counter(words)

    # Score each sentence by summing word frequencies
    scores: List[Tuple[int, str]] = []
    for sentence in sentences:
        sentence_words = re.findall(r'\b\w+\b', sentence.lower())
        score = sum(freq.get(word, 0) for word in sentence_words)
        scores.append((score, sentence))

    # Select top sentences
    top_sentences = sorted(scores, key=lambda x: x[0], reverse=True)[:num_sentences]
    # Preserve original order as they appear in the text
    sorted_top = sorted(top_sentences, key=lambda x: sentences.index(x[1]))
    return ' '.join(sentence for _, sentence in sorted_top).strip()


def fetch_all_news() -> List[Dict[str, str]]:
    """Aggregate news items from all defined RSS feeds with caching.

    For each feed in FEED_SOURCES, check cache first, then fetch if needed.
    Generate summaries for descriptions and attach the source name. Uses file-based
    caching to reduce load on news sources and improve response times.

    Returns:
        List of aggregated news items with keys: `source`, `title`, `link`,
        `summary`.
    """
    aggregated: List[Dict[str, str]] = []

    for source_name, feed_url in FEED_SOURCES:
        cache_file = get_cache_file_path(source_name)

        # Try to load from cache first
        if is_cache_valid(cache_file):
            cached_items = load_from_cache(cache_file)
            aggregated.extend(cached_items)
            continue

        # Fetch fresh data if cache is invalid
        items = fetch_feed(feed_url)[:MAX_ITEMS_PER_SOURCE]
        processed_items = []

        for item in items:
            summary = summarize_text(item['description'], num_sentences=2)
            processed_item = {
                'source': source_name,
                'title': item['title'],
                'link': item['link'],
                'summary': summary,
            }
            processed_items.append(processed_item)
            aggregated.append(processed_item)

        # Save to cache
        save_to_cache(cache_file, processed_items)

    return aggregated


def fetch_news_by_region_from_db() -> Dict[str, List[Dict[str, str]]]:
    """Fetch news from database, organized by region.

    Returns:
        Dictionary with region names as keys and lists of news items as values.
    """
    try:
        articles_by_region = get_all_articles_by_region(hours_back=24)

        # Convert database format to API format
        formatted_data = {}
        for region, articles in articles_by_region.items():
            formatted_articles = []
            for article in articles[:MAX_ITEMS_PER_SOURCE]:  # Limit per region
                formatted_article = {
                    'region': article['region'],
                    'country': article['country'],
                    'flag': article['flag_emoji'],
                    'source': article['source'],
                    'title': article['title'],
                    'link': article['link'],
                    'summary': article['summary'] or article['description'][:200] + '...',
                }
                formatted_articles.append(formatted_article)

            if formatted_articles:
                formatted_data[region] = formatted_articles

        return formatted_data

    except Exception as e:
        print(f"Error fetching from database: {e}")
        return {}


def fetch_news_by_region() -> Dict[str, List[Dict[str, str]]]:
    """Aggregate news items organized by region with caching.

    Returns:
        Dictionary with region names as keys and lists of news items as values.
        Each news item includes region, flag, source, title, link, and summary.
    """
    news_by_region = {}
    successful_fetches = 0
    total_sources = sum(len(sources) for sources in FEED_SOURCES_BY_REGION.values())

    for region, sources in FEED_SOURCES_BY_REGION.items():
        region_news = []

        for source_name, feed_url, flag in sources:
            cache_file = get_cache_file_path(source_name)

            # Try to load from cache first
            if is_cache_valid(cache_file):
                cached_items = load_from_cache(cache_file)
                for item in cached_items:
                    item['region'] = region
                    item['flag'] = flag
                region_news.extend(cached_items)
                successful_fetches += 1
                continue

            # Fetch fresh data if cache is invalid
            items = fetch_feed(feed_url)[:MAX_ITEMS_PER_SOURCE]
            processed_items = []
            db_items = []

            if items:  # Successfully fetched data
                for item in items:
                    summary = summarize_text(item['description'], num_sentences=2)
                    processed_item = {
                        'region': region,
                        'flag': flag,
                        'source': source_name,
                        'title': item['title'],
                        'link': item['link'],
                        'summary': summary,
                    }
                    processed_items.append(processed_item)
                    region_news.append(processed_item)

                    # Prepare for database insertion
                    db_item = {
                        'region': region,
                        'country': region,  # For now, use region as country
                        'flag': flag,
                        'source': source_name,
                        'title': item['title'],
                        'link': item['link'],
                        'description': item['description'],
                        'summary': summary,
                        'language': 'en',  # Default language
                        'category': 'general'
                    }
                    db_items.append(db_item)

                # Save to database
                try:
                    inserted_count = insert_articles_batch(db_items)
                    update_source_stats(source_name, True, inserted_count)
                    print(f"Inserted {inserted_count} articles from {source_name} into database")
                except Exception as e:
                    print(f"Database insertion error for {source_name}: {e}")
                    update_source_stats(source_name, False, 0, str(e))

                # Save to cache (without region and flag for compatibility)
                cache_items = [{
                    'source': item['source'],
                    'title': item['title'],
                    'link': item['link'],
                    'summary': item['summary']
                } for item in processed_items]
                save_to_cache(cache_file, cache_items)
                successful_fetches += 1
            else:
                # If fetch failed, update stats and try sample data
                update_source_stats(source_name, False, 0, "Failed to fetch RSS data")
                print(f"Failed to fetch from {source_name}, using sample data for {region}")

        news_by_region[region] = region_news

    # If most fetches failed, try to get data from database first
    if successful_fetches < total_sources * 0.3:  # Less than 30% success rate
        print("Most RSS fetches failed, trying database first")
        db_data = fetch_news_by_region_from_db()

        # Merge with any successfully fetched data
        for region, db_news in db_data.items():
            if not news_by_region.get(region) or len(news_by_region[region]) < 2:
                news_by_region[region] = db_news

        # If database also doesn't have enough data, fall back to sample data
        if not news_by_region or sum(len(articles) for articles in news_by_region.values()) < 10:
            print("Database also insufficient, falling back to sample data")
            sample_data = get_sample_data_by_region()
            for region, sample_news in sample_data.items():
                if not news_by_region.get(region) or len(news_by_region[region]) < 2:
                    news_by_region[region] = sample_news

    return news_by_region


def get_database_statistics() -> Dict:
    """Get database statistics for monitoring."""
    try:
        return get_database_stats()
    except Exception as e:
        print(f"Error getting database stats: {e}")
        return {}


def cleanup_old_news(days: int = 30) -> int:
    """Clean up old news articles from database."""
    try:
        return cleanup_old_articles(days)
    except Exception as e:
        print(f"Error cleaning up old articles: {e}")
        return 0


if __name__ == '__main__':
    # When run directly, print a brief preview of aggregated news
    news = fetch_all_news()
    for n in news[:10]:
        print(f"[{n['source']}] {n['title']}: {n['summary'][:100]}\n")