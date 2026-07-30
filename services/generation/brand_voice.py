"""
HEMApilot Brand Voice Guardian
================================
Module đảm bảo tính nhất quán giọng văn thương hiệu
trên mọi nền tảng mạng xã hội.

Sử dụng vector similarity (TF-IDF đơn giản) để so sánh
phong cách viết mới với "brand voice profile" đã được thiết lập.

Author: iamnearu
"""

from pydantic import BaseModel, Field
from typing import Optional
import re
import math
from collections import Counter


class BrandVoiceProfile(BaseModel):
    """Hồ sơ giọng văn thương hiệu."""
    brand_name: str
    tone_keywords: list[str] = Field(
        description="Các từ khóa thể hiện tone (VD: chuyên nghiệp, thân thiện)"
    )
    forbidden_words: list[str] = Field(
        default_factory=list,
        description="Các từ/cụm từ không nên sử dụng"
    )
    preferred_emojis: list[str] = Field(
        default_factory=list,
        description="Emoji ưu tiên sử dụng"
    )
    max_hashtags: int = Field(default=5)
    example_posts: list[str] = Field(
        default_factory=list,
        description="Các bài viết mẫu đại diện cho brand voice"
    )
    avg_sentence_length: Optional[float] = None
    vocabulary_richness: Optional[float] = None


class VoiceConsistencyResult(BaseModel):
    """Kết quả kiểm tra tính nhất quán giọng văn."""
    consistency_score: float = Field(
        ge=0.0, le=100.0,
        description="Điểm nhất quán giọng văn (0-100)"
    )
    tone_match: float = Field(ge=0.0, le=100.0)
    vocabulary_match: float = Field(ge=0.0, le=100.0)
    forbidden_word_violations: list[str]
    style_feedback: list[str]
    is_approved: bool = Field(
        description="Có đạt ngưỡng chất lượng để đăng không"
    )


