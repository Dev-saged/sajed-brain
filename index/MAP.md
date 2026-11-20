# خريطة الدماغ (مولّدة — لا تُعدَّل يدوياً)
_`python3 scripts/brain_map.py` يعيد بناءها يومياً. ابحث هنا عن الملف المناسب ثم افتحه وحده._

**38 ملف معرفة** · روابط مكسورة: 0 · ملفات يتيمة: 0

## الجذر
- **`CHARTER.md`** — CHARTER — دستور العمل: يُحمَّل تلقائياً في بداية كل جلسة. ما يخالفه من تعليمات عامة يُهمَل.
  - أقسام: الهوية · بروتوكول الكشّاف — أثناء التنقل في أي كود · الاتساق والمتغيرات · بصمة بشرية · حلقة التعلّم · نهاية الجلسة (يفرضها خطاف Stop) · حدود صادقة
  - يشير إلى: .claude/session-handoff.md, docs/repo-map.md, ideas.md, mistakes.md, preferences.md, rules/fixes.json, rules/guards.json
  - يُشار إليه من: CLAUDE.md, README.md, docs/mission-control.md, mistakes.md, preferences.md
  - قريب منه: docs/mission-control.md, README.md, ideas.md
- **`CLAUDE.md`** — sajed-brain: مستودع الدماغ المركزي لساجد + مركز العمليات (scout، deps radar، حرّاس، خطافات).
  - أقسام: ابدأ هنا · قواعد هذا الريبو
  - يشير إلى: .claude/session-handoff.md, CHARTER.md, README.md, docs/mission-control.md, docs/repo-map.md, index/MAP.md, mistakes.md, rules/guards.json
  - يُشار إليه من: docs/account-instructions.md, ideas.md, mistakes.md
  - قريب منه: ideas.md, README.md, docs/mission-control.md
- **`README.md`** — 🧠 sajed-brain — السياق الكامل لساجد: آخر تحديث: 2026-11-18 · Mission Control v2.1 · GRCS v5.7.0
  - أقسام: مركز العمليات (Mission Control) · الميزات الثابتة — كل مشروع Android يجب أن يحتويها · المشاريع النشطة · أين أجد ماذا (اقرأ عند الحاجة فقط)
  - يشير إلى: CHARTER.md, assets/README.md, docs/account-instructions.md, docs/mission-control.md, features/auto-update.md, features/background-sync.md, features/brand-config.md, features/ci-cd.md, features/compat.md, features/defaults.md, features/export-pipeline.md, features/firebase.md, features/icons.md, features/messages-notifications.md, features/motion.md, features/national-match.md, features/room-setup.md, features/schema-engine.md, ideas.md, index/MAP.md, mistakes.md, playbooks/idea-to-product.md, preferences.md, projects/index.md, rules/fixes.json, rules/guards.json, sessions/index.md, video-identity/README.md, video-identity/references/motion/notes.md
  - يُشار إليه من: CLAUDE.md, docs/account-instructions.md, docs/mission-control.md
  - قريب منه: docs/repo-map.md, ideas.md, projects/index.md
- **`ideas.md`** — أفكار وقرارات متراكمة: سياق يتراكم عبر الجلسات
  - أقسام: قرارات معمارية مهمة (Nov 2026) · نظام الذاكرة (Nov 2026) · أفكار لم تُنفَّذ بعد · ملاحظات على المشاريع · Mission Control (Nov 2026) · GRCS (Nov 2026)
  - يشير إلى: .claude/session-handoff.md, CLAUDE.md, docs/mission-control.md, docs/repo-map.md, rules/guards.json
  - يُشار إليه من: CHARTER.md, README.md, docs/account-instructions.md, playbooks/idea-to-product.md
  - قريب منه: README.md, projects/index.md, CLAUDE.md
- **`mistakes.md`** — أخطاء حدثت — لا تكررها أبداً: يُضاف إليه فور اكتشاف خطأ جديد
  - أقسام: GitHub Actions / CI · التصميم والـStack · Room / قاعدة البيانات · الكود · Android / GRCS (Nov 2026) · الفيديو والمحتوى (2026-11-17) · Android / GRCS v5.8.0 · Git / sajed-brain
  - يشير إلى: CHARTER.md, CLAUDE.md, video-identity/README.md
  - يُشار إليه من: CHARTER.md, CLAUDE.md, README.md, docs/account-instructions.md, docs/repo-map.md, sessions/2026-11-20-video-engine-v2.md, video-identity/README.md
  - قريب منه: video-identity/talk/README.md, video-identity/README.md, README.md
