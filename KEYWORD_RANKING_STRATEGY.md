# Keyword Ranking Strategy for PlotVote

## Current Situation

**Target Keywords:**
- "crowdsourced storytelling" (Low competition, ~210 searches/month)
- "ai storytelling" (Medium competition, ~1,900 searches/month)
- "collaborative storytelling" (Low competition, ~590 searches/month)
- "interactive fiction" (High competition, ~3,600 searches/month)

**Challenge:** Brand new domain with no backlinks or authority yet.

**Timeline:** Expect 3-6 months minimum to see results, 6-12 months to reach page 1.

---

## Quick Wins (Do These Now)

### 1. Optimize Homepage for Primary Keywords

**Current homepage title:**
```
PlotVote - Collaborative AI Storytelling Platform
```

**Better title (60 chars, keyword-rich):**
```
PlotVote - AI Storytelling & Crowdsourced Fiction Platform
```

**Update meta description to include ALL target keywords:**
```
Create collaborative stories with AI. Join our crowdsourced storytelling platform where communities write interactive fiction together. Vote on plot twists and shape AI-generated narratives.
```

### 2. Add Keyword-Rich Content to Homepage

Add a section explaining what PlotVote is with natural keyword usage:

```html
<section class="py-12 bg-white">
    <div class="max-w-4xl mx-auto px-4">
        <h2 class="text-3xl font-bold mb-6">The Future of Crowdsourced Storytelling</h2>
        <p class="text-lg text-gray-700 mb-4">
            PlotVote combines <strong>AI storytelling</strong> with <strong>collaborative writing</strong>
            to create a unique <strong>interactive fiction</strong> platform. Our community-driven approach
            to <strong>crowdsourced storytelling</strong> lets readers become co-authors.
        </p>
        <p class="text-lg text-gray-700 mb-4">
            Unlike traditional storytelling platforms, PlotVote uses advanced AI to generate chapters
            based on community votes. Each story evolves through <strong>collective creativity</strong>,
            making every narrative truly unique.
        </p>
        <h3 class="text-2xl font-bold mb-4 mt-8">How Collaborative Storytelling Works</h3>
        <ul class="space-y-3 text-gray-700">
            <li>✓ Authors pitch story ideas to the community</li>
            <li>✓ Readers vote on plot directions and story prompts</li>
            <li>✓ AI generates chapters based on winning prompts</li>
            <li>✓ The story evolves through community participation</li>
        </ul>
    </div>
</section>
```

### 3. Create Dedicated Landing Pages

Create these new pages targeting specific keywords:

**a) `/ai-storytelling/` - Complete landing page**
**b) `/crowdsourced-storytelling/` - Complete landing page**
**c) `/interactive-fiction/` - Complete landing page**

### 4. Update Existing Content

Add keywords naturally to:
- Story descriptions
- Genre descriptions
- About/how it works sections
- Footer content

---

## Implementation: Update Homepage

Let me show you exactly what to update:

### Update Homepage View (stories/views.py)

Add SEO context to homepage:

```python
def homepage(request):
    # ... existing code ...

    context = {
        'active_stories': active_stories,
        'completed_stories': completed_stories,
        'pitched_stories': pitched_stories,
        'language_choices': Story.LANGUAGE_CHOICES,
        'selected_language': language_filter,

        # SEO meta
        'meta_title': 'PlotVote - AI Storytelling & Crowdsourced Fiction Platform',
        'meta_description': 'Create collaborative stories with AI. Join our crowdsourced storytelling platform where communities write interactive fiction together. Vote on plot twists and shape AI-generated narratives.',
        'meta_keywords': 'ai storytelling, crowdsourced storytelling, collaborative writing, interactive fiction, community stories, AI-generated stories',
    }

    return render(request, 'stories/homepage.html', context)
```

### Update Homepage Template

Add this section to `stories/templates/stories/homepage.html`:

```html
{% block meta_title %}PlotVote - AI Storytelling & Crowdsourced Fiction Platform{% endblock %}
{% block meta_description %}Create collaborative stories with AI. Join our crowdsourced storytelling platform where communities write interactive fiction together. Vote on plot twists and shape AI-generated narratives.{% endblock %}
{% block meta_keywords %}ai storytelling, crowdsourced storytelling, collaborative writing, interactive fiction{% endblock %}

<!-- Add this content section after the hero/main section -->
<section class="py-16 bg-white">
    <div class="max-w-6xl mx-auto px-4">
        <h2 class="text-4xl font-bold text-center mb-4">The Future of Crowdsourced Storytelling</h2>
        <p class="text-xl text-gray-600 text-center mb-12 max-w-3xl mx-auto">
            Experience the next evolution of collaborative writing with AI-powered interactive fiction
        </p>

        <div class="grid md:grid-cols-2 gap-8 mb-12">
            <div class="bg-gradient-to-br from-purple-50 to-indigo-50 p-8 rounded-xl">
                <h3 class="text-2xl font-bold mb-4 text-indigo-900">🤖 AI Storytelling</h3>
                <p class="text-gray-700 leading-relaxed">
                    Our advanced AI storytelling engine generates compelling chapters based on
                    community votes. Unlike traditional AI writing tools, PlotVote combines
                    human creativity with AI capabilities to create truly unique narratives.
                </p>
            </div>

            <div class="bg-gradient-to-br from-pink-50 to-purple-50 p-8 rounded-xl">
                <h3 class="text-2xl font-bold mb-4 text-purple-900">👥 Crowdsourced Fiction</h3>
                <p class="text-gray-700 leading-relaxed">
                    Join thousands of writers and readers in our crowdsourced storytelling
                    community. Vote on plot directions, submit story prompts, and watch as
                    collaborative stories unfold in real-time.
                </p>
            </div>
        </div>

        <div class="bg-gray-50 rounded-xl p-8 mb-12">
            <h3 class="text-2xl font-bold mb-6">How Collaborative Storytelling Works on PlotVote</h3>
            <div class="grid md:grid-cols-4 gap-6">
                <div class="text-center">
                    <div class="w-16 h-16 bg-indigo-600 rounded-full flex items-center justify-center mx-auto mb-4 text-white text-2xl font-bold">1</div>
                    <h4 class="font-semibold mb-2">Pitch Your Story</h4>
                    <p class="text-sm text-gray-600">Authors submit story ideas for community voting</p>
                </div>
                <div class="text-center">
                    <div class="w-16 h-16 bg-indigo-600 rounded-full flex items-center justify-center mx-auto mb-4 text-white text-2xl font-bold">2</div>
                    <h4 class="font-semibold mb-2">Community Votes</h4>
                    <p class="text-sm text-gray-600">Readers vote on plot directions and story prompts</p>
                </div>
                <div class="text-center">
                    <div class="w-16 h-16 bg-indigo-600 rounded-full flex items-center justify-center mx-auto mb-4 text-white text-2xl font-bold">3</div>
                    <h4 class="font-semibold mb-2">AI Generates</h4>
                    <p class="text-sm text-gray-600">Our AI creates chapters based on winning prompts</p>
                </div>
                <div class="text-center">
                    <div class="w-16 h-16 bg-indigo-600 rounded-full flex items-center justify-center mx-auto mb-4 text-white text-2xl font-bold">4</div>
                    <h4 class="font-semibold mb-2">Story Evolves</h4>
                    <p class="text-sm text-gray-600">The narrative grows through collective creativity</p>
                </div>
            </div>
        </div>

        <div class="prose prose-lg max-w-4xl mx-auto">
            <h3 class="text-2xl font-bold mb-4">Why PlotVote is Different from Traditional Interactive Fiction</h3>
            <p class="text-gray-700 mb-4">
                Traditional <strong>interactive fiction</strong> platforms give you predetermined choices.
                PlotVote takes <strong>collaborative writing</strong> to the next level by combining:
            </p>
            <ul class="space-y-2 text-gray-700">
                <li>✓ <strong>Community-driven creativity</strong> - Every reader has a voice</li>
                <li>✓ <strong>AI-powered generation</strong> - Stories are written in real-time</li>
                <li>✓ <strong>Democratic storytelling</strong> - The best ideas win through voting</li>
                <li>✓ <strong>Unlimited possibilities</strong> - No pre-written paths or limitations</li>
            </ul>

            <h3 class="text-2xl font-bold mb-4 mt-8">Join the Crowdsourced Storytelling Revolution</h3>
            <p class="text-gray-700 mb-4">
                Whether you're a writer looking to engage with readers, or a reader who wants
                to influence your favorite stories, PlotVote offers a unique platform for
                <strong>AI storytelling</strong> and <strong>collaborative fiction</strong>.
            </p>
            <p class="text-gray-700 mb-6">
                Create your free account today and start participating in stories shaped by
                community votes. Experience the future of <strong>crowdsourced storytelling</strong>!
            </p>
        </div>
    </div>
</section>
```

---

## Content Marketing Strategy

### 1. Start a Blog

Create `/blog/` with articles targeting keywords:

**Article Ideas (Write these ASAP):**

1. **"What is Crowdsourced Storytelling? A Complete Guide"** (2000+ words)
   - Target: "crowdsourced storytelling"
   - Include examples, benefits, how PlotVote works
   - Internal links to story examples