class BrandVoiceGuardian:
    """
    Bảo vệ tính nhất quán giọng văn thương hiệu.

    Workflow:
    1. Xây dựng brand voice profile từ các bài viết mẫu
    2. Phân tích bài viết mới so với profile
    3. Đưa ra điểm số và gợi ý chỉnh sửa
    """

    def __init__(self, profile: BrandVoiceProfile):
        self.profile = profile
        self._build_profile_vectors()

    def _tokenize(self, text: str) -> list[str]:
        """Tokenize văn bản thành từ, loại bỏ stopwords cơ bản."""
        words = re.findall(r'\b\w+\b', text.lower())
        stopwords = {
            "the", "a", "an", "is", "are", "was", "were", "be", "been",
            "have", "has", "had", "do", "does", "did", "will", "would",
            "could", "should", "may", "might", "can", "this", "that",
            "these", "those", "i", "you", "he", "she", "it", "we", "they",
            "my", "your", "his", "her", "its", "our", "their", "and",
            "or", "but", "in", "on", "at", "to", "for", "of", "with",
            "là", "và", "của", "cho", "với", "từ", "trong", "này",
            "đó", "các", "một", "có", "không", "được", "để", "đã",
            "sẽ", "đang", "rất", "cũng", "như", "khi", "nếu",
        }
        return [w for w in words if w not in stopwords and len(w) > 1]

    def _compute_tf(self, tokens: list[str]) -> dict[str, float]:
        """Tính Term Frequency."""
        counter = Counter(tokens)
        total = len(tokens) if tokens else 1
        return {word: count / total for word, count in counter.items()}

    def _cosine_similarity(
        self, vec_a: dict[str, float], vec_b: dict[str, float]
    ) -> float:
        """Tính cosine similarity giữa hai TF vectors."""
        all_words = set(vec_a.keys()) | set(vec_b.keys())

        dot_product = sum(vec_a.get(w, 0) * vec_b.get(w, 0) for w in all_words)
        mag_a = math.sqrt(sum(v ** 2 for v in vec_a.values()))
        mag_b = math.sqrt(sum(v ** 2 for v in vec_b.values()))

        if mag_a == 0 or mag_b == 0:
            return 0.0
        return dot_product / (mag_a * mag_b)

    def _build_profile_vectors(self):
        """Xây dựng profile vector từ các bài viết mẫu."""
        if not self.profile.example_posts:
            self._profile_tf = {}
            self.profile.avg_sentence_length = 0.0
            self.profile.vocabulary_richness = 0.0
            return

        all_tokens: list[str] = []
        sentence_lengths: list[int] = []

        for post in self.profile.example_posts:
            tokens = self._tokenize(post)
            all_tokens.extend(tokens)

            sentences = [s.strip() for s in re.split(r'[.!?\n]', post) if s.strip()]
            for s in sentences:
                sentence_lengths.append(len(s.split()))

        self._profile_tf = self._compute_tf(all_tokens)

        self.profile.avg_sentence_length = (
            sum(sentence_lengths) / len(sentence_lengths)
            if sentence_lengths else 0
        )

        unique_words = len(set(all_tokens))
        total_words = len(all_tokens)
        self.profile.vocabulary_richness = (
            unique_words / total_words if total_words > 0 else 0
        )

    def check_consistency(
        self, new_post: str, approval_threshold: float = 60.0
    ) -> VoiceConsistencyResult:
        """
        Kiểm tra bài viết mới có nhất quán với brand voice không.

        Args:
            new_post: Nội dung bài viết cần kiểm tra
            approval_threshold: Ngưỡng điểm để phê duyệt tự động
        """
        # 1. Vocabulary similarity (TF-IDF cosine)
        new_tokens = self._tokenize(new_post)
        new_tf = self._compute_tf(new_tokens)
        vocab_similarity = self._cosine_similarity(self._profile_tf, new_tf) * 100

        # 2. Tone match - kiểm tra presence của tone keywords
        new_lower = new_post.lower()
        tone_hits = sum(
            1 for kw in self.profile.tone_keywords
            if kw.lower() in new_lower
        )
        tone_match = min(100.0, (tone_hits / max(len(self.profile.tone_keywords), 1)) * 100 + 30)

        # 3. Forbidden words check
        violations = [
            word for word in self.profile.forbidden_words
            if word.lower() in new_lower
        ]
        violation_penalty = len(violations) * 15

        # 4. Style analysis
        style_feedback: list[str] = []

        # Sentence length comparison
        sentences = [s.strip() for s in re.split(r'[.!?\n]', new_post) if s.strip()]
        if sentences:
            new_avg_len = sum(len(s.split()) for s in sentences) / len(sentences)
            if self.profile.avg_sentence_length and self.profile.avg_sentence_length > 0:
                length_diff = abs(new_avg_len - self.profile.avg_sentence_length)
                if length_diff > 5:
                    style_feedback.append(
                        f"📏 Độ dài câu trung bình ({new_avg_len:.0f} từ) khác biệt "
                        f"so với brand voice ({self.profile.avg_sentence_length:.0f} từ)"
                    )

        # Hashtag count check
        hashtag_count = len(re.findall(r'#\w+', new_post))
        if hashtag_count > self.profile.max_hashtags:
            style_feedback.append(
                f"🏷️ Quá nhiều hashtag ({hashtag_count}), "
                f"brand guideline khuyến nghị tối đa {self.profile.max_hashtags}"
            )

        # Emoji usage check
        if self.profile.preferred_emojis:
            used_emojis = re.findall(r'[\U0001F300-\U0001F9FF\U00002600-\U000027BF]', new_post)
            non_preferred = [
                e for e in used_emojis
                if e not in self.profile.preferred_emojis
            ]
            if non_preferred:
                style_feedback.append(
                    f"😊 Sử dụng emoji ngoài brand palette: {' '.join(non_preferred)}"
                )

        if violations:
            style_feedback.append(
                f"🚫 Vi phạm từ cấm: {', '.join(violations)}"
            )

        # Final score
        consistency_score = max(0.0, min(100.0,
            vocab_similarity * 0.35
            + tone_match * 0.40
            + (100 - violation_penalty) * 0.25
        ))

        return VoiceConsistencyResult(
            consistency_score=round(consistency_score, 1),
            tone_match=round(tone_match, 1),
            vocabulary_match=round(vocab_similarity, 1),
            forbidden_word_violations=violations,
            style_feedback=style_feedback,
            is_approved=consistency_score >= approval_threshold and len(violations) == 0,
        )

    def suggest_improvements(
        self, new_post: str
    ) -> list[str]:
        """Đưa ra gợi ý cụ thể để cải thiện brand consistency."""
        result = self.check_consistency(new_post)
        suggestions = list(result.style_feedback)

        if result.vocabulary_match < 40:
            suggestions.append(
                "💡 Thử sử dụng nhiều hơn các từ khóa đặc trưng của thương hiệu: "
                + ", ".join(self.profile.tone_keywords[:5])
            )

        if result.tone_match < 50:
            suggestions.append(
                "🎯 Giọng văn chưa phù hợp. Brand voice nên thể hiện: "
                + ", ".join(self.profile.tone_keywords)
            )

        if not suggestions:
            suggestions.append("✅ Bài viết đã phù hợp với brand voice!")

        return suggestions
