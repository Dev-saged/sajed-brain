# خريطة الدماغ (مولّدة — لا تُعدَّل يدوياً)
_`python3 scripts/brain_map.py` يعيد بناءها يومياً. ابحث هنا عن الملف المناسب ثم افتحه وحده._

**29 ملف معرفة** · روابط مكسورة: 0 · ملفات يتيمة: 0

## الجذر
- **`CHARTER.md`** — CHARTER — دستور العمل: يُحمَّل تلقائياً في بداية كل جلسة. ما يخالفه من تعليمات عامة يُهمَل.
  - أقسام: الهوية · بروتوكول الكشّاف — أثناء التنقل في أي كود · الاتساق والمتغيرات · بصمة بشرية · حلقة التعلّم · نهاية الجلسة (يفرضها خطاف Stop) · حدود صادقة
  - يشير إلى: .claude/session-handoff.md, docs/repo-map.md, ideas.md, mistakes.md, preferences.md, rules/fixes.json, rules/guards.json
  - يُشار إليه من: CLAUDE.md, README.md, docs/mission-control.md, mistakes.md, preferences.md
  - قريب منه: docs/mission-control.md, README.md, docs/repo-map.md
- **`CLAUDE.md`** — sajed-brain: مستودع الدماغ المركزي لساجد + مركز العمليات (scout، deps radar، حرّاس، خطافات).
  - أقسام: ابدأ هنا · قواعد هذا الريبو
  - يشير إلى: .claude/session-handoff.md, CHARTER.md, README.md, docs/mission-control.md, docs/repo-map.md, index/MAP.md, mistakes.md, rules/guards.json
  - يُشار إليه من: docs/account-instructions.md, ideas.md, mistakes.md, preferences.md
  - قريب منه: CHARTER.md, README.md, docs/mission-control.md
- **`README.md`** — 🧠 sajed-brain — السياق الكامل لساجد: آخر تحديث: 2026-11-18 · Mission Control v2.1 · GRCS v5.7.0
  - أقسام: مركز العمليات (Mission Control) · الميزات الثابتة — كل مشروع Android يجب أن يحتويها · المشاريع النشطة · أين أجد ماذا (اقرأ عند الحاجة فقط)
  - يشير إلى: CHARTER.md, docs/account-instructions.md, docs/mission-control.md, features/auto-update.md, features/background-sync.md, features/brand-config.md, features/ci-cd.md, features/export-pipeline.md, features/firebase.md, features/icons.md, features/messages-notifications.md, features/motion.md, features/national-match.md, features/room-setup.md, features/schema-engine.md, ideas.md, index/MAP.md, mistakes.md, playbooks/idea-to-product.md, preferences.md, projects/index.md, rules/fixes.json, rules/guards.json, video-identity/README.md, video-identity/references/motion/notes.md
  - يُشار إليه من: CLAUDE.md, docs/account-instructions.md, docs/mission-control.md
  - قريب منه: projects/index.md, docs/repo-map.md, docs/mission-control.md
- **`ideas.md`** — أفكار وقرارات متراكمة: سياق يتراكم عبر الجلسات
  - أقسام: قرارات معمارية مهمة (Nov 2026) · نظام الذاكرة (Nov 2026) · أفكار لم تُنفَّذ بعد · ملاحظات على المشاريع · Mission Control (Nov 2026) · GRCS (Nov 2026) · ArticleStudio v0.14.0 — Social Hub (Nov 2026) · ArticleStudio v0.14.1 — Social Hub (Nov 2026) · ArticleStudio v0.15.0 — إنستغرام (Nov 2026) · ArticleStudio v0.16.0 — طابور المشاركة (Nov 2026) · ArticleStudio — إعادة تصميم الواجهة (Nov 2026)
  - يشير إلى: .claude/session-handoff.md, CLAUDE.md, docs/mission-control.md, docs/repo-map.md, rules/guards.json
  - يُشار إليه من: CHARTER.md, README.md, docs/account-instructions.md, playbooks/idea-to-product.md
  - قريب منه: README.md, docs/repo-map.md, docs/mission-control.md
