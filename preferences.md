# تفضيلات ساجد الثابتة
_يُحدَّث عند ظهور تفضيل جديد_

## اللغة والتواصل
- الردود بالعربية، المعرّفات والـsyntax والـcommits بالإنجليزية
- لا ترحيب ولا حشو، قرارات صارمة وردود مختصرة
- خطأ واحد قبل الكود، 3 نقاط كحد أقصى للشرح

## التصميم
- OKLCH لكل الألوان — لا hex مباشر في أي مكان غير BrandConfig
- خط عربي مختلف لكل مشروع (Readex Pro, Alexandria, Almarai, IBM Plex Sans Arabic, ...)
- واجهات التطبيقات: أيقونات hand-crafted ImageVector/Canvas في Icons.kt — لا icon packs ولا emoji
- لا إيموجي إطلاقاً في أي تصميم أو فيديو أو ملف (ولا مجسمات إيموجي 3D)؛ الفيديو يستخدم أيقونات التصميم المفهرسة في `assets/`
- عائلة أيقونات واحدة لكل app: شبكة 24dp، سماكة خط موحدة، طقم كامل من البداية
- Material You = opt-in فقط في BrandConfig، الـbrand palette هي الافتراضي
- شاشة واحدة = هدف واحد + زر primary واحد فقط
- بيانات تجريبية: أسماء عربية حقيقية، عملة محلية، لا "John Doe" ولا lorem ipsum
- أرقام tabular (fontFeatureSettings = "tnum") في كل قائمة وجدول وKPI
- أرقام داخل نص عربي = LTR isolate

## المعمارية
- BrandConfig.kt = المصدر الوحيد: brand، OKLCH، fonts، modules، Firebase، license
- schema-driven: كل وحدة = schema object (~10 سطور)، engine واحد يرسم كل شيء
- طبقات صارمة: ui → ViewModel → repository → data
- UiState واحد immutable لكل شاشة
- أخطاء كـsealed results، لا swallowed exceptions
- Room: numbered migrations، append-only، لا تعديل على migration قديمة
- Balance مشتق دائماً من transactions، لا يُخزَّن أبداً

## الكود
- لا TODO، لا AI artifacts، لا purposeless lines
- الكشّاف: أثناء التنقل يُحدَّث القديم ويُصلَح الخطأ ويُحذف الميت ويُدمج المكرر وفق سلّم T0–T3 (CHARTER.md)
- تعليقات عربية مختصرة عند الضرورة فقط
- ProGuard/R8 مفعّل على release
- لا secrets في الكود أو logs أو commits

## الـworkflow
- مشروع جديد → يبدأ من Dev-saged/android-template دائماً
- prototype أولاً (3 اتجاهات بصرية) → انتظار اختيار ساجد → بناء على الشل المختار
- أول push يحتوي الأساس كاملاً (BrandConfig، Icons، shell، Room، schema، #test، CI/CD)
- "جاهز" = build + tests خضراء فعلياً، لا ادعاء

## حجم الملفات والتوثيق (Nov 2026)
- لا قيود حجم على أي ملف توثيق أو ذاكرة في أي مشروع: `docs/repo-map.md` و`.claude/session-handoff.md` و`CLAUDE.md` تنمو بقدر الحاجة. لا تحذف معلومة ولا تختصرها لتدخل حداً.
- الترتيب بدل الحذف: عناوين ثابتة (Features / Decisions / Solved bugs / Open issues) ليبقى القارئ سريعاً.

## الفيديو والمحتوى (Nov 2026)
- القانون: `video-identity/references/motion/gold/GRAMMAR.md` — سطح نص واحد، كابشن بالعبارة، مشاهد ≥45%، انتقالات مقيسة.
- نص حرفي لا يُغيَّر، كل لغة بخطها، صوت طبيعي، ألوان وخط العناوين من مزاج المحتوى، غلاف مصمم لكل فيديو، لا نص على الوجه في البداية.
- لا رندر لأي فيديو حتى يطلب ساجد صراحة؛ التحليل والتعلّم والتخزين أولاً.

## الأصول والمراجع (Nov 2026)
- ما يرفعه ساجد (Drive «sajed-brain مكتبة المونتاج») يتقدّم على البحث؛ «فهرس الجديد» ← `scripts/assets_ingest.py`.
- عند الحاجة لأصول: حزم جاهزة (zip واحد لكل صنف) مع اسم مجلد Drive لكل حزمة.

## الذاكرة والجلسات (Nov 2026)
- كل جلسة تنتهي بملف في `sessions/` يُرفع للمستودع؛ «رتّب الدماغ» ← `scripts/brain_tidy.py` (ويعمل يومياً في brain-daily).
- `rules/consistency.json` يمنع عودة أي قرار قديم (تغليف الويب القديم، إيموجي، ألوان فيديو ثابتة، قيود حجم) — brain_doctor يفشل عند التعارض.
