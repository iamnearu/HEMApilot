"""
HEMApilot Analytics Engine
==========================
Module phân tích hiệu suất nội dung mạng xã hội sử dụng AI.
Tự động đánh giá chất lượng bài viết trước khi đăng.

Author: iamnearu
"""

from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum
from datetime import datetime
import re
import math


class SentimentType(str, Enum):
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"
    INSPIRING = "inspiring"
    CONTROVERSIAL = "controversial"


class EngagementPrediction(BaseModel):
    """Dự đoán mức độ tương tác của bài viết dựa trên phân tích nội dung."""
    estimated_likes: int = Field(description="Số lượt thích dự đoán")
    estimated_shares: int = Field(description="Số lượt chia sẻ dự đoán")
    estimated_comments: int = Field(description="Số bình luận dự đoán")
    virality_score: float = Field(
        ge=0.0, le=100.0,
        description="Điểm tiềm năng lan truyền (0-100)"
    )
    best_posting_hour: int = Field(
        ge=0, le=23,
        description="Giờ đăng bài tối ưu nhất (0-23)"
    )
    confidence: float = Field(
        ge=0.0, le=1.0,
        description="Độ tin cậy của dự đoán"
    )


class ContentQualityReport(BaseModel):
    """Báo cáo chất lượng nội dung trước khi đăng."""
    readability_score: float = Field(
        ge=0.0, le=100.0,
        description="Điểm dễ đọc (Flesch-Kincaid adapted cho social media)"
    )
    sentiment: SentimentType
    hashtag_effectiveness: float = Field(
        ge=0.0, le=100.0,
        description="Độ hiệu quả của hashtag sử dụng"
    )
    cta_strength: float = Field(
        ge=0.0, le=100.0,
        description="Sức mạnh của Call-to-Action"
    )
    overall_score: float = Field(
        ge=0.0, le=100.0,
        description="Điểm tổng thể chất lượng bài viết"
    )
    suggestions: list[str] = Field(
        default_factory=list,
        description="Gợi ý cải thiện nội dung"
    )