2. **"AI Storytelling in 2025: How AI is Transforming Creative Writing"** (2500+ words)
   - Target: "ai storytelling"
   - Discuss AI writing tools, benefits, limitations
   - Position PlotVote as hybrid solution

3. **"10 Best Interactive Fiction Platforms for Writers and Readers"** (3000+ words)
   - Target: "interactive fiction"
   - List competitors, compare features
   - Objectively include PlotVote with unique benefits

4. **"Collaborative Writing: How Communities Create Better Stories"** (2000+ words)
   - Target: "collaborative writing"
   - Case studies of successful PlotVote stories
   - Tips for effective community storytelling

5. **"How to Write Engaging Story Prompts for AI Generation"** (1500+ words)
   - Target: long-tail keywords
   - Practical guide for PlotVote users
   - Encourages account creation

### 2. Create Resource Pages

**a) `/resources/` - Hub page**
**b) `/how-it-works/` - Detailed explainer with keywords**
**c) `/examples/` - Showcase best stories**
**d) `/community-guidelines/` - Build trust**

### 3. User-Generated Content

Encourage users to:
- Write detailed story descriptions (more content = better SEO)
- Add rich chapter titles and summaries
- Comment on chapters (more engagement signals)

---

## Off-Page SEO (Critical for Rankings)

### Backlink Building Strategy

**Goal:** Get 20-50 quality backlinks in first 6 months

**High-Priority Actions:**

1. **Submit to Directories** (Week 1)
   - Product Hunt (MUST DO - can drive 1000s of visitors)
   - Indie Hackers
   - AlternativeTo (list under "Wattpad alternatives")
   - Slant.co
   - G2
   - Capterra

2. **Write Guest Posts** (Ongoing)
   - Medium (publish on "AI", "Writing" tags)
   - Dev.to (technical AI storytelling article)
   - Hackernoon (AI/startup focused)
   - Write for writing blogs, AI blogs

3. **Community Participation** (Daily)
   - Answer questions on:
     - Quora: "What are the best collaborative writing platforms?"
     - Reddit: r/writing, r/AIWriting, r/InteractiveFiction
     - Stack Exchange: Writers community
   - Include PlotVote link when genuinely helpful

4. **Partnerships**
   - Contact writing blogs for features
   - Reach out to AI newsletters
   - Connect with writing communities/Discord servers
   - Partner with creative writing courses

5. **Social Media**
   - Twitter: Share stories, engage with #WritingCommunity
   - Reddit: Share interesting stories (not spam)
   - Facebook: Writing groups
   - LinkedIn: Content about AI + creativity

### HARO (Help a Reporter Out)

Sign up at helpareporter.com
- Answer journalist queries about AI, writing, storytelling
- Free press mentions = high-authority backlinks

---

## Technical SEO Improvements

### 1. Add Schema Markup for Homepage

Add to homepage:

```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "WebApplication",
  "name": "PlotVote",
  "description": "AI-powered crowdsourced storytelling platform for collaborative interactive fiction",
  "applicationCategory": "EntertainmentApplication",
  "operatingSystem": "Web",
  "offers": {
    "@type": "Offer",
    "price": "0",
    "priceCurrency": "USD"
  },
  "featureList": [
    "AI Story Generation",
    "Crowdsourced Storytelling",
    "Community Voting",
    "Interactive Fiction",
    "Collaborative Writing"
  ],
  "url": "https://plotvote.com",
  "keywords": "ai storytelling, crowdsourced storytelling, collaborative writing, interactive fiction"
}
</script>
```

### 2. Improve Internal Linking

On every story page, add contextual links:
- "Explore more collaborative stories →"
- "Learn how AI storytelling works →"
- "Join our crowdsourced fiction community →"

### 3. Add FAQ Section

Add to homepage with schema markup:

```html
<section id="faq">
    <h2>Frequently Asked Questions About AI Storytelling</h2>

    <div itemscope itemprop="mainEntity" itemtype="https://schema.org/Question">
        <h3 itemprop="name">What is crowdsourced storytelling?</h3>
        <div itemscope itemprop="acceptedAnswer" itemtype="https://schema.org/Answer">
            <div itemprop="text">
                <p>Crowdsourced storytelling is a collaborative approach to fiction writing where
                a community of readers and writers work together to create and shape narratives.
                On PlotVote, readers vote on story directions, submit plot ideas, and influence
                how AI-generated chapters unfold.</p>
            </div>
        </div>
    </div>

    <!-- Add 5-10 more FAQs targeting keywords -->
</section>
```

---

## Analytics & Tracking

### Setup Google Search Console

1. Add property: https://plotvote.com
2. Submit sitemap
3. Monitor:
   - Which keywords you rank for
   - Click-through rates
   - Impressions vs clicks
   - Indexing issues

### Track Keyword Rankings