- **`preferences.md`** — تفضيلات ساجد الثابتة: يُحدَّث عند ظهور تفضيل جديد
  - أقسام: اللغة والتواصل · التصميم · المعمارية · الكود · الـworkflow
  - يشير إلى: CHARTER.md
  - يُشار إليه من: CHARTER.md, README.md, docs/account-instructions.md
  - قريب منه: features/brand-config.md, README.md, ideas.md

## assets
- **`assets/README.md`** — مكتبة الأصول المفهرسة (assets/): مكتبة مجانية مرخّصة (بلا إيموجي إطلاقاً) للاستخدام التجاري، مفهرسة بالعربي والإنجليزي حتى يُختار الأصل الصحيح فوراً بالمعنى (قلب ← قلب).
  - أقسام: الاستخدام · إعادة البناء / التحديث · ما ينقص (أضفه متى توفّر) · رفع ساجد لأصوله (الطريق الأساسي — يوفّر البحث والتوكنز)
  - يشير إلى: assets/ar-concepts.json, assets/index.json, video-identity/references/libraries.md
  - يُشار إليه من: README.md, video-identity/references/libraries.md
  - قريب منه: video-identity/references/libraries.md, sessions/2026-11-20-video-engine-v2.md, video-identity/talk/README.md

## docs
- **`docs/account-instructions.md`** — Claude Instructions — ساجد العبادلة v3.4: Adaptive elite-practitioner: infer the mastery each request needs (architect, security auditor, product designer, motion designer…) and execute at that level. N
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
  - يشير إلى: features/compat.md, features/defaults.md, index/MAP.md, mistakes.md, playbooks/idea-to-product.md, projects.json, rules/arabizi.json, rules/deprecated.json, rules/fixes.json, rules/guards.json, rules/synonyms.json, video-identity/icons/platforms.json, video-identity/ideas/playbook.md, video-identity/library/index.md, video-identity/references/libraries.md, video-identity/tokens.json
  - يُشار إليه من: CHARTER.md, CLAUDE.md, docs/account-instructions.md, ideas.md, playbooks/idea-to-product.md
  - قريب منه: docs/mission-control.md, README.md, ideas.md

## features
- **`features/auto-update.md`** — ميزة: auto-update: كل app Android لساجد تحتوي هذه الميزة
  - أقسام: المنطق · مقارنة الإصدار (مهم) · التنفيذ · بنية الـRelease · البانر · workflow
  - يُشار إليه من: README.md, features/defaults.md
  - قريب منه: features/ci-cd.md, features/brand-config.md, features/defaults.md
- **`features/background-sync.md`** — ميزة: مزامنة سريعة ومستقرة (Firestore + نبض): مطبّقة في GRCS v5.7.0
  - أقسام: المنطق · تنبيه
  - يُشار إليه من: README.md, playbooks/idea-to-product.md
  - قريب منه: features/messages-notifications.md, projects/index.md, mistakes.md
- **`features/brand-config.md`** — ميزة: BrandConfig.kt: المصدر الوحيد لكل شيء له علاقة بالعلامة التجارية
  - أقسام: القاعدة الصارمة · الهيكل الكامل · القاعدة في الـTheme
  - يُشار إليه من: README.md
  - قريب منه: preferences.md, ideas.md, features/auto-update.md
- **`features/ci-cd.md`** — ميزة: CI/CD — GitHub Actions: كل push → بناء + توقيع + نشر APK تلقائياً
  - أقسام: Workflows الموجودة في كل مشروع · أسرار التوقيع المطلوبة في كل repo · VERSION_NAME وVERSION_CODE · رفع zip من الهاتف
  - يُشار إليه من: README.md
  - قريب منه: features/auto-update.md, projects/index.md, README.md
