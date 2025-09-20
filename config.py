"""
config.py

Configuration module for the news scraper application.
Contains RSS feed sources, cache settings, and other application constants.
"""

from __future__ import annotations

import os
from typing import List, Tuple

# RSS feed sources organized by region/country
FEED_SOURCES_BY_REGION = {
    "美国": [
        ("CNN", "https://rss.cnn.com/rss/edition.rss", "🇺🇸"),
        ("NPR", "https://feeds.npr.org/1001/rss.xml", "🇺🇸"),
        ("AP News", "https://rsshub.app/ap/topics/apf-topnews", "🇺🇸"),
        ("Fox News", "https://moxie.foxnews.com/google-publisher/latest.xml", "🇺🇸"),
        ("USA Today", "https://www.usatoday.com/rss/", "🇺🇸"),
        ("Wall Street Journal", "https://feeds.a.dj.com/rss/RSSWorldNews.xml", "🇺🇸"),
        ("Washington Post", "https://feeds.washingtonpost.com/rss/world", "🇺🇸"),
        ("New York Times", "https://rss.nytimes.com/services/xml/rss/nyt/World.xml", "🇺🇸"),
    ],
    "加拿大": [
        ("CBC News", "https://www.cbc.ca/cmlink/rss-topstories", "🇨🇦"),
        ("Global News", "https://globalnews.ca/feed/", "🇨🇦"),
        ("CTV News", "https://www.ctvnews.ca/rss/ctvnews-ca-top-stories-public-rss-1.822009", "🇨🇦"),
    ],
    "英国": [
        ("BBC", "https://feeds.bbci.co.uk/news/rss.xml", "🇬🇧"),
        ("The Guardian", "https://www.theguardian.com/world/rss", "🇬🇧"),
        ("Sky News", "https://feeds.skynews.com/feeds/rss/world.xml", "🇬🇧"),
        ("Telegraph", "https://www.telegraph.co.uk/rss.xml", "🇬🇧"),
        ("Independent", "https://www.independent.co.uk/rss", "🇬🇧"),
    ],
    "德国": [
        ("DW", "https://rss.dw.com/rdf/rss-en-all", "🇩🇪"),
        ("Spiegel", "https://www.spiegel.de/international/index.rss", "🇩🇪"),
        ("Deutsche Welle", "https://rss.dw.com/rdf/rss-en-world", "🇩🇪"),
    ],
    "法国": [
        ("France 24", "https://www.france24.com/en/rss", "🇫🇷"),
        ("Le Monde", "https://www.lemonde.fr/en/rss/une.xml", "🇫🇷"),
        ("RFI", "https://www.rfi.fr/en/rss", "🇫🇷"),
    ],
    "意大利": [
        ("ANSA", "https://www.ansa.it/english/news/rss.xml", "🇮🇹"),
        ("La Repubblica", "https://www.repubblica.it/rss/homepage/rss2.0.xml", "🇮🇹"),
    ],
    "西班牙": [
        ("El País", "https://feeds.elpais.com/mrss-s/pages/ep/site/english.elpais.com/portada", "🇪🇸"),
        ("ABC", "https://www.abc.es/rss/feeds/abcPortada.xml", "🇪🇸"),
    ],
    "俄罗斯": [
        ("RT", "https://www.rt.com/rss/", "🇷🇺"),
        ("Sputnik", "https://sputniknews.com/export/rss2/world/index.xml", "🇷🇺"),
        ("TASS", "https://tass.com/rss/v2.xml", "🇷🇺"),
    ],
    "日本": [
        ("NHK World", "https://www3.nhk.or.jp/rss/news/cat0.xml", "🇯🇵"),
        ("Japan Times", "https://www.japantimes.co.jp/rss/news.xml", "🇯🇵"),
        ("Kyodo News", "https://english.kyodonews.net/rss/news.xml", "🇯🇵"),
        ("Asahi Shimbun", "https://www.asahi.com/rss/english/", "🇯🇵"),
    ],
    "韩国": [
        ("Yonhap", "https://en.yna.co.kr/RSS/news.xml", "🇰🇷"),
        ("Korea Herald", "https://www.koreaherald.com/rss.php", "🇰🇷"),
        ("KBS World", "https://world.kbs.co.kr/rss/rss_news.htm", "🇰🇷"),
    ],
    "中国": [
        ("新华网", "http://www.news.cn/rss/world.xml", "🇨🇳"),
        ("央视网", "http://news.cctv.com/rss/world.xml", "🇨🇳"),
        ("人民网", "http://www.people.com.cn/rss/world.xml", "🇨🇳"),
        ("中新网", "http://www.chinanews.com/rss/scroll-news.xml", "🇨🇳"),
        ("China Daily", "https://www.chinadaily.com.cn/rss/world_rss.xml", "🇨🇳"),
        ("CGTN", "https://www.cgtn.com/subscribe/rss/section/world.xml", "🇨🇳"),
        ("Global Times", "https://www.globaltimes.cn/rss/outbrain.xml", "🇨🇳"),
    ],
    "印度": [
        ("Times of India", "https://timesofindia.indiatimes.com/rssfeedstopstories.cms", "🇮🇳"),
        ("Hindu", "https://www.thehindu.com/news/international/feeder/default.rss", "🇮🇳"),
        ("NDTV", "https://feeds.feedburner.com/ndtvnews-world-news", "🇮🇳"),
        ("Indian Express", "https://indianexpress.com/section/world/feed/", "🇮🇳"),
    ],
    "新加坡": [
        ("CNA", "https://www.channelnewsasia.com/api/v1/rss-outbound-feed?_format=xml", "🇸🇬"),
        ("Straits Times", "https://www.straitstimes.com/news/world/rss.xml", "🇸🇬"),
    ],
    "澳大利亚": [
        ("ABC News", "https://www.abc.net.au/news/feed/45910/rss.xml", "🇦🇺"),
        ("Sydney Morning Herald", "https://www.smh.com.au/rss/world.xml", "🇦🇺"),
        ("The Australian", "https://www.theaustralian.com.au/rss", "🇦🇺"),
    ],
    "阿联酋": [
        ("Gulf News", "https://gulfnews.com/rss", "🇦🇪"),
        ("Khaleej Times", "https://www.khaleejtimes.com/rss", "🇦🇪"),
        ("Emirates News", "https://www.wam.ae/en/rss/rss.xml", "🇦🇪"),
    ],
    "卡塔尔": [
        ("Al Jazeera", "https://www.aljazeera.com/xml/rss/all.xml", "🇶🇦"),
        ("Peninsula", "https://thepeninsulaqatar.com/rss", "🇶🇦"),
    ],
    "以色列": [
        ("Haaretz", "https://www.haaretz.com/cmlink/1.628752", "🇮🇱"),
        ("Jerusalem Post", "https://www.jpost.com/rss/rssfeedsfrontpage.aspx", "🇮🇱"),
        ("Times of Israel", "https://www.timesofisrael.com/feed/", "🇮🇱"),
    ],
    "土耳其": [
        ("Daily Sabah", "https://www.dailysabah.com/rss", "🇹🇷"),
        ("Hürriyet", "https://www.hurriyetdailynews.com/rss", "🇹🇷"),
        ("Anadolu", "https://www.aa.com.tr/en/rss/default?cat=world", "🇹🇷"),
    ],
    "巴西": [
        ("Folha", "https://feeds.folha.uol.com.br/mundo/rss091.xml", "🇧🇷"),
        ("G1", "https://g1.globo.com/dynamo/mundo/rss2.xml", "🇧🇷"),
        ("Brasil de Fato", "https://www.brasildefato.com.br/feed.xml", "🇧🇷"),
    ],
    "墨西哥": [
        ("El Universal", "https://www.eluniversal.com.mx/rss.xml", "🇲🇽"),
        ("Milenio", "https://www.milenio.com/rss", "🇲🇽"),
    ],
    "阿根廷": [
        ("Clarín", "https://www.clarin.com/rss/mundo/", "🇦🇷"),
        ("La Nación", "https://www.lanacion.com.ar/mundo/rss", "🇦🇷"),
    ],
    "南非": [
        ("News24", "https://feeds.news24.com/articles/news24/World/rss", "🇿🇦"),
        ("IOL", "https://www.iol.co.za/cmlink/international-news-rss-feed-1.730", "🇿🇦"),
        ("TimesLive", "https://www.timeslive.co.za/rss/", "🇿🇦"),
    ],
    "埃及": [
        ("Al-Ahram", "https://english.ahram.org.eg/rss/world.aspx", "🇪🇬"),
        ("Egypt Today", "https://www.egypttoday.com/Rss", "🇪🇬"),
    ],
    "国际组织": [
        ("Reuters", "https://feeds.reuters.com/Reuters/worldNews", "🌍"),
        ("UN News", "https://news.un.org/feed/subscribe/en/news/all/rss.xml", "🇺🇳"),
        ("World Bank", "https://www.worldbank.org/en/news/rss", "🏦"),
        ("IMF", "https://www.imf.org/en/News/rss", "💰"),
        ("WHO", "https://www.who.int/rss-feeds/news-english.xml", "🏥"),
    ],
    "科技平台": [
        ("TechCrunch", "https://techcrunch.com/feed/", "💻"),
        ("Wired", "https://www.wired.com/feed/rss", "💻"),
        ("Ars Technica", "https://feeds.arstechnica.com/arstechnica/index", "💻"),
        ("The Verge", "https://www.theverge.com/rss/index.xml", "💻"),
        ("Engadget", "https://www.engadget.com/rss.xml", "💻"),
        ("Hacker News", "https://rsshub.app/hackernews", "🧠"),
        ("Reddit Tech", "https://rsshub.app/reddit/r/technology", "📱"),
        ("GitHub Trending", "https://rsshub.app/github/trending/daily", "🐙"),
    ],
    "社交媒体": [
        ("Twitter Trends", "https://rsshub.app/twitter/trends", "🐦"),
        ("Reddit WorldNews", "https://rsshub.app/reddit/r/worldnews", "📰"),
        ("YouTube News", "https://rsshub.app/youtube/channel/UCupvZG-5ko_eiXAupbDfxWw", "📺"),
        ("LinkedIn News", "https://rsshub.app/linkedin/company/linkedin", "💼"),
        ("Instagram Stories", "https://rsshub.app/instagram/user/bbcnews", "📷"),
        ("Facebook Pages", "https://rsshub.app/facebook/page/bbcnews", "📘"),
    ],
    "金融经济": [
        ("Bloomberg", "https://feeds.bloomberg.com/markets/news.rss", "💰"),
        ("Financial Times", "https://www.ft.com/rss/home/global", "📈"),
        ("MarketWatch", "https://feeds.marketwatch.com/marketwatch/topstories/", "📊"),
        ("CNBC", "https://www.cnbc.com/id/100003114/device/rss/rss.html", "📺"),
        ("Yahoo Finance", "https://feeds.finance.yahoo.com/rss/2.0/topstories", "💹"),
        ("Coindesk", "https://feeds.coindesk.com/CoinDesk", "₿"),
    ],
    "体育运动": [
        ("ESPN", "https://www.espn.com/espn/rss/news", "⚽"),
        ("BBC Sport", "https://feeds.bbci.co.uk/sport/rss.xml", "🏆"),
        ("Sky Sports", "https://www.skysports.com/rss/12040", "🏈"),
        ("ESPN Soccer", "https://www.espn.com/espn/rss/soccer/news", "⚽"),
        ("Olympic News", "https://rsshub.app/olympic/news", "🥇"),
    ],
    "娱乐文化": [
        ("Variety", "https://variety.com/feed/", "🎬"),
        ("Hollywood Reporter", "https://www.hollywoodreporter.com/feed/", "🎭"),
        ("Entertainment Weekly", "https://ew.com/feed/", "📺"),
        ("Rolling Stone", "https://www.rollingstone.com/feed/", "🎵"),
        ("Pitchfork", "https://pitchfork.com/rss/news/", "🎶"),
    ]
}

