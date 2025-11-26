# Stripe Payment Integration Setup Guide

This guide will help you set up Stripe payment processing for PlotVote credit purchases.

---

## 🎯 Prerequisites

- Stripe account (sign up at https://stripe.com)
- PlotVote development environment running

---

## 📝 Step 1: Get Your Stripe API Keys

1. Go to https://dashboard.stripe.com/test/apikeys
2. You'll see two keys:
   - **Publishable key** (starts with `pk_test_`)
   - **Secret key** (starts with `sk_test_`)
3. Copy both keys

---

## 🔧 Step 2: Add Keys to Environment File

1. Open `/Users/jiegou/Downloads/plotvote/.env`
2. Add your Stripe keys:

```env
# Stripe API Configuration
STRIPE_PUBLISHABLE_KEY=pk_test_your_actual_key_here
STRIPE_SECRET_KEY=sk_test_your_actual_key_here
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret_here
```

**Replace** `your_actual_key_here` with your real keys from Step 1.

---

## 🌐 Step 3: Set Up Stripe Webhook (For Production)

Webhooks allow Stripe to notify your app when payments succeed.

### Option A: Local Testing with Stripe CLI (Recommended for Development)

1. **Install Stripe CLI:**
   ```bash
   brew install stripe/stripe-cli/stripe
   ```

2. **Login to Stripe:**
   ```bash
   stripe login
   ```

3. **Forward webhooks to local server:**
   ```bash
   stripe listen --forward-to localhost:8000/users/webhook/stripe/
   ```

4. **Copy the webhook signing secret** (starts with `whsec_`) and add to `.env`:
   ```env
   STRIPE_WEBHOOK_SECRET=whsec_abc123...
   ```

### Option B: Production Webhook Setup

1. Go to https://dashboard.stripe.com/webhooks
2. Click **+ Add endpoint**
3. Set endpoint URL: `https://yourdomain.com/users/webhook/stripe/`
4. Select events to listen to:
   - ✅ `checkout.session.completed`
5. Copy the **Signing secret** and add to `.env`

---

## 🧪 Step 4: Test the Payment Flow

### 1. Start your development server:
```bash
source venv/bin/activate
python manage.py runserver
```

### 2. (If using Stripe CLI) Start webhook listener in another terminal:
```bash
stripe listen --forward-to localhost:8000/users/webhook/stripe/
```

### 3. Visit the credits page:
```
http://localhost:8000/credits/
```

### 4. Click "Buy Now" on any package

### 5. Use Stripe test card:
- Card number: `4242 4242 4242 4242`
- Expiry: Any future date (e.g., `12/34`)
- CVC: Any 3 digits (e.g., `123`)
- ZIP: Any 5 digits (e.g., `12345`)

### 6. Complete the payment

### 7. Check that credits were added:
- You should be redirected back with a success message
- Check your credit balance in the navigation bar
- View transaction history on credits dashboard

---

## 🔍 Verify Payment Webhook

1. Check your terminal where `stripe listen` is running
2. You should see:
   ```
   checkout.session.completed [evt_xxx]
   ```

3. Check Django server logs for:
   ```
   Credits added: username received X credits
   ```

4. Check database:
   ```bash
   python manage.py shell
   from users.models import Purchase
   Purchase.objects.all()
   ```

---

## 💳 Stripe Test Cards

Use these test cards in development:

| Card Number | Scenario |
|-------------|----------|
| `4242 4242 4242 4242` | Success |
| `4000 0000 0000 0002` | Card declined |
| `4000 0025 0000 3155` | Requires authentication (3D Secure) |

---

## 🚀 Going Live (Production)

When ready to accept real payments:

1. **Switch to Live Mode** in Stripe Dashboard
2. **Get Live API Keys:**
   - Go to https://dashboard.stripe.com/apikeys
   - Copy **Live** keys (start with `pk_live_` and `sk_live_`)

3. **Update Production Environment Variables:**
   ```env
   STRIPE_PUBLISHABLE_KEY=pk_live_your_live_key
   STRIPE_SECRET_KEY=sk_live_your_live_key
   STRIPE_WEBHOOK_SECRET=whsec_your_live_webhook_secret
   ```

4. **Set up Live Webhook:**
   - Add endpoint at https://dashboard.stripe.com/webhooks
   - Use your production URL

5. **Verify Identity with Stripe:**
   - Stripe requires business verification to accept payments
   - Follow prompts in dashboard

---

## 🛠️ Troubleshooting

### Credits not added after payment?

**Check webhook logs:**
```bash
# In Stripe CLI terminal
stripe listen --forward-to localhost:8000/users/webhook/stripe/
```

**Check Django logs:**
Look for `Credits added: ...` message

**Verify webhook secret:**
Make sure `STRIPE_WEBHOOK_SECRET` in `.env` matches the one from `stripe listen`

### "No such checkout session" error?

**Restart Django server** after updating `.env` file with Stripe keys.

### Payment succeeded but redirected to error page?

**Check success URL** in `users/views.py` - should be:
```python
success_url=request.build_absolute_uri('/credits/success?session_id={CHECKOUT_SESSION_ID}')
```

---

## 📊 Monitoring Payments

### View Purchases in Django Admin:
1. Go to http://localhost:8000/admin/
2. Navigate to **Users > Purchases**
3. See all payment transactions

### View in Stripe Dashboard:
1. Go to https://dashboard.stripe.com/test/payments
2. See all successful/failed payments
3. Click on any payment for details

---

## 🔐 Security Best Practices

### ✅ DO:
- ✅ Use environment variables for API keys (never commit to git)
- ✅ Verify webhook signatures (already implemented)
- ✅ Use HTTPS in production
- ✅ Keep Stripe library updated: `pip install --upgrade stripe`

### ❌ DON'T:
- ❌ Never commit `.env` file with real keys
- ❌ Never use live keys in development
- ❌ Never skip webhook signature verification
- ❌ Never store card details (Stripe handles this)

---

## 📞 Support

- **Stripe Documentation:** https://stripe.com/docs
- **Stripe Support:** https://support.stripe.com
- **Test your integration:** https://stripe.com/docs/testing

---

## ✅ Quick Verification Checklist

Before going live, verify:

- [ ] Stripe keys added to `.env`
- [ ] Webhook endpoint set up
- [ ] Test purchase completes successfully
- [ ] Credits added to user account
- [ ] Transaction recorded in database
- [ ] Success/cancel redirects work
- [ ] Email receipts sent (Stripe automatic)
- [ ] Refunds work (test in Stripe dashboard)

---

## 🎉 You're All Set!

Your Stripe integration is complete. Users can now purchase credits and generate AI stories!

**Next Steps:**
1. Test thoroughly with test cards
2. Set up webhook monitoring
3. When ready, switch to live mode
4. Start accepting real payments!