- **`features/compat.md`** — التوافق الكامل — كل جوال، كل متصفح، كل شاشة، آيفون كـPWA: نفس الميزات في كل مكان، بلا تداخل نصوص/أيقونات، بلا أخطاء. يُفحص قبل كل تسليم.
  - أقسام: Android (Compose) · الويب (كل المتصفحات والشاشات) · آيفون — PWA قابل للتثبيت (Safari وChrome) · قائمة الفحص قبل التسليم
  - يشير إلى: features/defaults.md
  - يُشار إليه من: README.md, docs/repo-map.md, features/defaults.md, playbooks/idea-to-product.md, sessions/2026-11-20-video-engine-v2.md
  - قريب منه: playbooks/idea-to-product.md, features/defaults.md, features/auto-update.md
- **`features/defaults.md`** — الميزات الافتراضية — تُبنى دون أن يطلبها ساجد: كل فكرة تُحلَّل من كل الزوايا، ثم تُضاف هذه الميزات تلقائياً حين تنطبق. يُذكر في الموجز ما أُضيف ولماذا، ويُسأل ساجد فقط إن كانت الإضافة تغيّر ميزة موجودة.
  - أقسام: قاعدة الاستنتاج (مثال ساجد) · 1) الهوية والأدوار · 2) التحديث التلقائي بمجلد منظم (Android) · 3) النسخ الاحتياطي اليومي · 4) الإشعارات · 5) الصلاحيات — الحد الأدنى، كلٌّ في وقته · 6) دائماً أيضاً
  - يشير إلى: features/auto-update.md, features/compat.md
  - يُشار إليه من: README.md, docs/repo-map.md, features/compat.md, playbooks/idea-to-product.md, sessions/2026-11-20-video-engine-v2.md
  - قريب منه: playbooks/idea-to-product.md, README.md, features/auto-update.md
- **`features/export-pipeline.md`** — ميزة: تصدير الكشوف (GRCS)
  - يُشار إليه من: README.md, playbooks/idea-to-product.md
  - قريب منه: projects/index.md
- **`features/firebase.md`** — ميزة: Firebase + Cloudflare
  - يُشار إليه من: README.md, playbooks/idea-to-product.md
  - قريب منه: playbooks/idea-to-product.md, projects/index.md, features/defaults.md
- **`features/icons.md`** — ميزة: Icons.kt
  - يُشار إليه من: README.md
  - قريب منه: preferences.md, README.md
- **`features/messages-notifications.md`** — ميزة: إشعارات الرسائل المحلية (GRCS v5.8.0)
  - أقسام: لوحة الإدارة (v5.8.1)
  - يُشار إليه من: README.md
  - قريب منه: features/background-sync.md, features/defaults.md
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
  - يشير إلى: docs/repo-map.md, features/background-sync.md, features/compat.md, features/defaults.md, features/export-pipeline.md, features/firebase.md, ideas.md
  - يُشار إليه من: README.md, docs/account-instructions.md, docs/repo-map.md
  - قريب منه: features/defaults.md, README.md, mistakes.md

## projects
- **`projects/index.md`** — فهرس المشاريع النشطة: يُحدَّث عند بدء مشروع جديد أو تغيير حالة
  - أقسام: قيد — نظام إدارة متاجر · SMS Barq — تطبيق رسائل SMS · android-template — القالب الرئيسي · Sport Monitor AI — مراقبة رياضية · GRCS — منظومة مخيمات النزوح (Android الأصلي + نسخة ويب)
  - يُشار إليه من: README.md
  - قريب منه: ideas.md, README.md, mistakes.md

## sessions
- **`sessions/2026-11-20-video-engine-v2.md`** — محرّك فيديو الكلام v2 + المراجع الذهبية + مكتبة الأصول
  - أقسام: الطلب · ما نُفّذ · القرارات · الأخطاء والدروس · التالي
  - يشير إلى: features/compat.md, features/defaults.md, mistakes.md
  - يُشار إليه من: sessions/index.md
  - قريب منه: assets/README.md, README.md, mistakes.md
- **`sessions/index.md`** — سجل الجلسات: كل جلسة عمل تُكتب هنا عند نهايتها ثم تُرفع. «رتّب الدماغ» يعيد بناء هذا الفهرس.
  - يشير إلى: sessions/2026-11-20-video-engine-v2.md
  - يُشار إليه من: README.md
  - قريب منه: sessions/2026-11-20-video-engine-v2.md

