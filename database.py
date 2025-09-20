"""
database.py

Database models and operations for the news aggregator.
Uses SQLite for persistent storage of news articles.
"""

import sqlite3
import hashlib
import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
import os

from config import CACHE_DIR

# Database file path
DB_PATH = os.path.join(CACHE_DIR, 'news_database.db')

def get_db_connection():
    """Get database connection with row factory."""
    if not os.path.exists(CACHE_DIR):
        os.makedirs(CACHE_DIR)

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_database():
    """Initialize the database with required tables."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Create news_articles table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS news_articles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            hash_id TEXT UNIQUE NOT NULL,
            region TEXT NOT NULL,
            country TEXT NOT NULL,
            source TEXT NOT NULL,
            flag_emoji TEXT NOT NULL,
            title TEXT NOT NULL,
            link TEXT NOT NULL,
            description TEXT,
            summary TEXT,
            content TEXT,
            pub_date TEXT,
            fetch_date TEXT NOT NULL,
            language TEXT DEFAULT 'en',
            category TEXT DEFAULT 'general',
            tags TEXT,
            sentiment_score REAL,
            word_count INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Create sources table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS news_sources (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            url TEXT NOT NULL,
            region TEXT NOT NULL,
            country TEXT NOT NULL,
            flag_emoji TEXT NOT NULL,
            language TEXT DEFAULT 'en',
            reliability_score REAL DEFAULT 0.5,
            last_fetch TEXT,
            fetch_count INTEGER DEFAULT 0,
            error_count INTEGER DEFAULT 0,
            active BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Create fetch_logs table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS fetch_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source_name TEXT NOT NULL,
            status TEXT NOT NULL,
            articles_count INTEGER DEFAULT 0,
            error_message TEXT,
            fetch_duration REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Create indexes for better performance
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_articles_region ON news_articles(region)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_articles_country ON news_articles(country)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_articles_source ON news_articles(source)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_articles_fetch_date ON news_articles(fetch_date)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_articles_hash ON news_articles(hash_id)')

    conn.commit()
    conn.close()

def generate_article_hash(title: str, link: str, source: str) -> str:
    """Generate unique hash for an article."""
    content = f"{title}|{link}|{source}".encode('utf-8')
    return hashlib.md5(content).hexdigest()

def insert_article(article_data: Dict) -> bool:
    """Insert a new article into the database."""
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Generate unique hash
        hash_id = generate_article_hash(
            article_data['title'],
            article_data['link'],
            article_data['source']
        )

        # Prepare data
        now = datetime.now().isoformat()

        cursor.execute('''
            INSERT OR IGNORE INTO news_articles (
                hash_id, region, country, source, flag_emoji, title, link,
                description, summary, content, pub_date, fetch_date,
                language, category, tags, word_count
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            hash_id,
            article_data.get('region', ''),
            article_data.get('country', ''),
            article_data['source'],
            article_data.get('flag', '📰'),
            article_data['title'],
            article_data['link'],
            article_data.get('description', ''),
            article_data.get('summary', ''),
            article_data.get('content', ''),
            article_data.get('pub_date', ''),
            now,
            article_data.get('language', 'en'),
            article_data.get('category', 'general'),
            json.dumps(article_data.get('tags', [])),
            len(article_data.get('summary', '').split())
        ))

        conn.commit()
        return cursor.rowcount > 0

    except sqlite3.Error as e:
        print(f"Database error inserting article: {e}")
        return False
    finally:
        conn.close()

def insert_articles_batch(articles: List[Dict]) -> int:
    """Insert multiple articles in batch."""
    conn = get_db_connection()
    cursor = conn.cursor()

    inserted_count = 0
    now = datetime.now().isoformat()

    try:
        for article in articles:
            hash_id = generate_article_hash(
                article['title'],
                article['link'],
                article['source']
            )

            try:
                cursor.execute('''
                    INSERT OR IGNORE INTO news_articles (
                        hash_id, region, country, source, flag_emoji, title, link,
                        description, summary, content, pub_date, fetch_date,
                        language, category, tags, word_count
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    hash_id,
                    article.get('region', ''),
                    article.get('country', ''),
                    article['source'],
                    article.get('flag', '📰'),
                    article['title'],
                    article['link'],
                    article.get('description', ''),
                    article.get('summary', ''),
                    article.get('content', ''),
                    article.get('pub_date', ''),
                    now,
                    article.get('language', 'en'),
                    article.get('category', 'general'),
                    json.dumps(article.get('tags', [])),
                    len(article.get('summary', '').split())
                ))

                if cursor.rowcount > 0:
                    inserted_count += 1

            except sqlite3.Error as e:
                print(f"Error inserting article {article['title']}: {e}")
                continue

        conn.commit()

    except sqlite3.Error as e:
        print(f"Database error in batch insert: {e}")
    finally:
        conn.close()

    return inserted_count

def get_articles_by_region(region: str, limit: int = 50, hours_back: int = 72) -> List[Dict]:
    """Get articles for a specific region."""
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cutoff_time = (datetime.now() - timedelta(hours=hours_back)).isoformat()

        cursor.execute('''
            SELECT * FROM news_articles
            WHERE region = ? AND fetch_date > ?
            ORDER BY fetch_date DESC, created_at DESC
            LIMIT ?
        ''', (region, cutoff_time, limit))

        rows = cursor.fetchall()
        return [dict(row) for row in rows]

    except sqlite3.Error as e:
        print(f"Database error getting articles by region: {e}")
        return []
    finally:
        conn.close()

def get_articles_by_country(country: str, limit: int = 50, hours_back: int = 72) -> List[Dict]:
    """Get articles for a specific country."""
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cutoff_time = (datetime.now() - timedelta(hours=hours_back)).isoformat()

        cursor.execute('''
            SELECT * FROM news_articles
            WHERE country = ? AND fetch_date > ?
            ORDER BY fetch_date DESC, created_at DESC
            LIMIT ?
        ''', (country, cutoff_time, limit))

        rows = cursor.fetchall()
        return [dict(row) for row in rows]

    except sqlite3.Error as e:
        print(f"Database error getting articles by country: {e}")
        return []
    finally:
        conn.close()

def get_all_articles_by_region(hours_back: int = 72) -> Dict[str, List[Dict]]:
    """Get all articles grouped by region."""
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cutoff_time = (datetime.now() - timedelta(hours=hours_back)).isoformat()

        cursor.execute('''
            SELECT * FROM news_articles
            WHERE fetch_date > ?
            ORDER BY region, fetch_date DESC, created_at DESC
        ''', (cutoff_time,))

        rows = cursor.fetchall()
        articles_by_region = {}

        for row in rows:
            article = dict(row)
            region = article['region']

            if region not in articles_by_region:
                articles_by_region[region] = []

            articles_by_region[region].append(article)

        return articles_by_region

    except sqlite3.Error as e:
        print(f"Database error getting all articles by region: {e}")
        return {}
    finally:
        conn.close()

def get_latest_articles(limit: int = 100) -> List[Dict]:
    """Get latest articles across all sources."""
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute('''
            SELECT * FROM news_articles
            ORDER BY fetch_date DESC, created_at DESC
            LIMIT ?
        ''', (limit,))

        rows = cursor.fetchall()
        return [dict(row) for row in rows]

    except sqlite3.Error as e:
        print(f"Database error getting latest articles: {e}")
        return []
    finally:
        conn.close()

def update_source_stats(source_name: str, success: bool, articles_count: int = 0, error_msg: str = None):
    """Update source statistics."""
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        now = datetime.now().isoformat()

        # Insert or update source stats
        cursor.execute('''
            INSERT OR REPLACE INTO news_sources (
                name, url, region, country, flag_emoji, last_fetch, fetch_count, error_count
            ) VALUES (
                ?, '', '', '', '', ?,
                COALESCE((SELECT fetch_count FROM news_sources WHERE name = ?), 0) + 1,
                COALESCE((SELECT error_count FROM news_sources WHERE name = ?), 0) + ?
            )
        ''', (source_name, now, source_name, source_name, 0 if success else 1))

        # Log fetch attempt
        cursor.execute('''
            INSERT INTO fetch_logs (source_name, status, articles_count, error_message)
            VALUES (?, ?, ?, ?)
        ''', (source_name, 'success' if success else 'error', articles_count, error_msg))

        conn.commit()

    except sqlite3.Error as e:
        print(f"Database error updating source stats: {e}")
    finally:
        conn.close()

def get_database_stats() -> Dict:
    """Get database statistics."""
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        stats = {}

        # Total articles
        cursor.execute('SELECT COUNT(*) FROM news_articles')
        stats['total_articles'] = cursor.fetchone()[0]

        # Articles by region
        cursor.execute('''
            SELECT region, COUNT(*) FROM news_articles
            GROUP BY region ORDER BY COUNT(*) DESC
        ''')
        stats['articles_by_region'] = dict(cursor.fetchall())

        # Articles by source
        cursor.execute('''
            SELECT source, COUNT(*) FROM news_articles
            GROUP BY source ORDER BY COUNT(*) DESC LIMIT 10
        ''')
        stats['top_sources'] = dict(cursor.fetchall())

        # Recent activity (last 24 hours)
        yesterday = (datetime.now() - timedelta(hours=24)).isoformat()
        cursor.execute('''
            SELECT COUNT(*) FROM news_articles WHERE fetch_date > ?
        ''', (yesterday,))
        stats['articles_last_24h'] = cursor.fetchone()[0]

        return stats

    except sqlite3.Error as e:
        print(f"Database error getting stats: {e}")
        return {}
    finally:
        conn.close()

def cleanup_old_articles(days_old: int = 30):
    """Remove articles older than specified days."""
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cutoff_date = (datetime.now() - timedelta(days=days_old)).isoformat()

        cursor.execute('''
            DELETE FROM news_articles WHERE fetch_date < ?
        ''', (cutoff_date,))

        deleted_count = cursor.rowcount
        conn.commit()

        print(f"Cleaned up {deleted_count} old articles")
        return deleted_count

    except sqlite3.Error as e:
        print(f"Database error cleaning up articles: {e}")
        return 0
    finally:
        conn.close()

# Initialize database on import
if __name__ == '__main__':
    init_database()
    print("Database initialized successfully")
else:
    init_database()