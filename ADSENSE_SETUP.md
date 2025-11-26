# Google AdSense Setup Guide for PlotVote

## 🎯 Overview

PlotVote now has **sidebar banner ads** on all chapter pages. Free users see ads, subscribers get ad-free reading.

**Revenue:** $3-5 CPM (per 1,000 chapter views)
**Expected at 10K users:** $200-500/month initially, scaling up as traffic grows

---

## 📝 Step 1: Apply for Google AdSense

### 1. Sign up at Google AdSense

Go to: https://www.google.com/adsense/start/

**Click "Get Started"**

### 2. Fill in your details

- **Website URL:** Your PlotVote domain (e.g., plotvote.com or localhost for testing)
- **Email:** Your Google account email
- **Country:** Your location

### 3. Accept terms and submit application

**Approval time:** Usually 24-48 hours (can take up to 2 weeks)

**Requirements for approval:**
- ✅ Original content (your AI-generated stories count!)
- ✅ Clear navigation
- ✅ Privacy policy page
- ✅ About/Contact page
- ✅ At least 10-20 pages of content

**Tip:** You should be approved easily since PlotVote has unique, original content!

---

## 🔧 Step 2: Get Your Publisher ID

Once approved, you'll receive an email from Google.

### 1. Log in to AdSense Dashboard

Go to: https://www.google.com/adsense

### 2. Find your Publisher ID

- Look in the top navigation bar
- Your Publisher ID looks like: **ca-pub-1234567890123456**
- It starts with `ca-pub-` followed by 16 digits

### 3. Copy your Publisher ID

You'll need this in Step 4!

---

## 🎨 Step 3: Create Ad Units

You need to create **2 ad units** for the chapter sidebar.

### 1. Go to "Ads" → "By ad unit"

In your AdSense dashboard, click:
- **Ads** (left sidebar)
- **By ad unit**
- **Display ads**

### 2. Create First Ad Unit

**Name:** `PlotVote Chapter Sidebar 1`
**Type:** Display ads
**Size:** Responsive

**Click "Create"**

### 3. Copy the Ad Slot ID

After creating, you'll see code like this:

```html
<ins class="adsbygoogle"
     data-ad-client="ca-pub-1234567890123456"
     data-ad-slot="9876543210"></ins>
```

**Copy the `data-ad-slot` number:** `9876543210`

This is your **Ad Slot ID** for the first ad unit.

### 4. Create Second Ad Unit

Repeat the process:

**Name:** `PlotVote Chapter Sidebar 2`
**Type:** Display ads
**Size:** Responsive

**Copy the second Ad Slot ID**

---

## 💻 Step 4: Add Your IDs to PlotVote

Now you need to add your Publisher ID and Ad Slot IDs to the code.

### 1. Open the chapter template

File: `/Users/jiegou/Downloads/plotvote/stories/templates/stories/chapter_detail.html`

### 2. Find the placeholder code (line ~134)

Look for:
```html
<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-XXXXXXXXXX"
```

### 3. Replace the placeholders

**Replace `ca-pub-XXXXXXXXXX`** with your real Publisher ID (in 3 places):

```html
<!-- Replace this -->
<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-XXXXXXXXXX"

<!-- With your real ID -->
<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-1234567890123456"
```

**Replace `YYYYYYYYYY`** with your first Ad Slot ID:

```html
<!-- Replace this -->
data-ad-slot="YYYYYYYYYY"

<!-- With your real slot ID -->
data-ad-slot="9876543210"
```

**Replace `ZZZZZZZZZZ`** with your second Ad Slot ID (around line 166):

```html
<!-- Replace this -->
data-ad-slot="ZZZZZZZZZZ"

<!-- With your real slot ID -->
data-ad-slot="1234567890"
```

### 4. Save the file

Make sure to save `chapter_detail.html` after editing!

---

## 🧪 Step 5: Test Your Ads

### 1. Restart Django server

```bash
python manage.py runserver
```

### 2. Visit a chapter page

Example: http://localhost:8000/story/your-story-slug/1/

### 3. What you should see

**For FREE USERS (not subscribed):**
- Two ad boxes in the sidebar
- "Advertisement" label
- Ads will show after ~10 minutes (Google needs to crawl your site)
- Initially you might see blank boxes (normal)

**For SUBSCRIBERS:**
- "Ad-Free Reading" badge instead of ads
- No ads anywhere

### 4. Initial ad display

**First 24 hours:** Ads might not show (Google is reviewing your site)
**After approval:** Ads appear automatically
**Blank ads:** Normal for first few hours

---

## 📊 Step 6: Monitor Revenue

### 1. Check AdSense Dashboard

Go to: https://www.google.com/adsense

**Metrics to watch:**
- **Page views:** How many chapter pages were viewed
- **Impressions:** How many times ads were shown
- **Clicks:** How many users clicked ads
- **RPM (Revenue Per Thousand):** Your CPM rate
- **Earnings:** Total revenue

### 2. Expected revenue