class ContentAnalyzer:
    """
    Engine phân tích nội dung mạng xã hội.

    Sử dụng kết hợp heuristic rules và NLP cơ bản để đánh giá
    chất lượng bài viết trước khi đăng lên các nền tảng.
    """

    # Các từ khóa tích cực thường gây tương tác cao
    POWER_WORDS = [
        "miễn phí", "bí mật", "khám phá", "cách", "hướng dẫn",
        "mới", "nhanh", "dễ dàng", "tuyệt vời", "đặc biệt",
        "free", "secret", "discover", "how", "guide",
        "new", "fast", "easy", "amazing", "exclusive",
        "AI", "automation", "breakthrough", "launch", "open-source",
    ]

    # CTA patterns
    CTA_PATTERNS = [
        r"(check|try|explore|visit|click|xem|thử|khám phá|truy cập)",
        r"(link|👇|⬇️|🔗|đường link|liên kết)",
        r"(comment|share|like|bình luận|chia sẻ|theo dõi)",
    ]

    OPTIMAL_LENGTHS = {
        "twitter": (80, 260),
        "linkedin": (150, 1300),
    }

    def __init__(self):
        self._history: list[ContentQualityReport] = []

    def analyze_readability(self, text: str) -> float:
        """
        Đánh giá độ dễ đọc cho nội dung mạng xã hội.
        Sử dụng phiên bản đơn giản hóa của Flesch Reading Ease,
        được điều chỉnh cho bối cảnh social media.
        """
        sentences = [s.strip() for s in re.split(r'[.!?\n]', text) if s.strip()]
        words = text.split()

        if not sentences or not words:
            return 0.0

        avg_sentence_length = len(words) / len(sentences)

        # Penalize quá dài hoặc quá ngắn
        length_score = 100.0
        if avg_sentence_length > 25:
            length_score -= (avg_sentence_length - 25) * 3
        elif avg_sentence_length < 5:
            length_score -= (5 - avg_sentence_length) * 5

        # Bonus cho emoji (tăng engagement trên social media)
        emoji_count = len(re.findall(
            r'[\U0001F300-\U0001F9FF\U00002600-\U000027BF]', text
        ))
        emoji_bonus = min(emoji_count * 5, 15)  # Tối đa +15 điểm

        # Bonus cho line breaks (dễ scan hơn)
        line_breaks = text.count('\n')
        format_bonus = min(line_breaks * 3, 12)

        return max(0.0, min(100.0, length_score + emoji_bonus + format_bonus))

    def analyze_sentiment(self, text: str) -> SentimentType:
        """
        Phân tích cảm xúc cơ bản của nội dung.
        Production: nên thay bằng model NLP thực sự.
        """
        text_lower = text.lower()

        inspiring_words = [
            "inspire", "truyền cảm hứng", "thay đổi", "transform",
            "breakthrough", "đột phá", "revolution", "cách mạng",
            "future", "tương lai", "dream", "ước mơ",
        ]
        negative_words = [
            "fail", "thất bại", "problem", "vấn đề", "issue",
            "bug", "error", "lỗi", "warning", "cảnh báo",
        ]
        positive_words = [
            "great", "tuyệt", "amazing", "awesome", "love",
            "yêu", "thích", "excellent", "xuất sắc", "happy",
        ]

        inspiring_count = sum(1 for w in inspiring_words if w in text_lower)
        negative_count = sum(1 for w in negative_words if w in text_lower)
        positive_count = sum(1 for w in positive_words if w in text_lower)

        if inspiring_count >= 2:
            return SentimentType.INSPIRING
        if positive_count > negative_count:
            return SentimentType.POSITIVE
        if negative_count > positive_count:
            return SentimentType.NEGATIVE
        return SentimentType.NEUTRAL

    def analyze_hashtags(self, text: str) -> float:
        """Đánh giá chất lượng và số lượng hashtag."""
        hashtags = re.findall(r'#\w+', text)
        count = len(hashtags)

        if count == 0:
            return 30.0  # Không có hashtag = bỏ lỡ cơ hội
        if count <= 3:
            return 90.0  # Sweet spot
        if count <= 5:
            return 70.0
        if count <= 10:
            return 50.0  # Quá nhiều
        return 20.0  # Spam territory

    def analyze_cta(self, text: str) -> float:
        """Đánh giá sức mạnh của Call-to-Action."""
        text_lower = text.lower()
        score = 0.0

        for pattern in self.CTA_PATTERNS:
            if re.search(pattern, text_lower):
                score += 30.0

        # Bonus cho URL (dẫn traffic)
        if re.search(r'https?://', text):
            score += 10.0

        return min(100.0, score)

    def predict_engagement(
        self, text: str, platform: str = "twitter"
    ) -> EngagementPrediction:
        """
        Dự đoán mức độ tương tác dựa trên phân tích nội dung.
        Sử dụng heuristic scoring system.
        """
        text_lower = text.lower()

        # Base score từ power words
        power_word_hits = sum(
            1 for w in self.POWER_WORDS if w.lower() in text_lower
        )
        base_score = min(power_word_hits * 8, 40)

        # Length optimization score
        min_len, max_len = self.OPTIMAL_LENGTHS.get(platform, (80, 260))
        text_len = len(text)
        if min_len <= text_len <= max_len:
            length_score = 25
        else:
            deviation = min(
                abs(text_len - min_len), abs(text_len - max_len)
            )
            length_score = max(0, 25 - deviation // 10)

        # Engagement signals
        has_question = '?' in text
        has_emoji = bool(re.search(
            r'[\U0001F300-\U0001F9FF\U00002600-\U000027BF]', text
        ))
        has_numbers = bool(re.search(r'\d+', text))

        signal_score = sum([
            has_question * 10,
            has_emoji * 8,
            has_numbers * 7,
        ])

        virality = min(100.0, base_score + length_score + signal_score)

        # Ước tính metrics dựa trên virality score
        base_multiplier = virality / 100.0
        likes = int(50 * base_multiplier * (1 + math.log1p(virality / 20)))
        shares = int(likes * 0.15)
        comments = int(likes * 0.08)

        # Best posting hour (giờ Việt Nam)
        # Peak hours: 7-9h sáng, 12-13h trưa, 19-21h tối
        if platform == "linkedin":
            best_hour = 8  # Giờ làm việc
        else:
            best_hour = 20  # Giờ giải trí

        return EngagementPrediction(
            estimated_likes=likes,
            estimated_shares=shares,
            estimated_comments=comments,
            virality_score=round(virality, 1),
            best_posting_hour=best_hour,
            confidence=round(min(0.85, 0.3 + power_word_hits * 0.05), 2),
        )

    def generate_report(
        self, text: str, platform: str = "twitter"
    ) -> ContentQualityReport:
        """Tạo báo cáo chất lượng toàn diện cho nội dung."""
        readability = self.analyze_readability(text)
        sentiment = self.analyze_sentiment(text)
        hashtag_score = self.analyze_hashtags(text)
        cta_score = self.analyze_cta(text)

        overall = (
            readability * 0.25
            + hashtag_score * 0.20
            + cta_score * 0.30
            + (80 if sentiment in (SentimentType.POSITIVE, SentimentType.INSPIRING) else 50) * 0.25
        )

        suggestions: list[str] = []

        if readability < 60:
            suggestions.append("📝 Rút gọn câu văn để dễ đọc hơn trên thiết bị di động")
        if hashtag_score < 50:
            suggestions.append("🏷️ Điều chỉnh số lượng hashtag (3-5 là tối ưu)")
        if cta_score < 40:
            suggestions.append("📢 Thêm Call-to-Action rõ ràng hơn (VD: 'Xem chi tiết tại...')")
        if sentiment == SentimentType.NEGATIVE:
            suggestions.append("😊 Cân nhắc sử dụng giọng văn tích cực hơn")
        if not re.search(r'[\U0001F300-\U0001F9FF]', text):
            suggestions.append("✨ Thêm emoji để tăng engagement")

        min_len, max_len = self.OPTIMAL_LENGTHS.get(platform, (80, 260))
        if len(text) > max_len:
            suggestions.append(
                f"✂️ Bài viết dài {len(text)} ký tự, nên rút gọn xuống dưới {max_len}"
            )
        elif len(text) < min_len:
            suggestions.append(
                f"📏 Bài viết ngắn {len(text)} ký tự, nên bổ sung thêm nội dung"
            )

        report = ContentQualityReport(
            readability_score=round(readability, 1),
            sentiment=sentiment,
            hashtag_effectiveness=round(hashtag_score, 1),
            cta_strength=round(cta_score, 1),
            overall_score=round(overall, 1),
            suggestions=suggestions,
        )
        self._history.append(report)
        return report

    def get_improvement_trend(self) -> Optional[float]:
        """
        Tính xu hướng cải thiện chất lượng qua các lần phân tích.
        Trả về phần trăm thay đổi trung bình.
        """
        if len(self._history) < 2:
            return None

        scores = [r.overall_score for r in self._history]
        changes = [
            (scores[i] - scores[i - 1]) / max(scores[i - 1], 1)
            for i in range(1, len(scores))
        ]
        return round(sum(changes) / len(changes) * 100, 2)
