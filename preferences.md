# تفضيلات ساجد الثابتة
_يُحدَّث عند ظهور تفضيل جديد_

## اللغة والتواصل
- الردود بالعربية، المعرّفات والـsyntax والـcommits بالإنجليزية
- لا ترحيب ولا حشو، قرارات صارمة وردود مختصرة
- خطأ واحد قبل الكود، 3 نقاط كحد أقصى للشرح

## التصميم
- OKLCH لكل الألوان — لا hex مباشر في أي مكان غير BrandConfig
- خط عربي مختلف لكل مشروع (Readex Pro, Alexandria, Almarai, IBM Plex Sans Arabic, ...)
- أيقونات hand-crafted ImageVector/Canvas في Icons.kt — لا icon packs ولا emoji
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