**Formula:** (Ad Impressions ÷ 1,000) × CPM

**Example:**
- 10,000 chapter views/month
- CPM = $4
- Revenue = (10,000 ÷ 1,000) × $4 = **$40/month**

**As you scale:**
- 100,000 views/month = $400/month
- 500,000 views/month = $2,000/month
- 1,000,000 views/month = $4,000/month

---

## 🚀 Optimization Tips

### 1. Increase ad value

- **Write more stories** → More pages → More ad inventory
- **Improve content quality** → Longer read times → More ad views
- **SEO optimization** → More organic traffic → More revenue

### 2. Ad placement tips

✅ **Current setup is good:**
- Sidebar ads are non-intrusive
- Visible without blocking content
- Responsive (works on mobile)

❌ **Don't:**
- Add too many ads (hurts user experience)
- Click your own ads (violates AdSense TOS)
- Ask users to click ads

### 3. Upgrade path

**Once you reach 50K+ monthly visitors:**
- Apply for **Google Ad Manager** (higher CPMs: $8-15)
- Enable video ads (even higher revenue)
- Work with premium ad networks

---

## 🛡️ AdSense Policies

### ✅ Do:
- ✅ Create original, valuable content
- ✅ Respect user privacy (have privacy policy)
- ✅ Make ads clearly labeled as "Advertisement"
- ✅ Keep site navigation clear

### ❌ Don't:
- ❌ Click your own ads (auto-ban)
- ❌ Ask users to click ads ("please click to support us")
- ❌ Place ads on pages with prohibited content
- ❌ Generate fake traffic

**Violation = Account suspension** (very strict!)

---

## 🎯 Current Implementation Summary

### What's working now:

**Ad Display Logic:**
```python
if user.has_active_subscription():
    # Show "Ad-Free" badge
else:
    # Show 2 AdSense banners in sidebar
```

**Tracking:**
- Every chapter view by non-subscribers is tracked in `AdView` model
- You can see ad impressions in Django admin
- Use this data + AdSense revenue to calculate CPM

**Subscriber Benefits:**
- No ads anywhere
- Clean "Ad-Free Reading" badge
- Incentive for free users to upgrade

---

## 📈 Revenue Projections

### Scenario: 10,000 Users

**User breakdown:**
- 7,000 free users (see ads)
- 3,000 subscribers (ad-free)

**Monthly chapter reads:**
- 7,000 free users × 10 chapters = 70,000 ad impressions

**Revenue:**
- 70,000 impressions ÷ 1,000 × $4 CPM = **$280/month**

**Plus subscription revenue:**
- 1,500 users × $4.99 Reader = $7,485/mo
- 1,000 users × $9.99 Writer = $9,990/mo
- 500 users × $19.99 Pro = $9,995/mo
- **Total subscription: $27,470/mo**

**Combined Total: ~$27,750/month** 🚀

---

## 🔍 Troubleshooting

### Problem: Ads not showing

**Solutions:**
1. **Wait 24-48 hours** (Google needs to approve site)
2. **Check Publisher ID** (must start with `ca-pub-`)
3. **Verify Ad Slot IDs** (16-digit numbers)
4. **Check browser console** (F12) for errors
5. **Disable ad blockers** (they hide test ads too)

### Problem: "AdSense account not approved"

**Solutions:**
1. **Add more content** (20+ story chapters minimum)
2. **Create privacy policy** page
3. **Add contact/about** pages
4. **Remove copyright violations** (only original content)
5. **Reapply after 2 weeks**

### Problem: Low CPM (under $2)

**Causes:**
- New site (builds over time)
- Low-value traffic (geography matters)
- Poor content quality
- Ad blocker usage

**Solutions:**
- Write higher-quality, longer stories
- Target US/UK/Canada traffic (higher CPM)
- Improve SEO
- Wait (CPM increases with time)

---

## ✅ Quick Setup Checklist

- [ ] Applied to Google AdSense
- [ ] Got approved (received email)
- [ ] Copied Publisher ID (ca-pub-XXXXXXXXXX)
- [ ] Created 2 ad units in AdSense dashboard
- [ ] Copied both Ad Slot IDs
- [ ] Updated `chapter_detail.html` with real IDs (replaced XXXXXXXXXX, YYYYYYYYYY, ZZZZZZZZZZ)
- [ ] Saved file and restarted Django
- [ ] Tested on a chapter page (saw ad boxes)
- [ ] Waited 24-48 hours for ads to populate
- [ ] Checked AdSense dashboard for impressions

---

## 🎉 You're All Set!

Your ad system is now live! Free users will see ads, subscribers enjoy ad-free reading, and you earn revenue from every chapter view.

**Next steps:**
1. Wait for AdSense approval (24-48 hours)
2. Add your IDs to the template
3. Test on localhost
4. Deploy to production
5. Watch revenue grow! 📈

**Need help?** Check the AdSense Help Center: https://support.google.com/adsense

---

Happy monetizing! 💰
