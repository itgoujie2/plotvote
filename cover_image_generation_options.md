# Cover Image Generation Options for PlotVote

## Overview
This document compares different AI image generation services for creating story cover images.

---

## Quick Recommendation

**For PlotVote: Use OpenAI DALL-E 3** ✅

**Reasons:**
- High quality, consistent results
- Same API you're likely already using for text generation
- Good prompt understanding (handles complex descriptions)
- Reasonable pricing for user-generated content
- Reliable API, good documentation
- Content policy aligned with storytelling use case

**Backup/Alternative: Stability AI (Stable Diffusion XL)** - Cheaper, more customizable

---

## Detailed Comparison

### 1. OpenAI DALL-E 3 ⭐ **RECOMMENDED**

**Pricing:**
- **Standard (1024x1024):** $0.040 per image
- **HD (1024x1792):** $0.080 per image
- **Standard (1792x1024):** $0.080 per image

**Quality:** ⭐⭐⭐⭐⭐ (Excellent)

**Pros:**
- ✅ Excellent prompt understanding (natural language)
- ✅ High-quality, artistic outputs
- ✅ Good for book covers, professional look
- ✅ Same API as your text generation (GPT)
- ✅ Built-in safety filters
- ✅ Consistent style and quality
- ✅ Great for fantasy, sci-fi, literary covers

**Cons:**
- ❌ More expensive than alternatives
- ❌ Less control over specific styles
- ❌ No fine-tuning on custom models
- ❌ 1-2 second generation time

**Best For:**
- Professional-looking book covers
- Complex scene descriptions
- Genre-appropriate artwork (fantasy, sci-fi, romance)

**API Endpoint:**
```python
from openai import OpenAI
client = OpenAI(api_key='your-api-key')

response = client.images.generate(
    model="dall-e-3",
    prompt="A fantasy book cover showing a lone warrior standing on a cliff overlooking a magical city at sunset, dramatic lighting, epic fantasy art style",
    size="1024x1024",  # or "1792x1024" for landscape
    quality="standard",  # or "hd" for better quality
    n=1,
)

image_url = response.data[0].url
```

**Documentation:** https://platform.openai.com/docs/guides/images

---

### 2. OpenAI DALL-E 2

**Pricing:**
- **1024x1024:** $0.020 per image (50% cheaper than DALL-E 3)
- **512x512:** $0.018 per image
- **256x256:** $0.016 per image

**Quality:** ⭐⭐⭐⭐ (Good)

**Pros:**
- ✅ Half the cost of DALL-E 3
- ✅ Still good quality for most use cases
- ✅ Same API as DALL-E 3
- ✅ Can generate variations of images

**Cons:**
- ❌ Lower quality than DALL-E 3
- ❌ Less accurate prompt following
- ❌ Older technology

**Best For:**
- Budget-conscious projects
- Testing/prototyping
- Users who want to generate many variations

---

### 3. Stability AI (Stable Diffusion XL) ⭐ **BUDGET OPTION**

**Pricing:**
- **Via Stability AI API:** ~$0.003-0.01 per image (much cheaper!)
- **Via Replicate:** ~$0.0055 per image
- **Self-hosted:** Free (requires GPU, ~$0.50-1.00/hour on cloud)

**Quality:** ⭐⭐⭐⭐ (Very Good)

**Pros:**
- ✅ **Much cheaper** than OpenAI
- ✅ Open source (can self-host)
- ✅ Highly customizable (LoRAs, fine-tuning)
- ✅ Multiple model versions (SDXL, SD 1.5, SD 2.1)
- ✅ Control over style with different models
- ✅ Supports negative prompts
- ✅ Fast generation (1-3 seconds)

**Cons:**
- ❌ More complex prompting required
- ❌ Less consistent quality without tuning
- ❌ Requires more technical knowledge
- ❌ Separate API from your text generation

**Best For:**
- High-volume image generation
- Budget-sensitive projects
- Need for specific art styles
- Technical teams comfortable with ML

**API Example (via Stability AI):**
```python
import requests

response = requests.post(
    "https://api.stability.ai/v1/generation/stable-diffusion-xl-1024-v1-0/text-to-image",
    headers={
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    },
    json={
        "text_prompts": [
            {
                "text": "Epic fantasy book cover, warrior on cliff, magical city, sunset, artstation style",
                "weight": 1
            },
            {
                "text": "blurry, bad quality, watermark, text, low resolution",
                "weight": -1  # Negative prompt
            }
        ],
        "cfg_scale": 7,
        "height": 1024,
        "width": 1024,
        "samples": 1,
        "steps": 30,
    },
)
```

**Documentation:** https://platform.stability.ai/docs/api-reference

---

### 4. Replicate (Multiple Models) ⭐ **FLEXIBILITY**