# Flatten sources for backward compatibility
FEED_SOURCES: List[Tuple[str, str]] = []
for region, sources in FEED_SOURCES_BY_REGION.items():
    for name, url, flag in sources:
        FEED_SOURCES.append((name, url))

# Social media and alternative sources (using RSSHub proxy)
SOCIAL_MEDIA_SOURCES = {
    "Twitter": [
        ("CNN Breaking", "https://rsshub.app/twitter/user/cnnbrk", "🐦"),
        ("BBC Breaking", "https://rsshub.app/twitter/user/bbcbreaking", "🐦"),
        ("Reuters Top News", "https://rsshub.app/twitter/user/reuters", "🐦"),
        ("AP News", "https://rsshub.app/twitter/user/ap", "🐦"),
    ],
    "Reddit": [
        ("WorldNews", "https://rsshub.app/reddit/r/worldnews", "📰"),
        ("News", "https://rsshub.app/reddit/r/news", "📰"),
        ("Politics", "https://rsshub.app/reddit/r/politics", "🗳️"),
        ("Technology", "https://rsshub.app/reddit/r/technology", "💻"),
    ],
    "YouTube": [
        ("BBC News", "https://rsshub.app/youtube/channel/UC16niRr50-MSBwiO3YDb3RA", "📺"),
        ("CNN", "https://rsshub.app/youtube/channel/UCupvZG-5ko_eiXAupbDfxWw", "📺"),
        ("Al Jazeera", "https://rsshub.app/youtube/channel/UCNye-wNBqNL5ZzHSJj3l8Bg", "📺"),
        ("DW News", "https://rsshub.app/youtube/channel/UCknLrEdhRCp1aegoMqRaCZg", "📺"),
    ],
    "Telegram": [
        ("Breaking News", "https://rsshub.app/telegram/channel/breakingnews", "📱"),
        ("World News", "https://rsshub.app/telegram/channel/worldnews", "📱"),
    ]
}

# Cache configuration
CACHE_DIR = os.path.join(os.path.dirname(__file__), 'cache')
CACHE_DURATION = 300  # 5 minutes in seconds
MAX_ITEMS_PER_SOURCE = 5
MAX_ITEMS_PER_REGION = 20  # Maximum items per region to display

# Request timeout settings
REQUEST_TIMEOUT = 10  # seconds