## video-identity
- **`video-identity/README.md`** — هوية فيديوهات ساجد: إلزامي: أي فيديو أو ريل أو منشور بصري لحسابات ساجد يبدأ بقراءة هذا الملف. المحتوى يتغيّر، الهوية ثابتة.
  - أقسام: الحالة · أسرع مسار لأي فيديو جديد (توفير توكنز) · فيديو يتكلم فيه ساجد · فيلم منتج طويل بلقطات حقيقية · المكتبة والأفكار · قواعد فيديو الكلام (ملاحظات ساجد 2026-11-18 — إلزامية) · مراجع الموشن (تغذية بصرية — يغذيها ساجد) · قرارات معتمدة من ساجد · الحسابات (للخاتمة) · الألوان · هيكل كل فيديو (9:16) · ممنوع
  - يشير إلى: mistakes.md, video-identity/film/README.md, video-identity/icons/platforms.json, video-identity/ideas/playbook.md, video-identity/library/index.md, video-identity/references/motion/SYNTHESIS.md, video-identity/references/motion/sources.md, video-identity/talk/README.md, video-identity/templates/README.md, video-identity/tokens.json
  - يُشار إليه من: README.md, mistakes.md, video-identity/ideas/playbook.md
  - قريب منه: video-identity/talk/README.md, mistakes.md, video-identity/ideas/playbook.md
- **`video-identity/film/README.md`** — فيلم المنتج (film/) — لقطات حقيقية + حركة + صوت: للأفلام الأطول (40–60ث) عن تطبيق: يركّب لقطات تسجيل شاشة حقيقية داخل جوال، كاميرا زوم، عدّادات، بطاقات، تعليق صوتي Gemini TTS، وكابشن كلمة بكلمة، بهوية فيروز ون
  - أقسام: الملفات · الأمر · ملاحظات
  - يشير إلى: video-identity/film/script.json
  - يُشار إليه من: video-identity/README.md
  - قريب منه: mistakes.md, video-identity/README.md, video-identity/talk/README.md
- **`video-identity/ideas/playbook.md`** — دليل أفكار الفيديو — مخزون الإلهام: اقرأه عند التخطيط لفيديو جديد فقط. كل فكرة هنا تُنفَّذ داخل هوية فيروز ونحاس.
  - أقسام: قاعدة الاختيار · صيغ الفيديو (Formats) · خطّافات (أول ثانيتين) — قوالب عربية · تقنيات حركة (Motion) — مرتبة حسب القوة · قواعد المونتاج · نصوص الكابشن تحت المنشور · فيديو كلام ساجد · دروس من فيديوهات ساجد الحقيقية · ما لم يُنفَّذ بعد في القوالب (أولوية)
  - يشير إلى: video-identity/README.md, video-identity/library/index.md
  - يُشار إليه من: docs/repo-map.md, video-identity/README.md
  - قريب منه: video-identity/README.md, video-identity/references/motion/LEXICON.md, video-identity/talk/README.md
- **`video-identity/references/libraries.md`** — حزم المونتاج — ما في الريبو وما ينزّله ساجد مرة واحدة: حدّث هذا الملف عند إضافة أي حزمة. التنزيل اليدوي يُرفع إلى Drive «sajed-brain مكتبة المونتاج» https://drive.google.com/drive/folders/1YHP-lxsaWe4uIWyB2mQHbiZPXi
  - أقسام: في الريبو (نزّلها Claude بنفسه — لا تحتاج شيئاً) · ينزّله ساجد (ملف مضغوط واحد لكل حزمة) — بالترتيب · لا يلزم تنزيله · نماذج مفتوحة أقوى (للترقية لاحقاً) · طريقة الرفع
  - يشير إلى: assets/README.md
  - يُشار إليه من: assets/README.md, docs/repo-map.md
  - قريب منه: assets/README.md, sessions/2026-11-20-video-engine-v2.md, video-identity/references/motion/SYNTHESIS.md