Use these free tools:
- Google Search Console (built-in)
- Ubersuggest (free tier)
- AnswerThePublic (keyword ideas)

### Monitor Competition

Track these competitors:
- Wattpad (huge authority, hard to beat)
- Royal Road (writing platform)
- Scribophile (collaborative writing)

See what keywords they rank for, then target related long-tail keywords.

---

## Long-Tail Keyword Strategy

**Instead of targeting broad keywords immediately, target these easier long-tail keywords:**

✅ **Easier to Rank (Target These First):**
- "ai generated story platform" (Low competition)
- "collaborative fiction writing online" (Low competition)
- "crowdsource story ideas" (Very low competition)
- "vote on story plots" (Very low competition)
- "community written stories" (Low competition)
- "ai storytelling platform free" (Low competition)

✅ **Question Keywords (Create content for these):**
- "how does crowdsourced storytelling work"
- "what is ai storytelling"
- "best collaborative writing platforms"
- "how to write interactive fiction"

---

## 6-Month Action Plan

### Month 1: Foundation
- [x] Technical SEO (DONE!)
- [ ] Optimize homepage with keywords
- [ ] Add content sections to homepage
- [ ] Submit to 10 directories
- [ ] Write first blog post
- [ ] Setup Google Search Console

### Month 2: Content Creation
- [ ] Write 4 blog posts (1 per week)
- [ ] Create landing pages for top 3 keywords
- [ ] Add FAQ section
- [ ] Submit to 10 more directories
- [ ] Start HARO

### Month 3: Outreach
- [ ] Write 2 guest posts
- [ ] Engage on Reddit/Quora daily
- [ ] Reach out to 20 writing blogs
- [ ] Launch on Product Hunt
- [ ] Write 4 more blog posts

### Month 4: Link Building
- [ ] Get 10 backlinks from guest posts
- [ ] Partner with 3 writing communities
- [ ] Create case studies from best stories
- [ ] Write 4 more blog posts

### Month 5: Amplification
- [ ] Repurpose blog content to Medium
- [ ] Create YouTube videos (if possible)
- [ ] Podcast outreach
- [ ] Write 4 more blog posts

### Month 6: Optimization
- [ ] Analyze rankings
- [ ] Double down on what's working
- [ ] Update underperforming content
- [ ] Build more backlinks
- [ ] Write 4 more blog posts

**Total: 24 blog posts, 50+ backlinks, 20+ directory listings**

---

## Realistic Expectations

### Timeline to Page 1:

- **"ai storytelling"** (competitive): 9-12 months
- **"crowdsourced storytelling"** (easier): 4-6 months
- **"collaborative fiction writing"** (easier): 3-5 months
- **Long-tail keywords**: 1-3 months

### Required Effort:

- **5-10 hours/week** minimum for content + outreach
- **Consistent publishing** (at least 1 article/week)
- **Active community engagement** (daily)

### Key Metrics to Track:

1. **Organic traffic** (expect slow growth)
2. **Keyword rankings** (track top 20 keywords)
3. **Backlinks** (aim for 5-10/month)
4. **Domain authority** (will grow slowly)

---

## Quick Wins This Week

1. **Update homepage title and meta description** (30 mins)
2. **Add keyword-rich content section to homepage** (2 hours)
3. **Submit to Product Hunt** (1 hour)
4. **Submit to 5 directories** (2 hours)
5. **Write first blog post** (4 hours)
6. **Setup Google Search Console** (30 mins)
7. **Answer 3 questions on Quora** (1 hour)

**Total time: ~11 hours for week 1**

---

## Remember

🎯 **SEO is a marathon, not a sprint**
- Don't expect overnight results
- Focus on quality content
- Build genuine relationships
- Provide real value

🚀 **The best SEO is a great product**
- Focus on user experience
- Create amazing stories
- Build an engaged community
- Word of mouth > any SEO trick

📊 **Track everything**
- What content performs best?
- Which keywords drive traffic?
- Where do backlinks come from?
- Adjust strategy based on data

---

## Tools & Resources

**Free SEO Tools:**
- Google Search Console (essential)
- Google Analytics (track traffic)
- Ubersuggest (keyword research - 3 free searches/day)
- AnswerThePublic (keyword ideas)
- HARO (journalist queries)

**Paid Tools (Optional but helpful):**
- Ahrefs ($99/mo) - Best for keyword research
- SEMrush ($119/mo) - Competitor analysis
- Surfer SEO ($59/mo) - Content optimization

---

## Need Help?

If you want me to:
1. Write the homepage content sections
2. Create the first blog post
3. Build landing pages for specific keywords
4. Set up structured data for FAQs
5. Create a blog system for PlotVote

Just let me know! I can help implement any of these.
