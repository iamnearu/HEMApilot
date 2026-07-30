"""
HEMApilot A/B Testing Framework
=================================
Module thực hiện A/B testing cho nội dung mạng xã hội.

Tự động tạo các biến thể (variants) của bài viết,
đo lường và so sánh hiệu suất bằng statistical testing.

Sử dụng Wilson Score Interval để đánh giá
tỷ lệ engagement với confidence interval.

Author: iamnearu
"""

from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum
from datetime import datetime
import math
import uuid


class VariantStatus(str, Enum):
    DRAFT = "draft"
    RUNNING = "running"
    COMPLETED = "completed"
    WINNER = "winner"
    LOSER = "loser"


class Variant(BaseModel):
    """Một biến thể của bài viết để test."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4())[:8])
    name: str
    content: str
    platform: str
    status: VariantStatus = VariantStatus.DRAFT
    impressions: int = 0
    engagements: int = 0  # likes + comments + shares
    clicks: int = 0
    created_at: datetime = Field(default_factory=datetime.now)

    @property
    def engagement_rate(self) -> float:
        if self.impressions == 0:
            return 0.0
        return self.engagements / self.impressions

    @property
    def click_rate(self) -> float:
        if self.impressions == 0:
            return 0.0
        return self.clicks / self.impressions


class ABTest(BaseModel):
    """Một phiên A/B test."""
    test_id: str = Field(default_factory=lambda: str(uuid.uuid4())[:8])
    name: str
    hypothesis: str
    variants: list[Variant]
    min_sample_size: int = Field(default=100)
    confidence_level: float = Field(default=0.95)
    winner_id: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None


class ABTestResult(BaseModel):
    """Kết quả phân tích A/B test."""
    test_id: str
    is_significant: bool
    winner_variant_id: Optional[str]
    winner_variant_name: Optional[str]
    confidence: float
    lift_percentage: float = Field(
        description="Phần trăm cải thiện của winner so với loser"
    )
    details: list[dict]
    recommendation: str


class ABTestEngine:
    """
    Engine thực hiện A/B testing cho social media content.

    Workflow:
    1. Tạo test với 2+ biến thể nội dung
    2. Thu thập engagement data
    3. Phân tích kết quả bằng Wilson Score Interval
    4. Xác định winner với statistical significance
    """

    def __init__(self):
        self._tests: dict[str, ABTest] = {}

    def create_test(
        self,
        name: str,
        hypothesis: str,
        variant_contents: dict[str, str],  # name -> content
        platform: str = "twitter",
        min_sample_size: int = 100,
        confidence_level: float = 0.95,
    ) -> ABTest:
        """
        Tạo một A/B test mới.

        Args:
            name: Tên test
            hypothesis: Giả thuyết cần kiểm chứng
            variant_contents: Dict {tên_biến_thể: nội_dung}
            platform: Nền tảng test
            min_sample_size: Số lượt impression tối thiểu mỗi variant
            confidence_level: Mức tin cậy thống kê (0.90, 0.95, 0.99)
        """
        if len(variant_contents) < 2:
            raise ValueError("Cần ít nhất 2 biến thể để thực hiện A/B test")

        variants = [
            Variant(name=name, content=content, platform=platform)
            for name, content in variant_contents.items()
        ]

        test = ABTest(
            name=name,
            hypothesis=hypothesis,
            variants=variants,
            min_sample_size=min_sample_size,
            confidence_level=confidence_level,
        )

        self._tests[test.test_id] = test
        return test

    def record_impression(self, test_id: str, variant_id: str):
        """Ghi nhận một lượt hiển thị."""
        test = self._tests.get(test_id)
        if not test:
            raise ValueError(f"Test {test_id} không tồn tại")

        for variant in test.variants:
            if variant.id == variant_id:
                variant.impressions += 1
                return

    def record_engagement(
        self,
        test_id: str,
        variant_id: str,
        engagements: int = 1,
        clicks: int = 0,
    ):
        """Ghi nhận engagement cho một variant."""
        test = self._tests.get(test_id)
        if not test:
            raise ValueError(f"Test {test_id} không tồn tại")

        for variant in test.variants:
            if variant.id == variant_id:
                variant.engagements += engagements
                variant.clicks += clicks
                return

    @staticmethod
    def _wilson_score(
        successes: int, total: int, z: float = 1.96
    ) -> tuple[float, float]:
        """
        Tính Wilson Score Confidence Interval.

        Phù hợp hơn normal approximation cho tỷ lệ nhỏ
        (typical trong social media engagement).

        Returns: (lower_bound, upper_bound)
        """
        if total == 0:
            return (0.0, 0.0)

        p_hat = successes / total
        denominator = 1 + z ** 2 / total

        center = (p_hat + z ** 2 / (2 * total)) / denominator
        margin = (z / denominator) * math.sqrt(
            (p_hat * (1 - p_hat) + z ** 2 / (4 * total)) / total
        )

        return (max(0.0, center - margin), min(1.0, center + margin))

    def _z_for_confidence(self, confidence: float) -> float:
        """Map confidence level to z-score."""
        z_table = {0.90: 1.645, 0.95: 1.96, 0.99: 2.576}
        return z_table.get(confidence, 1.96)

    def analyze_test(self, test_id: str) -> ABTestResult:
        """
        Phân tích kết quả A/B test.

        Sử dụng Wilson Score Interval để:
        - So sánh engagement rate giữa các variants
        - Xác định winner với confidence interval
        - Kiểm tra statistical significance
        """
        test = self._tests.get(test_id)
        if not test:
            raise ValueError(f"Test {test_id} không tồn tại")

        z = self._z_for_confidence(test.confidence_level)

        # Tính Wilson Score cho mỗi variant
        variant_scores: list[tuple[Variant, float, float]] = []
        details: list[dict] = []

        for variant in test.variants:
            lower, upper = self._wilson_score(
                variant.engagements, variant.impressions, z
            )
            variant_scores.append((variant, lower, upper))

            details.append({
                "variant_id": variant.id,
                "variant_name": variant.name,
                "impressions": variant.impressions,
                "engagements": variant.engagements,
                "engagement_rate": round(variant.engagement_rate * 100, 3),
                "wilson_lower": round(lower * 100, 3),
                "wilson_upper": round(upper * 100, 3),
                "clicks": variant.clicks,
                "click_rate": round(variant.click_rate * 100, 3),
            })

        # Sắp xếp theo Wilson lower bound (pessimistic estimate)
        variant_scores.sort(key=lambda x: x[1], reverse=True)

        best_variant, best_lower, best_upper = variant_scores[0]
        runner_up, runner_lower, runner_upper = variant_scores[1]

        # Significant nếu lower bound của best > upper bound của runner up
        is_significant = best_lower > runner_upper

        # Tính mẫu đủ chưa
        has_enough_data = all(
            v.impressions >= test.min_sample_size for v in test.variants
        )

        # Tính lift
        if runner_up.engagement_rate > 0:
            lift = (
                (best_variant.engagement_rate - runner_up.engagement_rate)
                / runner_up.engagement_rate * 100
            )
        else:
            lift = 0.0

        # Tính actual confidence
        if is_significant and has_enough_data:
            actual_confidence = test.confidence_level
        elif has_enough_data:
            actual_confidence = 0.5 + (best_lower - runner_upper) * 10
            actual_confidence = max(0.5, min(0.99, actual_confidence))
        else:
            actual_confidence = 0.0

        # Winner
        winner_id = None
        winner_name = None
        if is_significant and has_enough_data:
            winner_id = best_variant.id
            winner_name = best_variant.name
            best_variant.status = VariantStatus.WINNER
            for _, v in enumerate(test.variants):
                if v.id != winner_id:
                    v.status = VariantStatus.LOSER

        # Recommendation bằng tiếng Việt
        if not has_enough_data:
            min_remaining = max(
                test.min_sample_size - v.impressions
                for v in test.variants
            )
            recommendation = (
                f"⏳ Chưa đủ dữ liệu. Cần thêm ~{min_remaining} lượt impression "
                f"cho mỗi biến thể trước khi kết luận."
            )
        elif is_significant:
            recommendation = (
                f"🏆 Biến thể '{best_variant.name}' thắng rõ ràng "
                f"với engagement rate cao hơn {lift:.1f}%. "
                f"Khuyến nghị sử dụng biến thể này cho chiến dịch chính."
            )
        else:
            recommendation = (
                f"🤔 Chưa có sự khác biệt có ý nghĩa thống kê "
                f"giữa các biến thể. Cân nhắc: "
                f"(1) Chạy thêm dữ liệu, "
                f"(2) Tạo biến thể mới khác biệt hơn, "
                f"(3) Sử dụng biến thể nào cũng được."
            )

        return ABTestResult(
            test_id=test_id,
            is_significant=is_significant and has_enough_data,
            winner_variant_id=winner_id,
            winner_variant_name=winner_name,
            confidence=round(actual_confidence, 3),
            lift_percentage=round(lift, 2),
            details=details,
            recommendation=recommendation,
        )

    def get_all_tests(self) -> list[ABTest]:
        """Lấy danh sách tất cả các test."""
        return list(self._tests.values())
