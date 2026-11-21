# TamaCore — Google Play release checklist

**Current status: preparation only.** The repository generates a GDevelop
source project and a separate playable browser demo. It does **not** yet
produce a signed Android App Bundle (.aab) or integrate live Google Play Billing.

## Monetization and player economy

The generated MONETIZATION_MANIFEST.json defines:
- Free daily coins: 100; optional rewarded ad: 40 coins, at most 3 verified rewards/day.
- 1 premium gem can convert to 20 soft coins; coins/gems cannot be cashed out.
- Paid items: optional gems, permanent rainbow cosmetic, remove ads.
- No loot boxes, forced advertising, or pay-to-survive mechanics.
- Google Play sets localized real-money prices; do not hardcode fake checkout prices.
- No entitlement or currency granted solely because the client says payment succeeded.
- Verify purchase tokens server-side with Google Play Developer API, handle
  acknowledgment/consumption, refund/revocation, idempotency, and restored purchases.
- Rewarded ads require a genuine user opt-in and verified reward callback.
- Disable real-money purchases until the full billing integration passes sandbox testing.

## Required before publishing

1. Create/verify a Google Play Console developer account and application.
2. Set final unique Android application ID, app title, publisher contact,
   age-appropriate store listing, descriptions, screenshots, feature graphic,
   app icon, and support email.
3. Produce an Android project from GDevelop, install supported Android build tools,
   generate a release .aab and configure Play App Signing.
4. Integrate current supported Google Play Billing Library in the Android app.
   Create and activate products in Play Console; test purchases and refunds.
5. Add a secure server for purchase token verification and persistent entitlements.
6. Integrate a compliant ads SDK only after consent, privacy and age requirements
   have been addressed; use test ad units in development.
7. Publish a real privacy policy; complete Play Data safety, app content,
   ads declaration, content rating, target audience and Families declarations
   as applicable. Disclose analytics, advertising identifiers, and SDK data.
8. Set the currently required target Android API level and confirm current
   Google Play policies before submission; they can change.
9. Run internal testing, closed testing if required for the developer account,
   and staged rollout with crash/performance monitoring.
10. Validate GDevelop project and Android build on real devices, including
    offline behavior, payments, ad rewards, restore, accessibility and localization.

**Never ship the placeholder IAP runtime as if it were live purchases.**
The current IAP_* variables are scaffolding, not a payment integration.

## Monetization design rationale

A Tamagotchi-style pet should not punish players for refusing purchases.
Normal care, feeding and progress should remain accessible through free play.
Sell cosmetics and convenience without making progression depend on spending.
Do not use artificial countdowns, deceptive discounts, randomized paid rewards,
or undisclosed exchange rates.