- **`video-identity/references/motion/LEXICON.md`** — معجم الموشن — لغة مشتركة لوصف المراجع وتنفيذها: كل تفسير في `notes.md` يستخدم أسماء من هنا. العمود الأخير: أين ينفَّذ عندنا. أضف تقنية جديدة كلما ظهرت في مرجع.
  - يشير إلى: video-identity/references/motion/notes.md
  - يُشار إليه من: video-identity/references/motion/notes.md
  - قريب منه: video-identity/references/motion/notes.md, video-identity/references/motion/SYNTHESIS.md, video-identity/talk/README.md
- **`video-identity/references/motion/SYNTHESIS.md`** — خلاصة مراجع الموشن — ماذا يجعل المونتاج فخماً (2026-11-19، 16 مرجعاً، 6 عربية): يُقرأ قبل أي فيديو فخم. يُحدَّث كلما أضاف ساجد مراجع.
  - أقسام: الأنماط المشتركة (مرتبة حسب الأثر) · الترجمة لهوية ساجد (فيروز ونحاس) · خطة البناء في الأداة — ✅ نُفّذت 1–5 في 2026-11-19 (انظر `talk/README.md` ← عناصر الموشن)
  - يشير إلى: video-identity/references/motion/gold/README.md, video-identity/talk/README.md
  - يُشار إليه من: video-identity/README.md, video-identity/talk/README.md
  - قريب منه: video-identity/references/motion/LEXICON.md, video-identity/references/motion/notes.md, video-identity/talk/README.md
- **`video-identity/references/motion/gold/README.md`** — المراجع الذهبية — المستوى المطلوب حرفياً (اختيار ساجد 2026-11-20): كل فيديو كلام يُقاس عليها قبل التسليم. اللقطات `after-*.jpg` = جانب "After" فقط مقصوصاً، لقطة كل 0.5–1ث.
  - أقسام: ما يصنع الفخامة فيها (تحليل إطاراً إطاراً)
  - يُشار إليه من: video-identity/references/motion/SYNTHESIS.md
  - قريب منه: video-identity/references/motion/notes.md, video-identity/references/motion/SYNTHESIS.md, video-identity/references/motion/LEXICON.md
- **`video-identity/references/motion/notes.md`** — ملاحظات مراجع الموشن: سطر لكل فيديو مرجعي. القياسات تُكتب آلياً؛ Claude يستبدل "⏳ يحتاج تفسير" بالتقنية وطريقة تطبيقها بهويتنا بعد النظر إلى `refs/<slug>/sheet.jpg` فقط. المصطلحات من
  - يشير إلى: video-identity/references/motion/LEXICON.md
  - يُشار إليه من: README.md, video-identity/references/motion/LEXICON.md
  - قريب منه: video-identity/references/motion/LEXICON.md, video-identity/references/motion/SYNTHESIS.md, video-identity/references/motion/gold/README.md
- **`video-identity/references/motion/sources.md`** — مصادر مراجع الموشن — أين نبحث وبأي كلمات: لساجد: ابحث بهذه الكلمات، حمّل ما يعجبك، وارفعه إلى `inbox/` أو ضع رابط Drive في `links.txt`.
  - أقسام: اسم الأسلوب الذي نريده لفيديوهات الكلام · أين تبحث · مختارات بدأتُ بها (2026-11-18) · فرق مهم
  - يُشار إليه من: video-identity/README.md
  - قريب منه: video-identity/references/libraries.md, assets/README.md, video-identity/README.md
- **`video-identity/talk/README.md`** — فيديو كلام ساجد ← ريل بهويته: **قبل أي شيء:** طبّق "قواعد فيديو الكلام" في `../README.md` (نص حرفي، كل لغة بخطها، كابشن أسفل قوي، صوت طبيعي، موشن من دلالات الكلام، لا مقدمة مبرمج). المحرّك v
  - أقسام: المسار (أرخص بالتوكنز) · ما يحدث في الرندر · المتطلبات · ما تفرضه الأداة الآن (قواعد ساجد 2026-11-18) · عناصر الموشن (من خلاصة المراجع — `../references/motion/SYNTHESIS.md`)
  - يشير إلى: rules/arabizi.json, video-identity/references/motion/SYNTHESIS.md
  - يُشار إليه من: video-identity/README.md, video-identity/references/motion/SYNTHESIS.md
  - قريب منه: video-identity/README.md, video-identity/references/motion/LEXICON.md, mistakes.md
