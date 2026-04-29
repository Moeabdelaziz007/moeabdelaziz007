# Architecture Guide & System Design

## 1. AIX Philosophy (Artificial Intelligence eXchange)
The AIX-Format is designed to be the foundational standard for AI Agent deployment and inter-agent communication.
The philosophy is rooted in extreme efficiency, strict typed schemas, and zero-trust verification.

- **Determinism over Magic:** Every payload must be predictable and verifiable.
- **Portability:** Agents should be easily serialized into YAML/JSON/TOML formats, allowing deployment across any compute environment.
- **M2M Economics:** Built-in cryptographic signatures (Ed25519/secp256k1) ensure that Machine-to-Machine transactions are secure, sybil-resistant, and economically viable without human intervention.

## 2. System Design: The Profile Infrastructure
This profile repository is treated not as a standard text document, but as a live, self-updating infrastructure piece.

### Telemetry Subsystem
- **Core Script:** `scripts/generate_aix_dashboard.py` serves as the engine. It fetches (or simulates) real-time data such as Uptime and AIX Execution counts.
- **Data Rendering:** The script generates two artifacts:
  1. A minimal, Vercel-style SVG dashboard (`assets/aix_dashboard.svg`) using monochrome aesthetics.
  2. A clean Markdown table representing structured telemetry data.
- **Injection:** These artifacts are injected directly into `README.md` between predefined `<!-- START_LIVE_DATA -->` and `<!-- END_LIVE_DATA -->` tags.

## 3. Hidden Design Patterns
- **Monochrome Brutalism:** Visuals are stripped of noise (no glowing shadows or neon). We rely on 1px borders, `#000000` backgrounds, and `#ffffff` / `#888888` text. This reflects a production-grade infrastructure mindset.
- **Detached Manifests (AxiomID):** AIX configurations rely on detached identity structures, allowing agents to rotate capabilities without changing their core identity hash.
- **Dual-Language Symmetry:** English and Arabic content are semantically linked but structurally separated using proper `dir="rtl"` attributes for native readability.

## 4. Scaling Strategy
As the ecosystem grows, this infrastructure can be scaled:
- **Live APIs:** The Python script can be updated to fetch actual telemetry from a deployed AIX network (via REST/GraphQL) instead of mocked POC data.
- **Event-Driven Updates:** Instead of just a 6-hour CRON job, GitHub repository dispatch events can trigger dashboard updates immediately upon a new AIX agent deployment.

---

<div dir="rtl" align="right">

## دليل التثبيت والدمج (Integration & Setup Guide)

تم تصميم هذا المستودع ليعمل بشكل آلي تماماً باستخدام `GitHub Actions`.

### موقع الملفات
1. **السكربت البرمجي:** يوجد في `scripts/generate_aix_dashboard.py`. يجب أن يبقى هنا للحفاظ على هيكلية المستودع النظيفة.
2. **ملف سير العمل (Workflow):** يجب وضعه في المسار `.github/workflows/telemetry_update.yml`. هذا الملف هو المسؤول عن تشغيل السكربت كل 6 ساعات.

### كيف يعمل الدمج (Integration)؟
- عندما يعمل الـ GitHub Action، يقوم بتهيئة بيئة Python.
- يقوم بتشغيل السكربت `generate_aix_dashboard.py`.
- يبحث السكربت داخل `README.md` عن علامتي:
  `<!-- START_LIVE_DATA -->`
  و
  `<!-- END_LIVE_DATA -->`
- يقوم السكربت باستبدال ما بين هاتين العلامتين بالجدول النصي (Markdown Table) والصورة التوليدية (`aix_dashboard.svg`).
- أخيرًا، يقوم الـ Action بعمل `git commit` و `git push` تلقائياً باستخدام صلاحيات الـ `GITHUB_TOKEN`.

### حيل وأفكار متقدمة (Smart Tricks & Pro Hacks)
- **بيانات حقيقية (Live Data):** يمكنك لاحقاً ربط السكربت بـ APIs حقيقية (مثل WakaTime أو سيرفراتك الخاصة) لعرض إحصائيات فعلية بدلاً من الأرقام الوهمية.
- **لوحات متعددة (Multi-Dashboards):** يمكنك إنشاء ملفات SVG متعددة (مثل `assets/network_load.svg` و `assets/agent_status.svg`) وعرضها بجانب بعضها لتبدو كشاشات مراقبة حقيقية.
- **استخدام Cache:** في حال كنت تجلب بيانات من API خارجي يأخذ وقتاً، يمكنك استخدام GitHub Actions Cache لتخزين الاستجابة مؤقتاً لتسريع عملية البناء.
</div>

## 5. Transition to Product Landing Page
The profile serves as a product landing page focusing primarily on the AIX protocol.
- **Hero Section:** Retains a controlled "cyber identity" aesthetic to establish brand identity.
- **Visual Noise Reduction:** Achieved by minimizing unnecessary badges, shadows, and relying on F-pattern typography logic.