**Pricing:** Pay-per-use, varies by model
- **SDXL:** ~$0.0055 per image
- **Midjourney-style models:** ~$0.01 per image
- **Various fine-tuned models:** $0.002-0.02 per image

**Quality:** ⭐⭐⭐⭐ to ⭐⭐⭐⭐⭐ (Depends on model)

**Pros:**
- ✅ Access to many different models
- ✅ Easy to switch between models
- ✅ Good pricing
- ✅ Simple API
- ✅ Community-created models (anime, fantasy, realistic, etc.)
- ✅ No need to host infrastructure

**Cons:**
- ❌ Quality varies by model
- ❌ Some models slower than others
- ❌ Less corporate support than OpenAI

**Popular Models on Replicate:**
- `stability-ai/sdxl` - General purpose
- `lucataco/sdxl-fantasy` - Fantasy art
- `bytedance/sdxl-lightning` - Fast generation
- Various anime/manga models for different styles

**API Example:**
```python
import replicate

output = replicate.run(
    "stability-ai/sdxl:39ed52f2a78e934b3ba6e2a89f5b1c712de7dfea535525255b1aa35c5565e08b",
    input={
        "prompt": "Epic fantasy book cover art, professional, artstation trending",
        "negative_prompt": "text, watermark, low quality",
        "width": 1024,
        "height": 1024,
    }
)
```

**Documentation:** https://replicate.com/docs

---

### 5. Leonardo.ai

**Pricing:**
- **Free tier:** 150 tokens/day (~30 images)
- **Paid plans:** $10-30/month for higher limits
- **API:** Available on paid plans

**Quality:** ⭐⭐⭐⭐⭐ (Excellent, especially for fantasy/game art)

**Pros:**
- ✅ Excellent for fantasy, game art, character designs
- ✅ Multiple fine-tuned models for different styles
- ✅ Canvas editor for post-processing
- ✅ ControlNet support (pose control)
- ✅ Generous free tier

**Cons:**
- ❌ API less mature than OpenAI
- ❌ Monthly subscription model (not pure pay-per-use)
- ❌ Slower than DALL-E 3

**Best For:**
- Fantasy and sci-fi covers
- Character-focused artwork
- Teams wanting a web UI + API

**Website:** https://leonardo.ai

---

### 6. Midjourney (Third-Party APIs)

**Pricing:**
- **Official:** $10-60/month subscription (no official API)
- **Unofficial APIs:** ~$0.02-0.05 per image (via third-party services)

**Quality:** ⭐⭐⭐⭐⭐ (Excellent, artistic)

**Pros:**
- ✅ Stunning, artistic results
- ✅ Great for professional book covers
- ✅ Popular in creative community
- ✅ Excellent style consistency

**Cons:**
- ❌ **No official API** (uses Discord bot)
- ❌ Unofficial APIs are unreliable
- ❌ Subscription model (not pay-per-use)
- ❌ Against ToS to use unofficial APIs
- ❌ Not recommended for production

**Verdict:** Beautiful but not practical for API integration

---

### 7. Google Imagen / Adobe Firefly

**Status:** Limited availability

**Google Imagen:**
- Not publicly available yet
- Waitlist only

**Adobe Firefly:**
- Available via Adobe Creative Cloud
- API in beta (enterprise only)
- Excellent for commercial use (trained on licensed content)

**Verdict:** Not ready for indie developers yet

---

### 8. Self-Hosted Solutions

**Options:**
- Stable Diffusion via Automatic1111
- ComfyUI
- InvokeAI
- Hugging Face Diffusers

**Cost:**
- **Cloud GPU:** $0.50-1.50/hour (AWS, RunPod, Vast.ai)
- **Own GPU:** Initial cost $500-2000 (RTX 3060 to RTX 4090)

**Pros:**
- ✅ No per-image cost (after infrastructure)
- ✅ Full control and customization
- ✅ Privacy (data stays on your server)
- ✅ Can fine-tune models

**Cons:**
- ❌ Requires technical expertise
- ❌ Infrastructure management
- ❌ High upfront cost for hardware
- ❌ Scaling challenges

**Best For:**
- High volume (>10,000 images/month)
- Specific customization needs
- Privacy-sensitive applications

---

## Cost Comparison (Per 1000 Images)

| Service | Standard Quality | HD Quality | Notes |
|---------|-----------------|------------|-------|
| **DALL-E 3** | $40 | $80 | 1024x1024 / HD |
| **DALL-E 2** | $20 | N/A | 1024x1024 |
| **Stability AI (SDXL)** | $5-10 | N/A | Via API |
| **Replicate (SDXL)** | $5.50 | N/A | Per image |
| **Leonardo.ai** | $10-30/mo | N/A | Subscription |
| **Self-hosted SD** | $500-1500 | N/A | Cloud GPU cost |

