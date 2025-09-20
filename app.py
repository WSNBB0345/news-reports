"""
app.py

Flask web server that exposes an API endpoint for aggregated news and serves the
frontend page. The `/api/news` endpoint returns JSON-formatted summaries of
multiple international news sources, and the root path `/` serves a static HTML
file located in the project's frontend directory. To run the app, execute this
file with Python.
"""

from __future__ import annotations

import os
from flask import Flask, jsonify, send_from_directory

from news_scraper import fetch_all_news, fetch_news_by_region, get_database_statistics, cleanup_old_news


def create_app() -> Flask:
    """Factory to create and configure the Flask application."""
    # Static files (frontend) are located in ../frontend relative to this file
    base_dir = os.path.dirname(os.path.abspath(__file__))
    static_path = os.path.join(base_dir, '..', 'frontend')
    app = Flask(__name__, static_folder=static_path, static_url_path='')

    @app.route('/api/news')
    def api_news():
        """Return aggregated news as JSON."""
        news_items = fetch_all_news()
        return jsonify(news_items)

    @app.route('/api/news/by-region')
    def api_news_by_region():
        """Return news organized by region as JSON."""
        news_by_region = fetch_news_by_region()
        return jsonify(news_by_region)

    @app.route('/api/news/region/<region_name>')
    def api_news_single_region(region_name):
        """Return news for a specific region as JSON."""
        try:
            # URL decode the region name
            from urllib.parse import unquote
            region_name = unquote(region_name)

            news_by_region = fetch_news_by_region()

            if region_name not in news_by_region:
                return jsonify({'error': f'Region "{region_name}" not found'}), 404

            return jsonify({
                'region': region_name,
                'news': news_by_region[region_name],
                'count': len(news_by_region[region_name])
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/stats')
    def api_database_stats():
        """Return database statistics."""
        try:
            stats = get_database_statistics()
            return jsonify(stats)
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/cleanup/<int:days>')
    def api_cleanup_old_news(days):
        """Clean up old news articles."""
        try:
            if days < 1 or days > 365:
                return jsonify({'error': 'Days must be between 1 and 365'}), 400

            deleted_count = cleanup_old_news(days)
            return jsonify({
                'message': f'Cleaned up {deleted_count} articles older than {days} days',
                'deleted_count': deleted_count
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/health')
    def api_health_check():
        """Health check endpoint."""
        try:
            stats = get_database_statistics()
            return jsonify({
                'status': 'healthy',
                'database': 'connected',
                'total_articles': stats.get('total_articles', 0),
                'regions_count': len(stats.get('articles_by_region', {})),
                'last_24h_articles': stats.get('articles_last_24h', 0)
            })
        except Exception as e:
            return jsonify({
                'status': 'unhealthy',
                'error': str(e)
            }), 500

    @app.route('/')
    def index():
        """Serve the main HTML page."""
        return app.send_static_file('index.html')

    return app


if __name__ == '__main__':
    application = create_app()
    # Run the server with debug enabled for development purposes
    application.run(debug=True)