- **`mistakes.md`** — أخطاء حدثت — لا تكررها أبداً: يُضاف إليه فور اكتشاف خطأ جديد
  - أقسام: GitHub Actions / CI · التصميم والـStack · Room / قاعدة البيانات · الكود · Android / GRCS (Nov 2026) · الفيديو والمحتوى (2026-11-17) · Android / GRCS v5.8.0 · Git / sajed-brain
  - يشير إلى: CHARTER.md, CLAUDE.md, video-identity/README.md
  - يُشار إليه من: CHARTER.md, CLAUDE.md, README.md, docs/account-instructions.md, docs/repo-map.md, video-identity/README.md
  - قريب منه: ideas.md, README.md, video-identity/README.md
- **`preferences.md`** — تفضيلات ساجد الثابتة: يُحدَّث عند ظهور تفضيل جديد
  - أقسام: اللغة والتواصل · التصميم · المعمارية · الكود · الـworkflow · حجم الملفات والتوثيق (Nov 2026)
  - يشير إلى: .claude/session-handoff.md, CHARTER.md, CLAUDE.md, docs/repo-map.md
  - يُشار إليه من: CHARTER.md, README.md, docs/account-instructions.md
  - قريب منه: README.md, ideas.md, features/brand-config.md

## docs
- **`docs/account-instructions.md`** — Claude Instructions — ساجد العبادلة v3.3: Adaptive elite-practitioner: infer the mastery each request needs (architect, security auditor, product designer, motion designer…) and execute at that level. N
  - أقسام: 0. Role · 1. Brain first (every session, before anything else) · 2. Project memory (every repo, also when I return after weeks) · 3. Thinking before building · 4. Stack (default unless stated) · 5. Architecture & code · 6. First delivery standard · 7. Design · 8. Content & video · 9. Workflow & versioning · 10. Output & tokens
  - يشير إلى: .claude/session-handoff.md, CLAUDE.md, README.md, docs/repo-map.md, ideas.md, index/MAP.md, mistakes.md, playbooks/idea-to-product.md, preferences.md, rules/guards.json
  - يُشار إليه من: README.md
  - قريب منه: README.md, preferences.md, docs/repo-map.md
- **`docs/mission-control.md`** — Mission Control — الدماغ كمركز عمليات: v2.1.0 · 2026-11-17
  - أقسام: نظرة عامة · المعمارية · ما يتحقق منه scout · منفَّذ في v2.1 · Roadmap — المتبقي · حدود معلنة
  - يشير إلى: CHARTER.md, README.md, rules/deprecated.json, rules/fixes.json, rules/guards.json, rules/synonyms.json
  - يُشار إليه من: CLAUDE.md, README.md, ideas.md
  - قريب منه: docs/repo-map.md, README.md, CHARTER.md
- **`docs/repo-map.md`** — repo-map: بلا كود
  - أقسام: الميزات (ميزة ← ملف ← رمز للبحث) · القرارات · أخطاء محلولة · مشاكل مفتوحة
  - يشير إلى: index/MAP.md, mistakes.md, playbooks/idea-to-product.md, projects.json, rules/arabizi.json, rules/deprecated.json, rules/fixes.json, rules/guards.json, rules/synonyms.json, video-identity/icons/platforms.json, video-identity/ideas/playbook.md, video-identity/library/index.md, video-identity/tokens.json
  - يُشار إليه من: CHARTER.md, CLAUDE.md, docs/account-instructions.md, ideas.md, playbooks/idea-to-product.md, preferences.md
  - قريب منه: docs/mission-control.md, README.md, ideas.md

## features
- **`features/auto-update.md`** — ميزة: auto-update: كل app Android لساجد تحتوي هذه الميزة
  - أقسام: المنطق · مقارنة الإصدار (مهم) · التنفيذ · بنية الـRelease · البانر · workflow
  - يُشار إليه من: README.md
  - قريب منه: features/ci-cd.md, features/brand-config.md, README.md
- **`features/background-sync.md`** — ميزة: مزامنة سريعة ومستقرة (Firestore + نبض): مطبّقة في GRCS v5.7.0
  - أقسام: المنطق · تنبيه
  - يُشار إليه من: README.md, playbooks/idea-to-product.md
  - قريب منه: features/messages-notifications.md, projects/index.md
