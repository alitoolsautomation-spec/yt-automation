# YouTube Automation — Urdu Motivational Videos

Ye pipeline khud script likhta hai, AI voice banata hai, background clips
laga kar video assemble karta hai, aur seedha YouTube per upload kar deta
hai — din mein 2-3 dafa automatically.

## Aaj ke liye Setup Steps (roughly 1-2 ghantay)

### 1. Python environment
```bash
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
```
ImageMagick bhi install karein (title text overlay ke liye):
- Ubuntu/Debian: `sudo apt install imagemagick`
- Mac: `brew install imagemagick`
- Windows: imagemagick.org se installer

### 2. API Keys lein (sab ke free tiers available hain)
- **Anthropic (Claude)**: console.anthropic.com → API key
- **ElevenLabs**: elevenlabs.io → sign up → API key → Voice Library se
  ek Urdu-compatible ya multilingual voice choose karke uska Voice ID
  copy karein
- **Pexels**: pexels.com/api → free API key (unlimited, koi cost nahi)
- **YouTube Data API**:
  1. console.cloud.google.com → new project
  2. "YouTube Data API v3" enable karein
  3. OAuth consent screen setup karein (External, apna email add karein
     as test user)
  4. Credentials → Create OAuth Client ID → Desktop App
  5. `client_secret.json` download karke is folder mein rakhein

### 3. `.env` file banayein
`.env.example` ko copy karke `.env` banayein aur apni keys fill karein:
```bash
cp .env.example .env
```

### 4. Pehli baar apne laptop par ek dafa test/login run karein
```bash
python main.py
```
Pehli dafa YouTube upload par ek browser window khulegi jahan aap apne
Google account se login/authorize karenge. Ye sirf ek dafa, apne laptop
par hi karna hoga — is se ek `token.pickle` file ban jayegi jo cloud
mein use hogi (neeche step 5).

### 5. FREE Cloud Automation — GitHub Actions (laptop on rakhne ki zaroorat nahi)

Ye poori tarah **free** hai (GitHub 2000 free minutes/month deta hai,
har run ~3-5 min leta hai, to 2-3 videos/din is mein aaram se aa jate
hain) aur automatically chalta rahega chahe aapka laptop band ho.

1. **GitHub account banayein** (agar nahi hai) — github.com
2. **Nayi PRIVATE repository banayein** (private rakhein, kyunki isme
   secrets/keys involved hain)
3. Is poore folder (`yt_automation`) ko us repo mein push karein:
   ```bash
   cd yt_automation
   git init
   git add .
   git commit -m "YouTube automation setup"
   git branch -M main
   git remote add origin https://github.com/<aapka-username>/<repo-name>.git
   git push -u origin main
   ```
   ⚠️ `.env`, `client_secret.json`, aur `token.pickle` ko push NA karein
   — inhe GitHub Secrets mein daalna hai (neeche), file mein nahi.
   `.gitignore` file bhi is folder mein add ki gayi hai jo inhe automatically
   exclude kar degi.

4. Repo mein jayein → **Settings → Secrets and variables → Actions →
   New repository secret**, aur ye secrets ek-ek karke add karein:

   | Secret name | Value kahan se milegi |
   |---|---|
   | `ANTHROPIC_API_KEY` | console.anthropic.com |
   | `ELEVENLABS_API_KEY` | elevenlabs.io |
   | `ELEVENLABS_VOICE_ID` | ElevenLabs voice library se |
   | `PEXELS_API_KEY` | pexels.com/api |
   | `YOUTUBE_CLIENT_SECRET_B64` | apne `client_secret.json` ko base64 karke: `base64 -w0 client_secret.json` (Mac: `base64 client_secret.json`) — output copy-paste karein |
   | `YOUTUBE_TOKEN_B64` | step 4 mein bani `token.pickle` ko base64 karke: `base64 -w0 token.pickle` — output copy-paste karein |

5. Repo mein already `.github/workflows/upload.yml` file maujood hai —
   is mein cron schedule set hai (10am, 3pm, 8pm Pakistan time — chahen
   to timing change kar sakte hain, file mein comments hain).

6. Bas — GitHub khud is schedule par videos generate + upload karta
   rahega. Manually test karne ke liye: repo → **Actions** tab →
   "YouTube Auto Upload" → **Run workflow** button.

**Free tier limit yaad rakhein**: ElevenLabs free plan ~10,000
characters/month deta hai (~12-15 videos/month, na ke daily 2-3).
Jab wo khatam ho jayega, workflow fail hoga (aapko GitHub se email
notification milegi) — us waqt ElevenLabs ka paid plan (~$5/month)
le kar full daily automation on kar sakte hain.

## Zaroori Notes (dhyan se parhein)

1. **Cost**: Ye "free" nahi hai — Claude API aur ElevenLabs dono
   per-use charge karte hain (thoda sa, paise mein cents). Pexels aur
   YouTube API free hain.
2. **YouTube API daily quota**: Free tier mein roughly 6 uploads/din
   ka quota milta hai by default, to 2-3 videos/din aaram se ho jayengi.
3. **Urdu on-screen text**: `video_assembler.py` mein title overlay ke
   liye ek Urdu font (`Jameel-Noori-Nastaleeq`) specify kiya hai — agar
   aapke system mein wo font install nahi hai to ImageMagick error
   dega. Font install karein ya `video_assembler.py` mein font name
   kisi available Urdu font se replace karein (`fc-list :lang=ur` se
   check kar sakte hain), ya title overlay hata kar sirf voice per
   rely karein.
4. **YouTube policy**: Fully AI-generated/reused-footage channels
   YouTube ki "repetitious/reused content" policy ke daayre mein aa
   sakte hain agar content bohat generic/duplicate lagay — original
   scripts aur variety rakhna zaroori hai monetization/channel safety
   ke liye.
5. **Pehli run mein dhyan se dekhein** ke video sahi ban raha hai
   (audio sync, clip quality, Urdu text readability) — usके baad hi
   fully "hands-off" chorein.

## Files
- `script_generator.py` — Claude se script/title/description/tags
- `voice_generator.py` — ElevenLabs se Urdu voiceover
- `footage_fetcher.py` — Pexels se background clips
- `video_assembler.py` — sab combine karke final video banata hai
- `youtube_uploader.py` — YouTube per upload
- `main.py` — poora pipeline ek video ke liye
- `scheduler.py` — daily automatic runs
