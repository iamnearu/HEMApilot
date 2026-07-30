# 🚀 HEMApilot — Nền tảng Quản lý Nội dung Mạng xã hội Thông minh

<p align="center">
  <strong>AI-Powered Social Media Content Platform</strong><br/>
  Tự động hóa toàn bộ quy trình sáng tạo, kiểm duyệt, và đăng tải nội dung mạng xã hội<br/>
  với kiến trúc Microservices + LangGraph + Human-in-the-Loop
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.11+-blue?logo=python" alt="Python" />
  <img src="https://img.shields.io/badge/FastAPI-0.110+-green?logo=fastapi" alt="FastAPI" />
  <img src="https://img.shields.io/badge/Docker-Compose-blue?logo=docker" alt="Docker" />
  <img src="https://img.shields.io/badge/LangGraph-AI_Agent-purple" alt="LangGraph" />
  <img src="https://img.shields.io/badge/License-MIT-yellow" alt="License" />
</p>

---

## 📋 Mục lục

- [Tổng quan](#-tổng-quan)
- [Điểm nổi bật](#-điểm-nổi-bật-so-với-các-giải-pháp-hiện-có)
- [Kiến trúc hệ thống](#-kiến-trúc-hệ-thống-microservices)
- [Các module sáng tạo](#-các-module-sáng-tạo-original)
- [Cài đặt & Chạy thử](#-cài-đặt--chạy-thử)
- [Cấu hình](#-cấu-hình)
- [API Documentation](#-api-documentation)
- [Kế hoạch phát triển](#-kế-hoạch-phát-triển)

---

## 🎯 Tổng quan

**HEMApilot** là một nền tảng quản lý nội dung mạng xã hội end-to-end, được xây dựng trên nền tảng AI Agent (LangGraph) với kiến trúc Microservices. Thay vì chỉ đơn thuần tạo bài viết, HEMApilot mang đến một hệ sinh thái hoàn chỉnh:

```
📥 Thu thập dữ liệu (Slack, GitHub, URL, YouTube)
    ↓
🔍 Phân tích & Xác minh nội dung
    ↓
✍️  Tạo bài viết bằng AI (đa ngôn ngữ, đa nền tảng)
    ↓
📊 Kiểm tra chất lượng & Brand Voice
    ↓
🧪 A/B Testing (Wilson Score Interval)
    ↓
📅 Lập lịch thông minh (Bayesian Optimization)
    ↓
🚀 Đăng tải tự động (Twitter, LinkedIn, Facebook)
    ↓
📈 Phân tích hiệu suất & Tự học
```

### Vấn đề giải quyết

| Vấn đề | Giải pháp của HEMApilot |
|--------|------------------------|
| Tạo nội dung thủ công, tốn thời gian | AI Agent tự động tạo bài viết từ URL/nguồn dữ liệu |
| Không biết đăng lúc nào hiệu quả nhất | Smart Scheduler dùng Bayesian Optimization tìm "golden hours" |
| Giọng văn không nhất quán giữa các bài | Brand Voice Guardian kiểm tra cosine similarity |
| Không biết nội dung nào hiệu quả hơn | A/B Testing Framework với Wilson Score Interval |
| Nội dung chỉ phục vụ 1 thị trường | Multilingual Adapter hỗ trợ VN, EN, JP, KR, TH |
| Quy trình publish rời rạc | Pipeline tự động end-to-end với Human-in-the-Loop |

---

## ⭐ Điểm nổi bật so với các giải pháp hiện có

### 1. 🧠 Content Analytics Engine
> *Phân tích chất lượng bài viết TRƯỚC KHI đăng*

Không chỉ tạo nội dung, HEMApilot còn **đánh giá chất lượng** bài viết dựa trên:
- **Readability Score** — Điểm dễ đọc được điều chỉnh cho social media (có tính emoji, line breaks)
- **Sentiment Analysis** — Phân tích cảm xúc: tích cực, tiêu cực, truyền cảm hứng
- **Hashtag Effectiveness** — Đánh giá số lượng và chất lượng hashtag
- **CTA Strength** — Đo sức mạnh Call-to-Action
- **Engagement Prediction** — Dự đoán số likes, shares, comments

```python
from services.generation.analytics import ContentAnalyzer

analyzer = ContentAnalyzer()
report = analyzer.generate_report(
    "🚀 Khám phá HEMApilot - nền tảng AI quản lý social media! #AI #Automation",
    platform="twitter"
)
print(f"Điểm tổng: {report.overall_score}")
print(f"Gợi ý: {report.suggestions}")
```

### 2. 🎨 Brand Voice Guardian
> *Bảo vệ tính nhất quán giọng văn thương hiệu*

Sử dụng **TF-IDF Cosine Similarity** để so sánh bài viết mới với "brand voice profile":
- Tự học từ các bài viết mẫu của thương hiệu
- Phát hiện vi phạm từ cấm
- Kiểm tra phong cách emoji, hashtag theo brand guideline
- Tự động phê duyệt hoặc đề xuất chỉnh sửa

```python
from services.generation.brand_voice import BrandVoiceGuardian, BrandVoiceProfile

profile = BrandVoiceProfile(
    brand_name="HEMApilot",
    tone_keywords=["sáng tạo", "chuyên nghiệp", "thân thiện", "AI"],
    forbidden_words=["spam", "click bait"],
    example_posts=["🚀 AI đang thay đổi cách chúng ta làm marketing..."],
)
guardian = BrandVoiceGuardian(profile)
result = guardian.check_consistency("Bài viết mới cần kiểm tra...")
```

### 3. 🧪 A/B Testing Framework
> *So sánh hiệu suất nội dung bằng thống kê*

Framework A/B testing chuyên biệt cho social media, sử dụng **Wilson Score Interval** — phương pháp thống kê phù hợp hơn normal approximation cho tỷ lệ engagement nhỏ:

- Tạo và quản lý các biến thể nội dung
- Thu thập dữ liệu engagement real-time
- Xác định winner với **statistical significance**
- Tự động đề xuất chiến lược dựa trên kết quả

```python
from services.orchestrator.ab_testing import ABTestEngine

engine = ABTestEngine()
test = engine.create_test(
    name="Headline Test Q3",
    hypothesis="Emoji ở đầu bài tăng engagement 20%",
    variant_contents={
        "Có emoji": "🚀 HEMApilot ra mắt tính năng mới!",
        "Không emoji": "HEMApilot ra mắt tính năng mới!",
    },
)

# Sau khi thu thập đủ data
result = engine.analyze_test(test.test_id)
print(result.recommendation)  # "🏆 Biến thể 'Có emoji' thắng với +23.5%..."
```

### 4. 📅 Smart Scheduler (Bayesian Optimization)
> *Tìm "giờ vàng" đăng bài cho từng nền tảng*

Không chỉ đặt lịch, mà **tự học** từ dữ liệu engagement lịch sử:
- Bayesian update liên tục cập nhật mô hình
- Tối ưu riêng cho từng nền tảng (Twitter, LinkedIn, Facebook, Instagram)
- Content Calendar tự động với ưu tiên hóa
- Tránh trùng lặp lịch đăng bài

### 5. 🌏 Multilingual Content Adapter
> *Không chỉ dịch, mà "localize" cho từng thị trường*

Hỗ trợ 5 thị trường: 🇻🇳 Việt Nam, 🇺🇸 Mỹ, 🇯🇵 Nhật Bản, 🇰🇷 Hàn Quốc, 🇹🇭 Thái Lan
- Đề xuất hashtags trending theo từng thị trường
- Kiểm tra nhạy cảm văn hóa (emoji, giọng văn, format)
- Điều chỉnh formality level tự động
- Chuẩn bị metadata cho LLM localize chính xác

---

## 🏗️ Kiến trúc Hệ thống Microservices

```
┌─────────────────────────────────────────────────────────┐
│                    API Gateway / Client                  │
└──────────────────────┬──────────────────────────────────┘
                       │
         ┌─────────────▼──────────────┐
         │    🎛️ Orchestrator Service  │
         │    (Port 8000)              │
         │  ┌────────────────────────┐ │
         │  │ Smart Scheduler        │ │
         │  │ A/B Testing Engine     │ │
         │  │ Workflow Manager       │ │
         │  └────────────────────────┘ │
         └──┬────┬────┬────┬────┬─────┘
            │    │    │    │    │
    ┌───────▼┐ ┌▼────┐ ┌──▼──┐ ┌▼───────┐ ┌▼──────┐
    │📥 Ingest│ │✍️ Gen│ │🔍Vrf│ │📤Publsh│ │🖼️Media│
    │ Service │ │ Svc  │ │ Svc │ │Service │ │Service│
    │  :8001  │ │:8002 │ │:8003│ │ :8004  │ │:8005  │
    └─────────┘ └──────┘ └─────┘ └────────┘ └───────┘
```

### Mô tả từng Service

| Service | Port | Trách nhiệm |
|---------|------|-------------|
| **Orchestrator** | 8000 | Điều phối workflow, Smart Scheduler, A/B Testing |
| **Ingestion** | 8001 | Thu thập dữ liệu từ Slack, GitHub, YouTube, URL |
| **Generation** | 8002 | Tạo nội dung AI, Analytics Engine, Brand Voice, Multilingual |
| **Verification** | 8003 | Xác minh link, kiểm tra Reddit/Tweet |
| **Publishing** | 8004 | Đăng bài lên Twitter, LinkedIn (OAuth/Arcade) |
| **Media** | 8005 | Tìm kiếm, tạo, upload hình ảnh (Supabase) |

### Công nghệ sử dụng

| Layer | Công nghệ |
|-------|-----------|
| **Language** | Python 3.11+ |
| **API Framework** | FastAPI + Uvicorn |
| **AI/LLM** | LangGraph, LangChain, Anthropic Claude |
| **Data Validation** | Pydantic v2 |
| **Containerization** | Docker + Docker Compose |
| **Image Storage** | Supabase |
| **Social Media Auth** | Arcade, OAuth 2.0 |
| **Web Scraping** | FireCrawl |
| **Statistical Testing** | Wilson Score Interval (tự implement) |
| **Scheduling Algorithm** | Bayesian Optimization (tự implement) |

---

## 📦 Cài đặt & Chạy thử

### Yêu cầu

- Python 3.11+
- Docker & Docker Compose
- API Keys (xem phần [Cấu hình](#-cấu-hình))

### Chạy với Docker Compose

```bash
# Clone repository
git clone https://github.com/iamnearu/HEMApilot.git
cd HEMApilot

# Cấu hình biến môi trường
cp .env.quickstart.example .env
# Chỉnh sửa .env với API keys của bạn

# Khởi chạy toàn bộ hệ thống
docker compose up --build

# Kiểm tra health
curl http://localhost:8000/health
```

### Chạy từng service (Development)

```bash
# Cài đặt dependencies
cd services/orchestrator
pip install -e .

# Chạy service
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

---

## ⚙️ Cấu hình

Tạo file `.env` từ template và điền các API key:

```bash
# LLM
ANTHROPIC_API_KEY=your_key_here

# Web Scraping
FIRECRAWL_API_KEY=your_key_here

# Social Media Authentication
ARCADE_API_KEY=your_key_here
TWITTER_USER_ID=your_twitter_id
LINKEDIN_USER_ID=your_linkedin_id

# Image Storage
SUPABASE_URL=your_supabase_url
SUPABASE_SERVICE_ROLE_KEY=your_key_here

# Slack (tuỳ chọn)
SLACK_BOT_TOKEN=your_token_here
SLACK_CHANNEL_ID=your_channel_id
```

---

## 📖 API Documentation

Sau khi khởi chạy, truy cập Swagger UI tại:

- **Orchestrator**: http://localhost:8000/docs
- **Ingestion**: http://localhost:8001/docs
- **Generation**: http://localhost:8002/docs
- **Verification**: http://localhost:8003/docs
- **Publishing**: http://localhost:8004/docs
- **Media**: http://localhost:8005/docs

### Ví dụ API Calls

**Tạo bài viết từ URL:**
```bash
curl -X POST http://localhost:8000/api/v1/generate \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com/blog-post", "platforms": ["twitter", "linkedin"]}'
```

**Kiểm tra chất lượng nội dung:**
```bash
curl -X POST http://localhost:8002/api/v1/analyze \
  -H "Content-Type: application/json" \
  -d '{"content": "Bài viết cần phân tích...", "platform": "twitter"}'
```

**Gợi ý lịch đăng bài:**
```bash
curl -X GET http://localhost:8000/api/v1/schedule/suggest?platform=twitter
```

---

## 🗺️ Kế hoạch phát triển

### Đã hoàn thành ✅
- [x] Kiến trúc Microservices (6 services)
- [x] Docker Compose orchestration
- [x] Content Analytics Engine
- [x] Brand Voice Guardian (TF-IDF Cosine Similarity)
- [x] A/B Testing Framework (Wilson Score Interval)
- [x] Smart Scheduler (Bayesian Optimization)
- [x] Multilingual Content Adapter (5 thị trường)
- [x] Shared schemas với Pydantic v2

### Đang phát triển 🚧
- [ ] Hoàn thiện migration TypeScript → Python cho tất cả agents
- [ ] Dashboard real-time (React + WebSocket)
- [ ] Integration tests cho cross-service communication
- [ ] CI/CD pipeline

### Tương lai 🔮
- [ ] Thêm nền tảng: TikTok, Instagram, Facebook
- [ ] Competitor analysis module
- [ ] Auto-reply engine cho comments
- [ ] Visual content generation (DALL-E / Stable Diffusion)
- [ ] Mobile app (React Native)

---

## 🧑‍💻 Tác giả

**iamnearu** — Phát triển và thiết kế kiến trúc hệ thống

---

## 📄 Giấy phép

Dự án được phân phối theo giấy phép [MIT](LICENSE).

---

<p align="center">
  <strong>⭐ Nếu bạn thấy dự án hữu ích, hãy cho một Star trên GitHub!</strong>
</p>
