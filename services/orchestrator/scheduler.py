"""
HEMApilot Smart Scheduler
==========================
Module lập lịch đăng bài thông minh dựa trên phân tích
thời gian tương tác tối ưu của từng nền tảng.

Sử dụng thuật toán Bayesian Optimization đơn giản hóa
để học từ lịch sử đăng bài và tìm ra "golden hours".

Author: iamnearu
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, timedelta
from enum import Enum
import random
import math


class Platform(str, Enum):
    TWITTER = "twitter"
    LINKEDIN = "linkedin"
    FACEBOOK = "facebook"
    INSTAGRAM = "instagram"


class TimeSlot(BaseModel):
    """Một khung giờ đăng bài."""
    day_of_week: int = Field(ge=0, le=6, description="0=Thứ 2, 6=Chủ nhật")
    hour: int = Field(ge=0, le=23)
    platform: Platform
    avg_engagement: float = Field(default=0.0, description="Engagement trung bình")
    sample_count: int = Field(default=0, description="Số lần đăng trong khung giờ này")


class ScheduleSuggestion(BaseModel):
    """Gợi ý lịch đăng bài tối ưu."""
    suggested_datetime: datetime
    platform: Platform
    confidence: float = Field(ge=0.0, le=1.0)
    reason: str
    expected_reach_multiplier: float = Field(
        ge=0.0,
        description="Hệ số nhân reach so với trung bình"
    )


class ContentCalendarEntry(BaseModel):
    """Một mục trong content calendar."""
    scheduled_at: datetime
    platform: Platform
    content_preview: str
    status: str = "draft"
    priority: int = Field(ge=1, le=5, description="1=Cao nhất, 5=Thấp nhất")


class SmartScheduler:
    """
    Bộ lập lịch thông minh cho nội dung mạng xã hội.

    Tự động tìm khung giờ tối ưu để đăng bài dựa trên:
    - Dữ liệu engagement lịch sử
    - Đặc thù từng nền tảng
    - Múi giờ Việt Nam (UTC+7)
    - Tránh trùng lặp với bài đã lên lịch
    """

    # Golden hours mặc định cho từng platform (giờ VN)
    DEFAULT_PEAK_HOURS: dict[Platform, list[int]] = {
        Platform.TWITTER: [7, 8, 12, 13, 19, 20, 21],
        Platform.LINKEDIN: [7, 8, 9, 11, 12, 17, 18],
        Platform.FACEBOOK: [9, 10, 12, 13, 19, 20],
        Platform.INSTAGRAM: [8, 9, 11, 12, 19, 20, 21],
    }

    # Ngày tốt nhất trong tuần cho mỗi platform
    BEST_DAYS: dict[Platform, list[int]] = {
        Platform.TWITTER: [0, 1, 2, 3],       # Thứ 2-5
        Platform.LINKEDIN: [0, 1, 2, 3],       # Thứ 2-5
        Platform.FACEBOOK: [2, 3, 4, 5],       # Thứ 4-7
        Platform.INSTAGRAM: [0, 2, 4, 5, 6],   # T2, T4, T6, T7, CN
    }

    def __init__(self):
        self._time_slots: list[TimeSlot] = []
        self._calendar: list[ContentCalendarEntry] = []
        self._initialize_default_slots()

    def _initialize_default_slots(self):
        """Khởi tạo các time slot mặc định với prior knowledge."""
        for platform in Platform:
            peak_hours = self.DEFAULT_PEAK_HOURS[platform]
            best_days = self.BEST_DAYS[platform]

            for day in range(7):
                for hour in range(24):
                    base_engagement = 1.0

                    # Boost nếu giờ peak
                    if hour in peak_hours:
                        base_engagement *= 2.5

                    # Boost nếu ngày tốt
                    if day in best_days:
                        base_engagement *= 1.8

                    # Penalty cho giờ ngủ (0h-5h)
                    if 0 <= hour <= 5:
                        base_engagement *= 0.2

                    self._time_slots.append(TimeSlot(
                        day_of_week=day,
                        hour=hour,
                        platform=platform,
                        avg_engagement=base_engagement,
                        sample_count=1,  # Prior count
                    ))

    def record_engagement(
        self,
        platform: Platform,
        posted_at: datetime,
        engagement_score: float,
    ):
        """
        Ghi nhận kết quả engagement để cập nhật mô hình.
        Sử dụng Bayesian update đơn giản (running average).
        """
        day = posted_at.weekday()
        hour = posted_at.hour

        for slot in self._time_slots:
            if (
                slot.platform == platform
                and slot.day_of_week == day
                and slot.hour == hour
            ):
                # Bayesian-style update: weighted average
                total = slot.avg_engagement * slot.sample_count + engagement_score
                slot.sample_count += 1
                slot.avg_engagement = total / slot.sample_count
                break

    def suggest_next_slot(
        self,
        platform: Platform,
        after: Optional[datetime] = None,
        min_gap_hours: int = 4,
    ) -> ScheduleSuggestion:
        """
        Gợi ý thời điểm đăng bài tiếp theo tối ưu nhất.

        Args:
            platform: Nền tảng mục tiêu
            after: Thời điểm bắt đầu tìm (mặc định: bây giờ)
            min_gap_hours: Khoảng cách tối thiểu với bài trước (giờ)
        """
        if after is None:
            after = datetime.now()

        # Tìm các slot trong 7 ngày tới
        candidates: list[tuple[datetime, TimeSlot]] = []

        for days_ahead in range(7):
            candidate_date = after + timedelta(days=days_ahead)
            day_of_week = candidate_date.weekday()

            for slot in self._time_slots:
                if slot.platform != platform or slot.day_of_week != day_of_week:
                    continue

                candidate_dt = candidate_date.replace(
                    hour=slot.hour, minute=0, second=0, microsecond=0
                )

                # Phải sau thời điểm "after"
                if candidate_dt <= after:
                    continue

                # Kiểm tra khoảng cách với các bài đã lên lịch
                too_close = False
                for entry in self._calendar:
                    if entry.platform == platform:
                        gap = abs((candidate_dt - entry.scheduled_at).total_seconds())
                        if gap < min_gap_hours * 3600:
                            too_close = True
                            break

                if not too_close:
                    candidates.append((candidate_dt, slot))

        if not candidates:
            # Fallback: gợi ý giờ peak tiếp theo
            fallback_dt = after + timedelta(hours=min_gap_hours)
            return ScheduleSuggestion(
                suggested_datetime=fallback_dt,
                platform=platform,
                confidence=0.3,
                reason="Không tìm được slot tối ưu, sử dụng fallback",
                expected_reach_multiplier=1.0,
            )

        # Sắp xếp theo engagement score (cao nhất trước)
        candidates.sort(key=lambda x: x[1].avg_engagement, reverse=True)
        best_dt, best_slot = candidates[0]

        # Tính confidence dựa trên sample count
        confidence = min(0.95, 0.4 + math.log1p(best_slot.sample_count) * 0.1)

        # Tính reach multiplier
        avg_all = sum(s.avg_engagement for s in self._time_slots if s.platform == platform)
        avg_all /= max(1, sum(1 for s in self._time_slots if s.platform == platform))
        multiplier = best_slot.avg_engagement / max(avg_all, 0.01)

        # Tạo lý do bằng tiếng Việt
        day_names = ["Thứ 2", "Thứ 3", "Thứ 4", "Thứ 5", "Thứ 6", "Thứ 7", "Chủ nhật"]
        reason = (
            f"🎯 {day_names[best_slot.day_of_week]} lúc {best_slot.hour}h "
            f"là khung giờ vàng cho {platform.value}. "
            f"Dựa trên {best_slot.sample_count} lần phân tích, "
            f"engagement trung bình cao gấp {multiplier:.1f}x so với bình thường."
        )

        return ScheduleSuggestion(
            suggested_datetime=best_dt,
            platform=platform,
            confidence=round(confidence, 2),
            reason=reason,
            expected_reach_multiplier=round(multiplier, 2),
        )

    def add_to_calendar(
        self,
        content: str,
        platform: Platform,
        scheduled_at: Optional[datetime] = None,
        priority: int = 3,
    ) -> ContentCalendarEntry:
        """
        Thêm nội dung vào content calendar.
        Nếu không chỉ định thời gian, tự động chọn slot tối ưu.
        """
        if scheduled_at is None:
            suggestion = self.suggest_next_slot(platform)
            scheduled_at = suggestion.suggested_datetime

        entry = ContentCalendarEntry(
            scheduled_at=scheduled_at,
            platform=platform,
            content_preview=content[:100] + ("..." if len(content) > 100 else ""),
            priority=priority,
        )
        self._calendar.append(entry)
        self._calendar.sort(key=lambda e: (e.priority, e.scheduled_at))
        return entry

    def get_weekly_calendar(
        self, start_date: Optional[datetime] = None
    ) -> list[ContentCalendarEntry]:
        """Lấy content calendar cho tuần."""
        if start_date is None:
            start_date = datetime.now()
        end_date = start_date + timedelta(days=7)

        return [
            entry for entry in self._calendar
            if start_date <= entry.scheduled_at < end_date
        ]

    def generate_optimal_week(
        self,
        platforms: list[Platform],
        posts_per_platform: int = 3,
    ) -> list[ScheduleSuggestion]:
        """
        Tạo lịch đăng bài tối ưu cho cả tuần.
        Tự động phân bổ bài viết vào các khung giờ vàng,
        đảm bảo không trùng lặp và khoảng cách hợp lý.
        """
        suggestions: list[ScheduleSuggestion] = []
        temp_calendar = self._calendar.copy()

        for platform in platforms:
            for _ in range(posts_per_platform):
                suggestion = self.suggest_next_slot(
                    platform,
                    after=datetime.now(),
                    min_gap_hours=8,
                )
                suggestions.append(suggestion)

                # Tạm thêm vào calendar để tránh trùng
                self._calendar.append(ContentCalendarEntry(
                    scheduled_at=suggestion.suggested_datetime,
                    platform=platform,
                    content_preview="[Auto-scheduled placeholder]",
                    priority=3,
                ))

        # Restore calendar
        self._calendar = temp_calendar
        return suggestions
