# 🧠 sajed-brain — السياق الكامل لساجد
_آخر تحديث: 2026-11-18 · Mission Control v2.1 · GRCS v5.7.0_

> **كيفية الاستخدام:** اقرأ هذا الملف أول شيء في كل جلسة. ابحث في الملفات الفرعية فقط عند الحاجة لتفاصيل ميزة معينة.

---

## مركز العمليات (Mission Control)
اقرأ `CHARTER.md` بعد هذا الملف — فيه سلّم الصلاحيات T0–T3 وبروتوكول الكشّاف (تحديث/إصلاح/حذف/دمج أثناء التنقل) والبصمة البشرية.
| الأداة | الغرض |
|--------|-------|
| `scripts/scout.py <project>` | فهرس كل رمز (`docs/symbol-index.tsv`) + ميت/imports/مكرر/أسرار/حرّاس الأخطاء ← تقرير scout داخل المشروع؛ `--where <اسم>` يعرض التعريف وكل مرجع |
| `scripts/deps_radar.py` | مقارنة libs.versions.toml بآخر الإصدارات؛ `--apply` لـpatch/minor فقط |
| `scripts/brief.py --task "..."` | يسترجع من الدماغ المقاطع ذات الصلة فقط ضمن ميزانية |
| `rules/guards.json` | كل خطأ سابق = قاعدة تُفحص تلقائياً (لا تكرار) |
| `scout.py --apply-fixes` / `--detekt-report` | إصلاحات API آلية 1:1 (`rules/fixes.json`) + تأكيد الميت بـdetekt |
| `scripts/auto_maintain.py` | صيانة أسبوعية T0/T1 → PR (workflow `auto-maintain.yml`) |
| `learn --bad '...'` / `learn --file journal` | حارس مقترح (PR) من خطأ · يومية ✓/✗ تُضغط شهرياً في `journal/digest.md` |
| `scripts/kit.py` | استخراج الدوال المتطابقة إلى sajed-kit + `adopt` يحوّل المشاريع |
| `scripts/install_project.py <path>` | يثبّت الخطافات + scout.yml + commit-msg + ملفات الذاكرة في أي مشروع |
| `index/HEALTH.md`, `index/CROSS.md` | لوحة صحة المشاريع + كود مكرر عبر المشاريع (مرشح لمكتبة مشتركة) |
تفاصيل → `docs/mission-control.md`

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
| مطابقة ملفات Excel ضخمة | قراءة xlsx متدفقة متعددة المرور بذاكرة قليلة (GRCS) → `features/national-match.md` |
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

## أين أجد ماذا (اقرأ عند الحاجة فقط)
| الموقف | الملف |
|---|---|
| لا تعرف أين المعلومة | `index/MAP.md` (خريطة مولّدة يومياً لكل الملفات: أقسامها، روابطها، والملفات القريبة منها) أو `python3 scripts/brief.py --task "..."` |
| **فكرة أو مشروع جديد أو ميزة كبيرة** | `playbooks/idea-to-product.md` — افهم ← وسّع (Core/Pro/Wow) ← كتالوج حسب النوع ← موجز ← تنفيذ كامل من أول مرة |
| نص تعليمات حساب ساجد الحالي (v3.3) | `docs/account-instructions.md` |
| تفضيلات ساجد (RTL، أيقونات يدوية، OKLCH، BrandConfig، schema، لا TODO) | `preferences.md` |
| أخطاء سابقة لا تتكرر | `mistakes.md` + `rules/guards.json` |
| قرارات وأفكار متراكمة | `ideas.md` |
| أي فيديو/ريل/منشور (مهارة `sajed-video`) | `video-identity/README.md` — فيروز ونحاس، "ساجد العبادلة · من غزة" |
