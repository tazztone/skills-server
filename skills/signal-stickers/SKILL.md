---
name: signal-stickers
description: Create, prepare, and upload custom Signal sticker packs. Use this skill whenever the user wants to make stickers for Signal, design a sticker pack, prepare sticker artwork, or upload stickers to Signal. Also triggers for questions about Signal sticker file formats, size requirements, or the upload workflow.
---

# Signal Sticker Pack Creator

A skill for creating and publishing custom Signal sticker packs — from artwork preparation through upload and sharing.

## Overview

Signal stickers are end-to-end encrypted like all Signal content. Sticker packs are **not linked to your Signal account** — once uploaded they cannot be edited or deleted, so get everything right before uploading.

Requires **Signal Desktop** linked to your phone to upload.

---

## File Requirements (Hard Rules)

| Property | Non-animated | Animated |
|---|---|---|
| Format | PNG **or** WebP | APNG only (no GIFs) |
| Max file size | 300 KB per sticker | 300 KB per sticker |
| Canvas size | 512 × 512 px | 512 × 512 px |
| Max animation length | — | 3 seconds |
| Recommended FPS | — | 30 or 60 FPS |
| Background | Transparent | Transparent |

**Pack limits:**
- Minimum: 1 sticker (Signal's current tooling accepts 1+; some older docs say 4 minimum — aim for at least 4 for a coherent pack)
- Maximum: **200 stickers** per pack
- Each sticker is a **separate file** — no sprite sheets
- Assign **exactly one emoji** per sticker

**Cover image:**
- Must be **512 × 512 px PNG or WebP**
- Defaults to the first sticker in the pack if not specified
- Can be a different image from the stickers

**Pack metadata (required):**
- Title
- Author name (displayed publicly — spell it correctly, you cannot edit after upload)

---

## Design Recommendations

- **16 px margin** around artwork on the 512 × 512 canvas — keeps edges from being clipped on small screens
- **Transparent background** — stickers appear on chat bubbles in both light and dark themes
- **Outline strokes** on artwork so it reads on both light and dark backgrounds
- Animated stickers should **loop seamlessly**
- The **first frame** of an animated sticker should express its main feeling or idea — older devices that don't support APNG show only the first frame as a still
- Animated stickers display the first frame as a still in the sticker selector on unsupported devices

---

## Workflow

### 1. Prepare Artwork

1. Create each sticker on a **512 × 512 px transparent canvas**
2. Keep artwork within a **480 × 480 px safe area** (16 px margin on all sides)
3. Export each sticker as a **separate PNG** (or WebP for non-animated, APNG for animated)
4. Verify each file is **under 300 KB** — flatten detail or reduce colors if over budget
5. Prepare your cover image (or let it default to the first sticker)

### 2. Open the Sticker Pack Creator

Two entry points:
- **Signal Desktop:** `File → Create/Upload Sticker Pack` — opens the creator in your web browser
- **Direct URL:** The Signal Sticker Pack Creator opens in your browser automatically from Signal Desktop

### 3. Add and Arrange Stickers

1. Import sticker files — you can **drag and drop** or click to select
2. Select multiple files at once to import in bulk (click and drag over files)
3. **Drag and drop** within the creator to reorder
4. **Hover over a sticker** to preview it in both light and dark themes
5. Select **Next** when all stickers are added

### 4. Assign Emojis

- Assign **one emoji per sticker** — this powers the emoji-suggestion feature in chat
- Select **Next** when done

### 5. Set Pack Metadata

- Enter a **Title**
- Enter an **Author** name (publicly visible — double-check spelling)
- Optionally choose a **cover sticker** (different from the first sticker if desired)
- ⚠️ **Make all changes now.** You cannot edit the pack after uploading.

### 6. Upload

1. Select **Next** and confirm the upload
2. Signal Desktop will prompt you to **Install** the pack
3. Open Signal Desktop and select **Install**

### 7. Share Your Pack

- From the web browser, **copy the share link** to distribute outside Signal
- Use the hashtag **`#makeprivacystick`** on social media so others can find your pack
- Anyone with the link can view and install the pack (link reveals Title and Author)

---

## Sending Stickers

Once a pack is installed:

**Android:** Tap the sticker icon (or emoji icon → sticker icon). Scroll vertically through packs. Tap to send. Or type an emoji — matching stickers appear above the keyboard.

**iOS:** Tap the sticker icon. Scroll horizontally through packs. Tap to send. Or type an emoji for suggestions.

**Desktop:** Click the sticker icon. Browse packs. Click to send.

---

## Managing Packs

**Install a received pack:** Tap a sticker in chat → scroll through the pack → select Install. Or tap sticker icon → `+` → Stickers you received → download icon.

**Uninstall a pack:** Tap sticker icon → `+` → (Desktop: Installed) → select X / Uninstall / tap pack for options.

**You cannot delete or edit an uploaded pack** — uninstalling only removes it from your device. To "update" a pack, upload a new one.

---

## FAQ

**Can I create stickers without a Signal account?**
No — Signal Desktop must be linked to your phone. Install Signal on your phone first, then link Signal Desktop.

**Can I put all stickers in one file?**
No — each sticker must be a separate file.

**What if my sticker is larger than 512 × 512 px?**
Signal resizes it to fit, but this can degrade quality. Export at exactly 512 × 512 px for best results.

**Do stickers save as drafts?**
No — closing the creator loses your work. Complete the upload in one session.

**Who can see my pack?**
Anyone who receives a sticker from it, or anyone you share the link with. The Title and Author are publicly visible.

**Can my cover be different from my stickers?**
Yes — you can choose any 512 × 512 px PNG/WebP as the cover.

**Where to find more packs?**
- Search `#makeprivacystick` on Twitter/X or other social platforms
- Curated packs: [Animals](https://signal.art/addstickers/), [Emoticons](https://signal.art/addstickers/), Clothes, Food, Weather
- Receive a sticker from someone else and install their pack
