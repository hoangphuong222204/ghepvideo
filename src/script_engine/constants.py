"""Constants and system configuration configurations for the AI Script Engine."""

# Supported video script styles requested by user
SUPPORTED_STYLES = [
    "Problem Solution",
    "Review",
    "Native Review",
    "POV",
    "Luxury",
    "ASMR",
    "Comparison",
    "Storytelling",
    "Lifestyle",
    "Emotional",
    "Expert",
    "Funny",
    "Premium",
    "Minimal",
]

# Standard Reading Speed: Words Per Minute (WPM)
# Vietnamese average natural speaking rate for vertical video formats is ~150 WPM.
# 150 WPM = 2.5 words per second.
VIETNAMESE_WPM = 150.0

# Quality threshold boundary (0 to 100)
DEFAULT_QUALITY_THRESHOLD = 70.0

# TikTok sensitive / prohibited claim words and their standard rewrites
SENSITIVE_WORDS_MAP = {
    "trị dứt điểm": "hỗ trợ cải thiện rõ rệt",
    "chữa khỏi": "hỗ trợ cải thiện",
    "cam kết 100%": "mang lại trải nghiệm tối ưu",
    "tốt nhất": "vượt trội",
    "số 1": "độc đáo",
    "số một": "độc đáo",
    "hiệu quả tức thì": "hiệu quả nhanh chóng",
    "triệt để": "tối ưu",
    "an toàn tuyệt đối": "độ an toàn cao",
    "vĩnh viễn": "lâu dài",
    "thuốc trị": "sản phẩm hỗ trợ",
    "đảm bảo hết sạch": "hỗ trợ làm sạch tối đa",
}

# English branding / tech terms pronunciation phonetic mapping for Vietnamese voiceovers
ENGLISH_PRONUNCIATION_MAP = {
    "iphone": "ai-phôn",
    "sale": "seo",
    "hot": "hót",
    "review": "ri-viu",
    "tiktok": "tíc-tóc",
    "video": "vi-deo",
    "facebook": "phây-búc",
    "youtube": "diu-túp",
    "marketing": "mác-két-tinh",
    "voucher": "vau-chơ",
    "shopee": "sóp-pi",
    "ads": "át",
    "cream": "cờ-rim",
    "serum": "xi-rum",
    "skincare": "skin-ke",
    "toner": "tô-nơ",
    "feedback": "phít-bách",
    "studio": "stu-đi-ô",
    "pro": "pờ-rô",
}

# Platforms supported for future-ready customization
SUPPORTED_PLATFORMS = [
    "TikTok",
    "Shopee",
    "Facebook Reels",
    "YouTube Shorts",
    "Instagram Reels",
]