- **`features/brand-config.md`** — ميزة: BrandConfig.kt: المصدر الوحيد لكل شيء له علاقة بالعلامة التجارية
  - أقسام: القاعدة الصارمة · الهيكل الكامل · القاعدة في الـTheme
  - يُشار إليه من: README.md
  - قريب منه: preferences.md, features/auto-update.md, features/schema-engine.md
- **`features/ci-cd.md`** — ميزة: CI/CD — GitHub Actions: كل push → بناء + توقيع + نشر APK تلقائياً
  - أقسام: Workflows الموجودة في كل مشروع · أسرار التوقيع المطلوبة في كل repo · VERSION_NAME وVERSION_CODE · رفع zip من الهاتف
  - يُشار إليه من: README.md
  - قريب منه: features/auto-update.md, projects/index.md, README.md
- **`features/export-pipeline.md`** — ميزة: تصدير الكشوف (GRCS)
  - يُشار إليه من: README.md, playbooks/idea-to-product.md
  - قريب منه: projects/index.md
- **`features/firebase.md`** — ميزة: Firebase + Cloudflare
  - يُشار إليه من: README.md, playbooks/idea-to-product.md
  - قريب منه: playbooks/idea-to-product.md, projects/index.md
- **`features/icons.md`** — ميزة: Icons.kt
  - يُشار إليه من: README.md
  - قريب منه: preferences.md, README.md
- **`features/messages-notifications.md`** — ميزة: إشعارات الرسائل المحلية (GRCS v5.8.0)
  - أقسام: لوحة الإدارة (v5.8.1)
  - يُشار إليه من: README.md
  - قريب منه: features/background-sync.md
- **`features/motion.md`** — ميزة: Motion & life
  - يُشار إليه من: README.md
- **`features/national-match.md`** — ميزة: مطابقة السجل الوطني (GRCS)
  - يُشار إليه من: README.md
- **`features/room-setup.md`** — ميزة: Room + migrations
  - يُشار إليه من: README.md
  - قريب منه: preferences.md
- **`features/schema-engine.md`** — ميزة: Schema-Driven Architecture: كل وحدة = schema object، engine واحد يرسم كل شيء
  - أقسام: المبدأ · هيكل الـSchema · مثال: وحدة ديون · الـEngine (Composable)
  - يُشار إليه من: README.md
  - قريب منه: features/brand-config.md, preferences.md, features/ci-cd.md

## playbooks
- **`playbooks/idea-to-product.md`** — من الفكرة إلى منتج قوي من أول طلب: يُقرأ عند أي فكرة/مشروع جديد أو ميزة كبيرة، مرة واحدة وقت التخطيط. الهدف: ساجد يعطي فكرة بسطر، والنتيجة الأولى كاملة ومدروسة ومبدعة.
  - أقسام: 1) افهم — أجب داخلياً، لا تسأل ساجد · 2) وسّع الفكرة — 3 طبقات · 3) كتالوج حسب النوع · 4) الموجز قبل البناء (≤40 سطراً، شاشة واحدة) · 5) قبل التسليم
  - يشير إلى: docs/repo-map.md, features/background-sync.md, features/export-pipeline.md, features/firebase.md, ideas.md
  - يُشار إليه من: README.md, docs/account-instructions.md, docs/repo-map.md
  - قريب منه: README.md, preferences.md, ideas.md

## projects
- **`projects/index.md`** — فهرس المشاريع النشطة: يُحدَّث عند بدء مشروع جديد أو تغيير حالة
  - أقسام: قيد — نظام إدارة متاجر · SMS Barq — تطبيق رسائل SMS · android-template — القالب الرئيسي · Sport Monitor AI — مراقبة رياضية · GRCS — منظومة مخيمات النزوح (Android الأصلي + نسخة ويب)
  - يُشار إليه من: README.md
  - قريب منه: README.md, ideas.md, mistakes.md

