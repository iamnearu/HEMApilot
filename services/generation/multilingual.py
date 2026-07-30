"""
HEMApilot Multilingual Content Adapter
========================================
Module chuyển đổi và tối ưu hóa nội dung
cho nhiều ngôn ngữ và thị trường khác nhau.

Không chỉ dịch thuần túy, mà còn "localize" - điều chỉnh
ngữ cảnh văn hóa, hashtag xu hướng, và format phù hợp
cho từng thị trường.

Author: iamnearu
"""

from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum


class Market(str, Enum):
    VIETNAM = "vi"
    ENGLISH_US = "en_us"
    ENGLISH_UK = "en_uk"
    JAPANESE = "ja"
    KOREAN = "ko"
    THAI = "th"


class LocalizationConfig(BaseModel):
    """Cấu hình localization cho một thị trường."""
    market: Market
    max_post_length: int = Field(description="Giới hạn ký tự cho platform")
    hashtag_strategy: str = Field(
        description="Chiến lược hashtag: 'trending', 'niche', 'branded'"
    )
    emoji_density: str = Field(
        default="medium",
        description="Mật độ emoji: 'low', 'medium', 'high'"
    )
    formality_level: str = Field(
        default="casual",
        description="Mức độ trang trọng: 'formal', 'casual', 'playful'"
    )
    cultural_notes: list[str] = Field(
        default_factory=list,
        description="Lưu ý văn hóa đặc biệt cho thị trường"
    )


class LocalizedContent(BaseModel):
    """Nội dung đã được localize."""
    original_content: str
    localized_content: str
    market: Market
    adaptations_made: list[str] = Field(
        description="Danh sách các điều chỉnh đã thực hiện"
    )
    cultural_warnings: list[str] = Field(
        default_factory=list,
        description="Cảnh báo về vấn đề văn hóa tiềm ẩn"
    )
    suggested_hashtags: list[str] = Field(default_factory=list)
    confidence: float = Field(
        ge=0.0, le=1.0,
        description="Độ tin cậy của bản localize"
    )


# Market-specific configurations
MARKET_CONFIGS: dict[Market, LocalizationConfig] = {
    Market.VIETNAM: LocalizationConfig(
        market=Market.VIETNAM,
        max_post_length=280,
        hashtag_strategy="trending",
        emoji_density="high",
        formality_level="casual",
        cultural_notes=[
            "Người Việt ưa chuộng tone thân thiện, gần gũi",
            "Hashtag tiếng Việt không dấu phổ biến hơn",
            "Emoji được sử dụng rất nhiều",
            "Nội dung về công nghệ nên đi kèm ứng dụng thực tế",
        ],
    ),
    Market.ENGLISH_US: LocalizationConfig(
        market=Market.ENGLISH_US,
        max_post_length=280,
        hashtag_strategy="niche",
        emoji_density="medium",
        formality_level="casual",
        cultural_notes=[
            "Prefer direct, action-oriented language",
            "Tech audience values data and benchmarks",
            "CTA should be clear and compelling",
        ],
    ),
    Market.JAPANESE: LocalizationConfig(
        market=Market.JAPANESE,
        max_post_length=140,
        hashtag_strategy="branded",
        emoji_density="high",
        formality_level="formal",
        cultural_notes=[
            "Japanese social media prefers polite, respectful tone",
            "Kaomoji (顔文字) more accepted than standard emoji",
            "Shorter posts perform better",
        ],
    ),
    Market.KOREAN: LocalizationConfig(
        market=Market.KOREAN,
        max_post_length=280,
        hashtag_strategy="trending",
        emoji_density="high",
        formality_level="casual",
        cultural_notes=[
            "Korean audience values authenticity",
            "Mixing English loanwords is common in tech",
            "Visual content drives higher engagement",
        ],
    ),
    Market.THAI: LocalizationConfig(
        market=Market.THAI,
        max_post_length=280,
        hashtag_strategy="trending",
        emoji_density="high",
        formality_level="playful",
        cultural_notes=[
            "Thai social media is very emoji/sticker heavy",
            "Humor and playfulness are appreciated",
            "555 (hahaha) is commonly used",
        ],
    ),
}


# Trending hashtag templates per market
TRENDING_HASHTAG_TEMPLATES: dict[Market, list[str]] = {
    Market.VIETNAM: [
        "#CongNghe", "#AI", "#LapTrinh", "#Developer",
        "#TuDongHoa", "#OpenSource", "#MachineLearning",
        "#StartupVietNam", "#TechTrend", "#Innovation",
    ],
    Market.ENGLISH_US: [
        "#Tech", "#AI", "#MachineLearning", "#DevTools",
        "#Automation", "#OpenSource", "#BuildInPublic",
        "#SaaS", "#Startup", "#Innovation",
    ],
    Market.JAPANESE: [
        "#テック", "#AI", "#機械学習", "#開発者",
        "#自動化", "#オープンソース", "#プログラミング",
    ],
    Market.KOREAN: [
        "#테크", "#AI", "#머신러닝", "#개발자",
        "#자동화", "#오픈소스", "#프로그래밍",
    ],
    Market.THAI: [
        "#เทคโนโลยี", "#AI", "#นักพัฒนา",
        "#โอเพนซอร์ส", "#โปรแกรมมิ่ง",
    ],
}