**At 1,000 users generating 1 cover each:**
- DALL-E 3: $40
- DALL-E 2: $20
- Stable Diffusion: $5-10
- Break-even point for self-hosting: ~5,000-10,000 images

---

## Recommendation by Use Case

### For PlotVote (Beta / Early Stage)
**Start with: DALL-E 3**
- Reasons: Easy integration, high quality, same API as GPT
- Cost at 100 users: $4 (negligible)
- Cost at 1,000 users: $40 (acceptable)
- Cost at 10,000 users: $400 (manageable)

**Alternative: DALL-E 2**
- If budget is very tight
- 50% cost savings
- Still good quality

### For PlotVote (Growth / Scale)
**Switch to: Stability AI (SDXL)**
- When generating >5,000 images/month
- Cost savings: 75-80%
- Example: 10,000 images/month = $50-100 vs $400

**Consider: Self-hosted Stable Diffusion**
- When generating >20,000 images/month
- Requires DevOps capabilities
- Significant cost savings at scale

### For Premium Features
**Use: DALL-E 3 HD + Multiple variations**
- Premium users get higher quality
- Generate 3-4 options, let user choose
- Worth the premium price point

---

## Implementation Strategy

### Phase 1: MVP (Launch)
**Use DALL-E 3 Standard (1024x1024)**

```python
# stories/cover_generator.py
from openai import OpenAI
from django.conf import settings
import requests
from django.core.files.base import ContentFile

def generate_story_cover(story):
    """Generate a cover image for a story using DALL-E 3"""

    # Build prompt from story metadata
    prompt = f"""Professional book cover art for a {story.get_genre_display()} story titled "{story.title}".
    {story.description[:200]}
    Style: {story.get_genre_display()} cover art, professional, trending on artstation,
    dramatic lighting, no text, high quality digital art"""

    client = OpenAI(api_key=settings.OPENAI_API_KEY)

    try:
        response = client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size="1024x1024",
            quality="standard",
            n=1,
        )

        image_url = response.data[0].url

        # Download and save the image
        image_response = requests.get(image_url)
        if image_response.status_code == 200:
            story.cover_image.save(
                f"{story.slug}_cover.png",
                ContentFile(image_response.content),
                save=True
            )
            return True, "Cover image generated successfully!"

    except Exception as e:
        return False, f"Error generating cover: {str(e)}"

    return False, "Failed to generate cover image"
```

**Cost:** $0.04 per cover (very affordable)

### Phase 2: Multiple Options (Premium Feature)

```python
def generate_cover_options(story, num_variations=3):
    """Generate multiple cover options for user to choose from"""

    prompts = [
        # Different artistic styles
        f"Cinematic {story.genre} book cover, {story.description[:150]}",
        f"Minimalist {story.genre} cover design, {story.description[:150]}",
        f"Dramatic illustration {story.genre} style, {story.description[:150]}",
    ]

    results = []
    for prompt in prompts[:num_variations]:
        response = client.images.generate(
            model="dall-e-3",
            prompt=prompt + ", professional book cover, no text",
            size="1024x1024",
            quality="standard",
        )
        results.append(response.data[0].url)

    return results
```

**Cost:** $0.12 per story (3 variations) - only for premium users

### Phase 3: Scale Optimization

**Switch to Stability AI for standard tier:**

```python
def generate_cover_sdxl(story):
    """Generate cover using Stable Diffusion XL (cheaper for scale)"""

    import requests

    prompt = f"Professional {story.genre} book cover art, {story.description[:200]}, artstation, high quality"
    negative = "text, words, title, author name, watermark, low quality, blurry"

    response = requests.post(
        "https://api.stability.ai/v1/generation/stable-diffusion-xl-1024-v1-0/text-to-image",
        headers={
            "Authorization": f"Bearer {settings.STABILITY_API_KEY}",
        },
        json={
            "text_prompts": [
                {"text": prompt, "weight": 1},
                {"text": negative, "weight": -1}
            ],
            "cfg_scale": 7,
            "height": 1024,
            "width": 1024,
            "samples": 1,
            "steps": 30,
        },
    )

    # Process and save...
```

**Cost:** $0.005-0.01 per cover (75-90% savings)

---

## UI/UX Recommendations

### 1. Cover Generation Flow

**Option A: Automatic on Story Creation**
```
[Create Story] → [Story Details Form] → [Generate Cover Automatically] → [Story Created]
                                              ↓
                                    [Show generated cover]
                                    [Regenerate button if not satisfied]
```

**Option B: Optional Feature**
```
[Story Created] → [Story Dashboard]
                        ↓
                  [Generate Cover button]
                        ↓
                  [Cover generated]
                  [Use this / Regenerate / Upload custom]
```

