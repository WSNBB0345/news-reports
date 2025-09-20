"""
sample_data.py

Sample news data for demonstration purposes when RSS feeds are unavailable.
This serves as a fallback data source to ensure the application always has content to display.
"""

SAMPLE_NEWS_DATA = {
    "北美": [
        {
            "region": "北美",
            "flag": "🇺🇸",
            "source": "CNN",
            "title": "美国经济数据显示通胀率继续下降",
            "link": "https://example.com/news1",
            "summary": "最新发布的经济数据显示，美国通胀率连续第三个月下降，这为美联储的货币政策提供了更多灵活性。分析师认为这是经济软着陆的积极信号。"
        },
        {
            "region": "北美",
            "flag": "🇺🇸",
            "source": "NPR",
            "title": "科技巨头宣布新一轮人工智能投资计划",
            "link": "https://example.com/news2",
            "summary": "多家科技公司宣布将在未来三年内投资数百亿美元用于人工智能研发，重点关注生成式AI和机器学习技术的突破性应用。"
        },
        {
            "region": "北美",
            "flag": "🇺🇸",
            "source": "AP News",
            "title": "气候变化对北美农业产生显著影响",
            "link": "https://example.com/news3",
            "summary": "研究报告指出，极端天气事件频发对北美地区农业生产造成重大冲击，农民们正在适应新的种植策略以应对气候挑战。"
        }
    ],
    "欧洲": [
        {
            "region": "欧洲",
            "flag": "🇬🇧",
            "source": "BBC",
            "title": "欧盟通过新的数字服务法案",
            "link": "https://example.com/news4",
            "summary": "欧洲议会正式通过了新的数字服务法案，旨在加强对大型科技平台的监管，保护用户隐私和促进公平竞争。"
        },
        {
            "region": "欧洲",
            "flag": "🇬🇧",
            "source": "The Guardian",
            "title": "英国宣布新的可再生能源发展计划",
            "link": "https://example.com/news5",
            "summary": "英国政府公布了雄心勃勃的可再生能源发展路线图，计划到2030年实现碳中和目标，重点发展海上风电和太阳能项目。"
        },
        {
            "region": "欧洲",
            "flag": "🇩🇪",
            "source": "DW",
            "title": "德国汽车工业加速电动化转型",
            "link": "https://example.com/news6",
            "summary": "德国主要汽车制造商宣布加速电动汽车生产线建设，预计到2025年电动车产量将占总产量的50%以上。"
        },
        {
            "region": "欧洲",
            "flag": "🇫🇷",
            "source": "France 24",
            "title": "法国推出新的教育改革方案",
            "link": "https://example.com/news7",
            "summary": "法国教育部宣布新的教育改革计划，重点加强STEM教育和数字技能培养，以提升学生在全球化时代的竞争力。"
        }
    ],
    "亚太": [
        {
            "region": "亚太",
            "flag": "🇯🇵",
            "source": "NHK World",
            "title": "日本推出新一代高速铁路技术",
            "link": "https://example.com/news8",
            "summary": "日本铁道公司成功测试了时速400公里的新一代新干线列车，该技术将进一步巩固日本在高速铁路领域的领先地位。"
        },
        {
            "region": "亚太",
            "flag": "🇸🇬",
            "source": "CNA",
            "title": "新加坡成为全球金融科技创新中心",
            "link": "https://example.com/news9",
            "summary": "最新报告显示，新加坡凭借其完善的监管框架和创新环境，已成为亚太地区最重要的金融科技创新中心之一。"
        }
    ],
    "中东": [
        {
            "region": "中东",
            "flag": "🇶🇦",
            "source": "Al Jazeera",
            "title": "中东地区可再生能源投资创新高",
            "link": "https://example.com/news10",
            "summary": "阿联酋和沙特阿拉伯等海湾国家大幅增加可再生能源投资，太阳能项目规模不断扩大，显示出能源转型的坚定决心。"
        }
    ],
    "国际组织": [
        {
            "region": "国际组织",
            "flag": "🌍",
            "source": "Reuters",
            "title": "联合国发布全球气候行动进展报告",
            "link": "https://example.com/news11",
            "summary": "联合国最新报告显示，各国在减排目标实现方面取得积极进展，但仍需加大努力以实现《巴黎协定》的目标。"
        },
        {
            "region": "国际组织",
            "flag": "🇺🇳",
            "source": "UN News",
            "title": "世界卫生组织更新全球卫生指导方针",
            "link": "https://example.com/news12",
            "summary": "世卫组织发布了新的全球卫生指导方针，重点关注疾病预防、健康促进和卫生系统韧性建设。"
        }
    ]
}

def get_sample_data_by_region(region_name=None):
    """
    Get sample news data, optionally filtered by region.

    Args:
        region_name: Optional region name to filter by

    Returns:
        Dictionary of news data organized by region, or specific region data
    """
    if region_name:
        return SAMPLE_NEWS_DATA.get(region_name, [])
    return SAMPLE_NEWS_DATA

def get_sample_data_flat():
    """
    Get all sample news data as a flat list.

    Returns:
        List of all news items across all regions
    """
    flat_news = []
    for region_news in SAMPLE_NEWS_DATA.values():
        flat_news.extend(region_news)
    return flat_news