class MultilingualAdapter:
    """
    Adapter chuyển đổi nội dung cho nhiều thị trường.

    Features:
    - Phân tích nội dung gốc và phát hiện ngôn ngữ
    - Đề xuất hashtags phù hợp cho từng thị trường
    - Cảnh báo vấn đề văn hóa tiềm ẩn
    - Điều chỉnh format (emoji, length, formality)

    Lưu ý: Module này chuẩn bị metadata và cấu trúc
    cho việc localize. Việc dịch thuật thực sự sẽ được
    thực hiện bởi LLM (Anthropic/GPT) thông qua Generation Service.
    """

    def __init__(self):
        self._configs = MARKET_CONFIGS

    def get_config(self, market: Market) -> LocalizationConfig:
        """Lấy cấu hình cho một thị trường cụ thể."""
        return self._configs.get(market, self._configs[Market.ENGLISH_US])

    def suggest_hashtags(
        self,
        content: str,
        market: Market,
        max_count: int = 5,
    ) -> list[str]:
        """Đề xuất hashtags phù hợp cho thị trường."""
        templates = TRENDING_HASHTAG_TEMPLATES.get(market, [])
        content_lower = content.lower()

        # Score hashtags dựa trên relevance
        scored: list[tuple[str, float]] = []
        for tag in templates:
            tag_clean = tag.replace("#", "").lower()
            # Simple relevance scoring
            score = 0.5  # base score
            if tag_clean in content_lower:
                score += 1.0
            # Shorter hashtags score slightly higher (easier to read)
            score += max(0, (15 - len(tag_clean)) * 0.05)
            scored.append((tag, score))

        scored.sort(key=lambda x: x[1], reverse=True)
        return [tag for tag, _ in scored[:max_count]]

    def check_cultural_sensitivity(
        self,
        content: str,
        market: Market,
    ) -> list[str]:
        """Kiểm tra các vấn đề nhạy cảm văn hóa tiềm ẩn."""
        warnings: list[str] = []
        content_lower = content.lower()

        # Generic checks
        if market == Market.JAPANESE:
            if "!" in content and content.count("!") > 2:
                warnings.append(
                    "⚠️ Quá nhiều dấu chấm than có thể bị coi là thô lỗ "
                    "trong văn hóa Nhật Bản"
                )

        if market == Market.VIETNAM:
            # Kiểm tra mixing language quá nhiều
            import re
            english_words = re.findall(r'\b[a-zA-Z]{4,}\b', content)
            total_words = len(content.split())
            if total_words > 0 and len(english_words) / total_words > 0.5:
                warnings.append(
                    "💡 Bài viết chứa nhiều tiếng Anh. Cân nhắc dịch hoặc "
                    "giải thích thêm cho độc giả Việt Nam"
                )

        if market in (Market.JAPANESE, Market.KOREAN):
            if "🤑" in content or "💰" in content:
                warnings.append(
                    "⚠️ Emoji tiền tệ có thể bị coi là phô trương "
                    "trong văn hóa Đông Á"
                )

        return warnings

    def prepare_localization(
        self,
        content: str,
        target_market: Market,
    ) -> LocalizedContent:
        """
        Chuẩn bị nội dung cho localization.

        Tạo ra metadata và gợi ý để LLM có thể
        localize chính xác hơn.
        """
        config = self.get_config(target_market)
        adaptations: list[str] = []

        # Length check
        if len(content) > config.max_post_length:
            adaptations.append(
                f"Cần rút gọn từ {len(content)} xuống {config.max_post_length} ký tự"
            )

        # Hashtag suggestions
        suggested_tags = self.suggest_hashtags(content, target_market)
        adaptations.append(
            f"Đề xuất hashtags: {', '.join(suggested_tags)}"
        )

        # Formality adjustment
        adaptations.append(
            f"Điều chỉnh mức trang trọng: {config.formality_level}"
        )

        # Emoji density
        adaptations.append(
            f"Mật độ emoji khuyến nghị: {config.emoji_density}"
        )

        # Cultural warnings
        cultural_warnings = self.check_cultural_sensitivity(content, target_market)

        # Confidence based on how much adaptation is needed
        adaptation_count = len(adaptations)
        confidence = max(0.3, 1.0 - adaptation_count * 0.1)

        return LocalizedContent(
            original_content=content,
            localized_content=content,  # Placeholder - LLM sẽ thực hiện dịch
            market=target_market,
            adaptations_made=adaptations,
            cultural_warnings=cultural_warnings,
            suggested_hashtags=suggested_tags,
            confidence=round(confidence, 2),
        )
