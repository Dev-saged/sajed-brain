# 🧠 sajed-brain — السياق الكامل لساجد
_آخر تحديث: 2026-11-17 (GRCS v5.7.0)_

> **كيفية الاستخدام:** اقرأ هذا الملف أول شيء في كل جلسة. ابحث في الملفات الفرعية فقط عند الحاجة لتفاصيل ميزة معينة.

---

## الميزات الثابتة — كل مشروع Android يجب أن يحتويها
| الميزة | التفاصيل |
|--------|----------|
| auto-update | GitHub Release API → قارن versionCode → بانر RTL إذا يوجد إصدار أحدث → `features/auto-update.md` |
| BrandConfig.kt | مصدر الحقيقة الوحيد: OKLCH palette، fonts، modules، Firebase config، license expiry → `features/brand-config.md` |
| Room + migrations | SQLite مع WAL، migrations مرقّمة append-only، JSON export/import → `features/room-setup.md` |
| Schema engine | كل module = schema object (10 سطور)، Composable engine واحد يرسم forms/lists/filters/KPIs → `features/schema-engine.md` |
| Icons.kt | hand-crafted ImageVector، عائلة واحدة لكل app، شبكة 24dp، طقم كامل من البداية، الاتجاهية تنعكس RTL → `features/icons.md` |
| Motion & life | خلفية حية في الـhome، SharedTransitionLayout، haptics، skeleton loading، pull-to-refresh → `features/motion.md` |
| Firebase + Cloudflare | مشروع Firebase لكل عميل، Security Rules إلزامية، Cloudflare Worker للعمليات الحساسة → `features/firebase.md` |
| مزامنة سريعة | نبض `sync/pulse` + فحص 45ث + عامل 6 ساعات → `features/background-sync.md` |
| تصدير بتقدّم | foreground service + إشعار + مجلد منظم، كشف أفقي → `features/export-pipeline.md` |
| CI/CD | build.yml → sign (KEYSTORE_BASE64 + SIGNING_*) → Release "latest-build" → unpack-zip.yml → repomap.yml → `features/ci-cd.md` |

---

## المشاريع النشطة
| المشروع | المستودع | Stack | الحالة | آخر إصدار |
|---------|----------|-------|-------|-----------|
| قيد — نظام متاجر | Dev-saged/qayd | Kotlin+Compose+Firebase+Cloudflare | نشط | v2.x |
| SMS Barq — رسائل SMS | Dev-saged/SMS-Barq | Kotlin+Compose | نشط | v1.x |
| القالب الرئيسي | Dev-saged/android-template | Kotlin+Compose | قالب | - |
| GRCS — مخيمات النزوح | Dev-saged/wasla-system | Kotlin+Compose+Firestore REST + ويب | نشط | v5.7.0 |
| Sport Monitor AI | Dev-saged/sport-monitor-ai | Python Flask + Android WebView | نشط | - |

تفاصيل كل مشروع → `projects/index.md`

---

## تفضيلات ساجد الثابتة
→ القائمة الكاملة في `preferences.md`
- عربي RTL، أسماء عربية حقيقية في بيانات العرض، لا "John Doe"
- أيقونات مرسومة يدوياً، لا icon packs ولا emoji
- OKLCH لكل الألوان، لا hex مباشر
- BrandConfig.kt المصدر الوحيد للألوان والإعدادات
- schema-driven: كل وحدة schema لا Composable مخصص
- Material You opt-in فقط، الـbrand palette هي الافتراضي
- تحديث تلقائي في كل app عبر GitHub Release
- لا TODO في الكود، لا AI artifacts، لا purposeless lines
- تعليقات عربية مختصرة فقط عند الضرورة

---

## أخطاء حدثت — لا تكررها
→ القائمة الكاملة في `mistakes.md`
- `gh api` يرجع "null" على 404 في bulk workflows → تحقق من وجود الملف قبل التعديل
- nested folder داخل zip يكسر unpack-zip.yml → flatten الـzip عند الرفع
- Material You كان default → غُيّر إلى opt-in في BrandConfig (قرار Nov 2026)

---

## أفكار وقرارات متراكمة
→ `ideas.md`
