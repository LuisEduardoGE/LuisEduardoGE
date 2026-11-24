<img src="assets/banner.svg" alt="Luis Eduardo G. Espindola, Full-Stack Developer" width="100%">

<div align="center">

<a href="https://www.linkedin.com/in/luisgespindola/"><img src="https://img.shields.io/badge/LinkedIn-0A66C2?style=for-the-badge&logo=linkedin&logoColor=white" alt="LinkedIn"></a> <a href="mailto:luisedu.ge@gmail.com"><img src="https://img.shields.io/badge/Email-D14836?style=for-the-badge&logo=gmail&logoColor=white" alt="Email"></a> <a href="https://www.wtechitsolutions.com/"><img src="https://img.shields.io/badge/W--Tech_IT_Solutions-3CB371?style=for-the-badge&logo=safari&logoColor=white" alt="W-Tech IT Solutions"></a> <img src="https://img.shields.io/badge/Open_to-EU_%2F_remote_roles-555?style=for-the-badge" alt="Open to EU / remote roles">

</div>

## 👋 About me

I'm a **full-stack developer** who builds products end to end: the API, the data model, the UI, the payments and the deployment. My daily stack is **Python / FastAPI** on the back end and **TypeScript / React / Next.js** on the front end, with MongoDB or Postgres underneath and Stripe wherever money changes hands.