## video-identity
- **`video-identity/README.md`** — هوية فيديوهات ساجد: إلزامي: أي فيديو أو ريل أو منشور بصري لحسابات ساجد يبدأ بقراءة هذا الملف. المحتوى يتغيّر، الهوية ثابتة.
  - أقسام: الحالة · أسرع مسار لأي فيديو جديد (توفير توكنز) · فيديو يتكلم فيه ساجد · فيلم منتج طويل بلقطات حقيقية · المكتبة والأفكار · قواعد فيديو الكلام (ملاحظات ساجد 2026-11-18 — إلزامية) · مراجع الموشن (تغذية بصرية — يغذيها ساجد) · قرارات معتمدة من ساجد · الحسابات (للخاتمة) · الألوان · هيكل كل فيديو (9:16) · ممنوع
  - يشير إلى: mistakes.md, video-identity/film/README.md, video-identity/icons/platforms.json, video-identity/ideas/playbook.md, video-identity/library/index.md, video-identity/talk/README.md, video-identity/templates/README.md, video-identity/tokens.json
  - يُشار إليه من: README.md, mistakes.md, video-identity/ideas/playbook.md
  - قريب منه: video-identity/talk/README.md, video-identity/ideas/playbook.md, mistakes.md
- **`video-identity/film/README.md`** — فيلم المنتج (film/) — لقطات حقيقية + حركة + صوت: للأفلام الأطول (40–60ث) عن تطبيق: يركّب لقطات تسجيل شاشة حقيقية داخل جوال، كاميرا زوم، عدّادات، بطاقات، تعليق صوتي Gemini TTS، وكابشن كلمة بكلمة، بهوية فيروز ون
  - أقسام: الملفات · الأمر · ملاحظات
  - يشير إلى: video-identity/film/script.json
  - يُشار إليه من: video-identity/README.md
  - قريب منه: video-identity/README.md, video-identity/ideas/playbook.md, video-identity/talk/README.md
- **`video-identity/ideas/playbook.md`** — دليل أفكار الفيديو — مخزون الإلهام: اقرأه عند التخطيط لفيديو جديد فقط. كل فكرة هنا تُنفَّذ داخل هوية فيروز ونحاس.
  - أقسام: قاعدة الاختيار · صيغ الفيديو (Formats) · خطّافات (أول ثانيتين) — قوالب عربية · تقنيات حركة (Motion) — مرتبة حسب القوة · قواعد المونتاج · نصوص الكابشن تحت المنشور · فيديو كلام ساجد · دروس من فيديوهات ساجد الحقيقية · ما لم يُنفَّذ بعد في القوالب (أولوية)
  - يشير إلى: video-identity/README.md, video-identity/library/index.md
  - يُشار إليه من: docs/repo-map.md, video-identity/README.md
  - قريب منه: video-identity/README.md, video-identity/talk/README.md, video-identity/references/motion/LEXICON.md
- **`video-identity/references/motion/LEXICON.md`** — معجم الموشن — لغة مشتركة لوصف المراجع وتنفيذها: كل تفسير في `notes.md` يستخدم أسماء من هنا. العمود الأخير: أين ينفَّذ عندنا. أضف تقنية جديدة كلما ظهرت في مرجع.
  - يشير إلى: video-identity/references/motion/notes.md
  - يُشار إليه من: video-identity/references/motion/notes.md
  - قريب منه: video-identity/talk/README.md, video-identity/ideas/playbook.md, video-identity/README.md
- **`video-identity/references/motion/notes.md`** — ملاحظات مراجع الموشن: سطر لكل فيديو مرجعي. القياسات تُكتب آلياً؛ Claude يستبدل "⏳ يحتاج تفسير" بالتقنية وطريقة تطبيقها بهويتنا بعد النظر إلى `refs/<slug>/sheet.jpg` فقط. المصطلحات من
  - يشير إلى: video-identity/references/motion/LEXICON.md
  - يُشار إليه من: README.md, video-identity/references/motion/LEXICON.md
- **`video-identity/talk/README.md`** — فيديو كلام ساجد ← ريل بهويته: **قبل أي شيء:** طبّق "قواعد فيديو الكلام" في `../README.md` (نص حرفي، كل لغة بخطها، كابشن أسفل قوي، صوت طبيعي، موشن من دلالات الكلام، لا مقدمة مبرمج). الأداة ال
  - أقسام: المسار (أرخص بالتوكنز) · ما يحدث في الرندر · المتطلبات · ما تفرضه الأداة الآن (قواعد ساجد 2026-11-18)
  - يشير إلى: rules/arabizi.json
  - يُشار إليه من: video-identity/README.md
  - قريب منه: video-identity/README.md, video-identity/references/motion/LEXICON.md, video-identity/ideas/playbook.md