**Option C: Premium Feature (Recommended)**
```
Free tier: Upload only
Premium: AI generation + upload custom
```

### 2. User Controls

**Basic (MVP):**
- Generate button
- Regenerate button (1-2 free regenerations)

**Advanced:**
- Style selector (Realistic / Artistic / Minimalist / Cinematic)
- Cover description customization
- Choose from 3-4 variations
- Edit AI prompt before generating

### 3. Pricing Tiers

**Free Tier:**
- Upload custom cover image only
- OR 1 free AI-generated cover per story

**Premium Tier ($9.99/month):**
- Unlimited cover generation
- 3 style variations per generation
- HD quality (1792x1024)
- Custom prompt editing

**Credit System:**
- 1 credit = 1 cover generation
- 3 credits = choose from 3 variations

---

## Sample Prompts by Genre

### Fantasy
```
"Epic fantasy book cover art showing [scene from story],
magical atmosphere, dramatic lighting, artstation trending,
professional cover illustration, detailed, cinematic,
no text or words"
```

### Science Fiction
```
"Sci-fi book cover with [futuristic scene],
sleek technology, space setting, cyberpunk aesthetic,
professional illustration, trending on artstation,
cinematic lighting, no text"
```

### Romance
```
"Romantic book cover art, [romantic scene],
soft lighting, dreamy atmosphere, professional romance cover,
elegant composition, trending on artstation,
pastel tones, no text"
```

### Mystery/Thriller
```
"Mystery thriller book cover, dark moody atmosphere,
[mysterious scene], noir style, dramatic shadows,
professional cover art, suspenseful, cinematic,
no text or words"
```

### Horror
```
"Horror book cover art, eerie atmosphere, [scary scene],
dark and ominous, professional horror illustration,
dramatic lighting, trending on artstation,
unsettling mood, no text"
```

---

## Testing Recommendations

### Before Launch:
1. **Generate 20-30 sample covers** across different genres
2. **Compare DALL-E 3 vs DALL-E 2 vs SDXL** quality
3. **User testing:** Show 10 users, get feedback
4. **A/B test:** Auto-generate vs manual upload (which gets more engagement?)

### Metrics to Track:
- Cover generation success rate
- User satisfaction (thumbs up/down on generated covers)
- Regeneration rate (how often users regenerate)
- Cost per successful cover
- Impact on story views (do AI covers get more clicks?)

---

## Action Plan

### Week 1: Setup & Testing
- [ ] Sign up for OpenAI API (if not already)
- [ ] Test DALL-E 3 API with sample prompts
- [ ] Generate 10 test covers (different genres)
- [ ] Evaluate quality

### Week 2: Development
- [ ] Create `cover_generator.py` module
- [ ] Add "Generate Cover" button to story creation flow
- [ ] Implement image download and storage
- [ ] Add error handling

### Week 3: UI/UX
- [ ] Design cover generation interface
- [ ] Add regenerate functionality
- [ ] Show cover preview before saving
- [ ] Add loading states

### Week 4: Launch
- [ ] Beta test with 10 users
- [ ] Monitor costs and quality
- [ ] Gather feedback
- [ ] Iterate based on feedback

---

## Cost Projections

### Scenario 1: Conservative (1,000 users, 20% use cover gen)
- 200 covers/month × $0.04 = **$8/month**
- Negligible cost ✅

### Scenario 2: Moderate (5,000 users, 30% use)
- 1,500 covers/month × $0.04 = **$60/month**
- Acceptable cost ✅

### Scenario 3: High Growth (20,000 users, 40% use)
- 8,000 covers/month × $0.04 = **$320/month**
- Consider switching to SDXL: **$40-80/month** (75% savings)

### Scenario 4: Scale (100,000 users, 50% use)
- 50,000 covers/month × $0.04 = **$2,000/month**
- **Switch to self-hosted or SDXL** ($250-500/month)

---

## Final Recommendation

### **Start Simple: DALL-E 3**

1. **Easiest integration** (same API as GPT)
2. **High quality** results out of the box
3. **Low cost** at early stage ($8-60/month)
4. **Reliable** and well-documented
5. **Can optimize later** when volume justifies it

### **Implementation Priority:**
```
Phase 1: DALL-E 3 basic generation ✅ (Week 1-2)
Phase 2: Style options + regenerate (Week 3-4)
Phase 3: Premium multi-variation (Month 2)
Phase 4: Cost optimization with SDXL (Month 6+)
```

### **Pricing Strategy:**
```
Free: Upload custom cover OR 1 AI generation per story
Premium: Unlimited generations + style choices + HD quality
```

---

**Need help with implementation? Let me know and I can:**
1. Write the complete Django integration code
2. Create the UI components
3. Set up the API calls and error handling
4. Build the admin interface for monitoring costs
