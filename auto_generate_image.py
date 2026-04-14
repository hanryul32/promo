"""
auto_generate_image.py
使用 Google Gemini Imagen 3 自動生成韓律 Han Ryul 生活情境照片。
- 不需要本機 GPU，直接在 GitHub Actions 執行（使用 GEMINI_API_KEY）
- 照片風格：韓系美女，每天依日期輪換不同情境/穿搭，偶爾加入朋友
- 注意：每月免費額度約 2000 張 (Imagen 3 free tier)
"""

import os
import random
from datetime import datetime

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")

# ──────────────────────────────────────────────
# 韓律人物基礎描述（每次都帶入，保持一致風格）
# ──────────────────────────────────────────────
HANRYUL_BASE = (
    "a beautiful Korean woman in her mid-20s, "
    "natural Korean beauty with defined almond-shaped eyes and double eyelids, "
    "delicate small nose, soft fair porcelain skin, "
    "natural dewy Korean-style makeup, long silky black hair, "
    "slender figure, warm and gentle expression, "
    "photorealistic, high-quality lifestyle photography, natural lighting"
)

FRIEND_BASE = (
    "a cheerful young East Asian woman with short wavy hair, "
    "bright eyes and a warm smile, casual stylish outfit"
)

# ──────────────────────────────────────────────
# 情境清單：(類型, 情境描述)
# solo = 獨照，friends = 含朋友
# ──────────────────────────────────────────────
SCENARIOS = [
    # === 早晨 / 咖啡 ===
    ("solo",
     "sitting in a cozy Korean cafe with a latte art coffee on the table, "
     "warm morning sunlight through window, wearing a white linen blouse, "
     "cream-tone interior background"),
    ("solo",
     "holding a dalgona coffee outdoors, cherry blossom tree behind, "
     "spring morning, light pink dress, soft bokeh"),
    # === 街拍 / 購物 ===
    ("solo",
     "candid street photography in Myeongdong Seoul, "
     "wearing trendy Korean puffer jacket and sneakers, autumn, "
     "shopping bags in hand, warm golden-hour light"),
    ("solo",
     "window shopping on a boutique street, colorful storefronts, "
     "wearing an oversized blazer and wide-leg pants, city vibe"),
    # === 居家 / 保養 ===
    ("solo",
     "holding a skincare serum bottle with both hands, "
     "minimal white bedroom interior, soft natural window light, "
     "wearing cozy white loungewear, clean and fresh aesthetic"),
    ("solo",
     "sitting cross-legged on a bed reading a book, soft pastel duvet, "
     "afternoon sunlight streaming in, wearing a cute casual set"),
    # === 美食 ===
    ("solo",
     "enjoying a brunch plate with avocado toast and iced matcha, "
     "trendy all-day restaurant, wearing a lemon-yellow dress, "
     "marble table top, fresh flowers"),
    ("solo",
     "at a night market holding spicy tteokbokki, vibrant neon signs, "
     "casual denim jacket, happy candid expression"),
    # === 戶外 / 自然 ===
    ("solo",
     "walking through a rose garden, wearing a flowy floral midi skirt, "
     "golden hour glow, hand touching pink roses"),
    ("solo",
     "at a Han River park, sitting on a picnic blanket, "
     "wearing casual summer coord, blue sky, soft breeze"),
    # === 夜間 / 派對 ===
    ("solo",
     "city rooftop at sunset, wearing an elegant minimalist black dress, "
     "skyline behind with bokeh city lights, confident pose"),
    ("solo",
     "at a cozy wine bar, holding a glass of rosé, "
     "warm candlelight, wearing a chic burgundy top"),
    # === 與朋友同框 ===
    ("friends",
     "both laughing and walking together holding bubble tea cups, "
     "trendy street background, casual matching outfits, natural candid"),
    ("friends",
     "taking a selfie together at a K-beauty store, "
     "both holding skincare products, bright colorful shelves behind, big smiles"),
    ("friends",
     "rooftop cafe, both sitting across a small table, "
     "iced drinks, golden-hour light, relaxed happy atmosphere"),
    ("friends",
     "at an amusement park, both holding cotton candy, "
     "colorful fairground background, wearing cute matching headbands"),
]

# 朋友有時用不同外型（模擬 Nano Banana 2 風格：可愛感）
FRIEND_VARIANTS = [
    FRIEND_BASE,
    ("a cute East Asian girl with bob haircut, rosy cheeks, "
     "big expressive eyes, wearing a pastel outfit, fun and energetic vibe"),
    ("a stylish East Asian woman with long wavy brown hair, "
     "cat-eye makeup, wearing streetwear, cool confident attitude"),
]


def build_prompt(scenario_type: str, scenario_detail: str) -> str:
    day = datetime.now().timetuple().tm_yday
    friend_desc = FRIEND_VARIANTS[day % len(FRIEND_VARIANTS)]

    if scenario_type == "friends":
        return (
            f"A candid lifestyle photo of {HANRYUL_BASE}, "
            f"with {friend_desc}, "
            f"{scenario_detail}. "
            "Portrait orientation, social-media ready, soft warm color grading."
        )
    else:
        return (
            f"A lifestyle portrait of {HANRYUL_BASE}, "
            f"{scenario_detail}. "
            "Portrait orientation, social-media ready, soft warm color grading."
        )


def generate_image() -> tuple:
    """
    生成韓律的生活情境圖片。
    回傳 (image_bytes: bytes, mime_type: str) 或 (None, None)。
    """
    if not GEMINI_API_KEY:
        print("[ImageGen] 未設定 GEMINI_API_KEY，跳過生成")
        return None, None

    try:
        from google import genai
        from google.genai import types

        client = genai.Client(api_key=GEMINI_API_KEY)

        day = datetime.now().timetuple().tm_yday
        scenario_type, scenario_detail = SCENARIOS[day % len(SCENARIOS)]
        prompt = build_prompt(scenario_type, scenario_detail)

        print(f"[ImageGen] 情境: {scenario_detail[:60]}...")

        response = client.models.generate_images(
            model="imagen-3.0-generate-001",
            prompt=prompt,
            config=types.GenerateImagesConfig(
                number_of_images=1,
                aspect_ratio="4:5",       # 接近 IG/FB 直式比例
                safety_filter_level="BLOCK_SOME",
                person_generation="ALLOW_ADULT",
            ),
        )

        if response.generated_images:
            image_bytes = response.generated_images[0].image.image_bytes
            print("[ImageGen] ✅ 圖片生成成功")
            return image_bytes, "image/png"

    except Exception as e:
        print(f"[ImageGen] ❌ 生成失敗: {e}")

    return None, None


if __name__ == "__main__":
    # 本機測試：生成一張並存到 output/test_generated.png
    import os
    img_bytes, mime = generate_image()
    if img_bytes:
        out = os.path.join(os.path.dirname(__file__), "output", "test_generated.png")
        os.makedirs(os.path.dirname(out), exist_ok=True)
        with open(out, "wb") as f:
            f.write(img_bytes)
        print(f"[ImageGen] 已儲存到 {out}")
    else:
        print("[ImageGen] 無圖片產生")