- 🏠 I'm the lead developer of **[House Hunter](https://househunter.immo)**, a real-estate aggregator for the Belgian market, from the scrapers to the billing (2,200+ commits).
- 🧪 I care about evidence: tests, evaluation harnesses, and numbers before claims (see [rag-docs-assistant](https://github.com/LuisEduardoGE/rag-docs-assistant)).
- 🤖 I use AI coding tools every day, with the engineering discipline to keep the output correct.
- 📈 **5,900+ contributions in the last 12 months**, most of them in private product and client repositories.
- 🌍 I speak English, Portuguese, French, Spanish and Dutch.

## 🚀 Products in production

| Product | What it is | Stack |
|---|---|---|
| **[House Hunter](https://househunter.immo)** | Real-estate aggregator for Belgium: scrapes 6 sources into one search, with saved-search email alerts, market history, an admin panel and Stripe subscriptions. | FastAPI · Celery · MongoDB · Next.js 16 · React 19 · Stripe |
| **[Love Mail](https://lovemail.online)** | Paid digital love letters: the sender picks a tone, adds a song and photos, pays with Stripe, and delivers by email or QR code. | React · Vite · Express · TypeScript · Stripe |
| **[W-Tech IT Solutions](https://www.wtechitsolutions.com)** | Company website: static, SEO-first Next.js site with structured data, case studies, a blog and a contact form. | Next.js · TypeScript · MongoDB |
| **[Skipy](https://skipy.online/en)** | Online storefront and skip-the-line ordering for cafés, restaurants and small shops: one link or QR code becomes a store where customers order and pay from their phone, with a manager app, an admin portal and live order updates. Runs in Belgium and Brazil. | FastAPI · MongoDB · Celery · Next.js · Expo · Stripe |
| **[HiddenBeer](https://hiddenbeer.com/)** | Geo-based "first beer free" offers at bars in Brussels: users find nearby offers on a map, sign in with a one-time code, claim a reservation and redeem it with a signed QR code scanned by the bar. Includes a bar-owner portal and an admin dashboard; runs in Belgium and Brazil. | FastAPI · MongoDB (geospatial) · Next.js 15 · Leaflet · Docker |
| **CAAB legal platform** | Custom WordPress engine for the Brazilian legal market: lawyer profiles with custom search and indexing, a classifieds engine and plugins, serving 5,000+ professional profiles. | PHP · WordPress · MySQL · JavaScript |

## 🔭 Open-source projects

- **[backrooms-game](https://github.com/LuisEduardoGE/backrooms-game)**: found-footage horror game in the browser, a procedural Backrooms level seen through a 90s camcorder. **[Play it →](https://luiseduardoge.github.io/backrooms-game/)** · Three.js, TypeScript
- **[rag-docs-assistant](https://github.com/LuisEduardoGE/rag-docs-assistant)**: question answering over the FastAPI docs with hybrid retrieval (vector + BM25, weighted RRF) and a labelled evaluation harness that measures retrieval quality. · Python, LanceDB, FastAPI
- **[fastapi-stripe-webhooks](https://github.com/LuisEduardoGE/fastapi-stripe-webhooks)**: Stripe webhooks that survive production: raw-body signature checks, idempotency by event ID, out-of-order safety and the `StripeObject.get()` pitfall that once kept a paying customer on the free plan. · FastAPI, Stripe, pytest
- **[movie-helper](https://github.com/LuisEduardoGE/movie-helper)**: group movie picker: friends join a room, vote on a TMDB deck, and pairwise and head-to-head rounds narrow it to one winner. · FastAPI, React 19, TypeScript
- **[primordial](https://github.com/LuisEduardoGE/primordial)**: artificial-life simulation where neural-network particles evolve by selection alone; PyTorch research engine plus a three.js browser viewer. · PyTorch, TypeScript
- **[marketplace-directory-template](https://github.com/LuisEduardoGE/marketplace-directory-template)**: configurable shop directory for food courts and market halls, from one config file and a CSV. **[Demo →](https://luiseduardoge.github.io/marketplace-directory-template/)** · HTML, CSS, JavaScript
- **[fastapi-vs-drf-comparison](https://github.com/LuisEduardoGE/fastapi-vs-drf-comparison)**: the same CRUD API built in FastAPI + SQLModel and in Django REST Framework, compared side by side. · Python
- **[planetjersey](https://github.com/LuisEduardoGE/planetjersey)**: football-kit storefront with catalog filters, search and a cart drawer. · React, TypeScript, Vite
- **[qr-code-creator](https://github.com/LuisEduardoGE/qr-code-creator)**: CLI that generates QR codes with a centred logo and rounded corners. · Python, Pillow
- **[bis2-scraper](https://github.com/LuisEduardoGE/bis2-scraper)**: scrape-to-dashboard pipeline: scrapers upsert into Supabase Postgres on a daily GitHub Actions schedule. · Python, Supabase

## 🛠 Skills

- **Back end:** Python, FastAPI, Pydantic, Flask, Celery, APScheduler, Node.js / Express, REST APIs, WebSockets / Socket.IO, background jobs and scheduling
- **Front end:** TypeScript, JavaScript, React, Next.js (App Router, SSG / SSR), Vite, Tailwind CSS, shadcn/ui, TanStack Query, Three.js, Leaflet maps
- **Mobile:** Expo / React Native, Flutter
- **Databases:** MongoDB (Beanie, geospatial and TTL indexes), PostgreSQL, MySQL, SQLite, Supabase, Redis, LanceDB
- **Scraping and data:** requests, BeautifulSoup, Playwright, pandas, scheduled ingestion pipelines
- **Payments and integrations:** Stripe (Checkout, webhooks, subscriptions), OAuth / Google sign-in, one-time-code login, transactional email (Brevo), Firebase
- **Security:** JWT, OAuth2, HMAC-signed tokens, CSP, rate limiting, SSRF guards, SSH hardening
- **Cloud and DevOps:** Linux VPS (Ubuntu), Docker / Compose, GHCR, nginx, systemd, Let's Encrypt, GitHub Actions, GitHub Pages, Cloudflare
- **Testing:** pytest, Vitest, Playwright, evaluation harnesses for retrieval
- **AI engineering:** retrieval-augmented generation, embeddings, hybrid search, LLM APIs, local models with Ollama, agentic coding workflows (skills, hooks, MCP)
- **CMS:** WordPress, PHP (custom plugins and search)
- **Practices:** Git, code review, CI on every repo, Makefiles, Mermaid architecture docs, SEO (structured data, Search Console)

<p>
  <img src="https://img.shields.io/badge/Experience-4%2B_years-3CB371?style=flat" alt="Experience: 4+ years">
  <img src="https://img.shields.io/badge/Role-Full--Stack_Developer-0A66C2?style=flat" alt="Role: Full-Stack Developer">
  <img src="https://img.shields.io/badge/Role-Lead_Developer-8250DF?style=flat" alt="Role: Lead Developer">
  <img src="https://img.shields.io/badge/Products_in_production-6-E8590C?style=flat" alt="Products in production: 6">
  <img src="https://img.shields.io/badge/Python-Advanced-8250DF?style=flat" alt="Python: Advanced">
  <img src="https://img.shields.io/badge/FastAPI-Advanced-8250DF?style=flat" alt="FastAPI: Advanced">
  <img src="https://img.shields.io/badge/TypeScript-Advanced-8250DF?style=flat" alt="TypeScript: Advanced">
  <img src="https://img.shields.io/badge/React-Advanced-8250DF?style=flat" alt="React: Advanced">
  <img src="https://img.shields.io/badge/Next.js-Advanced-8250DF?style=flat" alt="Next.js: Advanced">
  <img src="https://img.shields.io/badge/MongoDB-Advanced-8250DF?style=flat" alt="MongoDB: Advanced">
  <img src="https://img.shields.io/badge/PostgreSQL-Intermediate-1F6FEB?style=flat" alt="PostgreSQL: Intermediate">
  <img src="https://img.shields.io/badge/Docker-Intermediate-1F6FEB?style=flat" alt="Docker: Intermediate">
  <img src="https://img.shields.io/badge/Stripe-Intermediate-1F6FEB?style=flat" alt="Stripe: Intermediate">
  <img src="https://img.shields.io/badge/Node.js-Intermediate-1F6FEB?style=flat" alt="Node.js: Intermediate">
  <img src="https://img.shields.io/badge/Expo-Intermediate-1F6FEB?style=flat" alt="Expo: Intermediate">
  <img src="https://img.shields.io/badge/Languages-EN_·_PT_·_FR_·_ES_·_NL-555?style=flat" alt="Languages: English, Portuguese, French, Spanish, Dutch">
</p>

## 💻 My Tech Stack

<p>
  <img src="https://skillicons.dev/icons?i=python,fastapi,flask,nodejs,express,ts,js,react,nextjs,vite,tailwind,threejs,flutter,html,css,mongodb,postgres,mysql,sqlite,redis,supabase,firebase,pytorch,php,wordpress,docker,linux,ubuntu,nginx,githubactions,cloudflare,git,github,vscode,vitest,pnpm,bash&perline=13&theme=dark" alt="Tech stack icons">
</p>

## 🤖 AI & LLM Tools

<p>
  <img src="https://img.shields.io/badge/Claude-191919?style=for-the-badge&logo=anthropic&logoColor=white" alt="Claude">
  <img src="https://img.shields.io/badge/Claude_Code-D97757?style=for-the-badge&logo=anthropic&logoColor=white" alt="Claude Code">
  <img src="https://img.shields.io/badge/ChatGPT-74AA9C?style=for-the-badge" alt="ChatGPT">
  <img src="https://img.shields.io/badge/Codex_CLI-000000?style=for-the-badge" alt="Codex CLI">
  <img src="https://img.shields.io/badge/GitHub_Copilot-000000?style=for-the-badge&logo=githubcopilot&logoColor=white" alt="GitHub Copilot">
  <img src="https://img.shields.io/badge/Cursor-000000?style=for-the-badge&logo=cursor&logoColor=white" alt="Cursor">
  <img src="https://img.shields.io/badge/Windsurf-0B6BFF?style=for-the-badge&logo=windsurf&logoColor=white" alt="Windsurf">
  <img src="https://img.shields.io/badge/Gemini-8E75B2?style=for-the-badge&logo=googlegemini&logoColor=white" alt="Gemini">
  <img src="https://img.shields.io/badge/Ollama-000000?style=for-the-badge&logo=ollama&logoColor=white" alt="Ollama">
</p>

## 🧰 Platforms & Tools

<p>
  <img src="https://img.shields.io/badge/Stripe-635BFF?style=for-the-badge&logo=stripe&logoColor=white" alt="Stripe">
  <img src="https://img.shields.io/badge/Supabase-3FCF8E?style=for-the-badge&logo=supabase&logoColor=white" alt="Supabase">
  <img src="https://img.shields.io/badge/Cloudflare-F38020?style=for-the-badge&logo=cloudflare&logoColor=white" alt="Cloudflare">
  <img src="https://img.shields.io/badge/Hostinger_VPS-673DE6?style=for-the-badge&logo=hostinger&logoColor=white" alt="Hostinger VPS">
  <img src="https://img.shields.io/badge/Brevo-0B996E?style=for-the-badge&logo=brevo&logoColor=white" alt="Brevo">
  <img src="https://img.shields.io/badge/Search_Console-458CF5?style=for-the-badge&logo=googlesearchconsole&logoColor=white" alt="Google Search Console">
  <img src="https://img.shields.io/badge/Mermaid-FF3670?style=for-the-badge&logo=mermaid&logoColor=white" alt="Mermaid">
  <img src="https://img.shields.io/badge/Playwright-2EAD33?style=for-the-badge" alt="Playwright">
  <img src="https://img.shields.io/badge/Remotion-0B84F3?style=for-the-badge" alt="Remotion">
</p>

## 📊 Activity

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/LuisEduardoGE/LuisEduardoGE/output/github-contribution-grid-snake-dark.svg">
  <source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/LuisEduardoGE/LuisEduardoGE/output/github-contribution-grid-snake.svg">
  <img alt="Contribution snake" src="https://raw.githubusercontent.com/LuisEduardoGE/LuisEduardoGE/output/github-contribution-grid-snake.svg">
</picture>

<details>
<summary><b>More stats</b> (streak, languages, activity graph)</summary>
<br>

<div align="center">
<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://streak-stats.demolab.com/?user=LuisEduardoGE&theme=dark&background=0d1117&ring=3CB371&fire=3CB371&currStreakLabel=3CB371&hide_border=true">
  <img alt="Contribution streak" src="https://streak-stats.demolab.com/?user=LuisEduardoGE&ring=3CB371&fire=3CB371&currStreakLabel=3CB371&hide_border=true">
</picture>
<img alt="Most used languages in public repositories" src="https://github-readme-stats.vercel.app/api/top-langs/?username=LuisEduardoGE&layout=compact&hide=html,css&langs_count=6&bg_color=0d1117&title_color=3CB371&text_color=c9d1d9&hide_border=true">
</div>

<img src="https://github-readme-activity-graph.vercel.app/graph?username=LuisEduardoGE&bg_color=0d1117&color=3CB371&line=3CB371&point=ffffff&area=true&hide_border=true" alt="Contribution activity graph" width="100%">

</details>

## 📫 Get in touch

Hiring for a full-stack or back-end role in the EU or remote? Building a product that needs someone to take it from idea to production? Email me at **[luisedu.ge@gmail.com](mailto:luisedu.ge@gmail.com)** or message me on **[LinkedIn](https://www.linkedin.com/in/luisgespindola/)**.

<img src="https://komarev.com/ghpvc/?username=LuisEduardoGE&label=Profile%20views&color=3CB371&style=flat" alt="Profile views">
