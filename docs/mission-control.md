# Mission Control — الدماغ كمركز عمليات
_v2.1.0 · 2026-11-17_

## نظرة عامة
الدماغ لم يعد ملفات تُقرأ فقط: هو طبقة تعمل على كل مشروع. تفحص الكود، تفهرس كل رمز، تنفّذ الأخطاء السابقة كقواعد، تستدعي السياق بقدر المهمة، وتُلزم أي ذكاء يعمل في مشروعك ببروتوكول واحد.

## المعمارية
```
sajed-brain/
  CHARTER.md              الدستور (T0–T3، الكشّاف، بصمة بشرية، حلقة التعلّم)
  README.md               مدخل الجلسة (بلا قيد حجم)
  rules/guards.json       أخطاء/تفضيلات → regex منفَّذة   (source يشير للأصل)
  rules/deprecated.json   APIs مُهملة + بديلها + Tier
  rules/synonyms.json     عربي↔إنجليزي لاسترجاع brief
  scripts/scout.py        → scoutlib/{lexer,symbols,findings,report,cli}
  scripts/deps_radar.py   ترقيات libs.versions.toml
  scripts/brief.py        استرجاع بميزانية
  scripts/brain_doctor.py سلامة الدماغ (روابط، قواعد، أسرار)
  scripts/crossref.py     كود مشترك/منحرف عبر المشاريع
  scripts/collect.py      يجمع المشاريع → index/
  scripts/install_project.py   يركّب الطبقة في مشروع
  templates/              ما يُنسخ للمشاريع (hooks, settings, scout.yml, commit-msg)
  index/<project>/        symbol-index.tsv + scout + deps لكل مشروع؛ HEALTH.md، CROSS.md
  .github/workflows/      brain-update (كتابة آمنة) · brain-daily (اختبارات+تنظيم+جمع)
```
تدفق الجلسة: `SessionStart` يحمّل README+CHARTER+handoff+git log+scout ← العمل بالسلّم T0–T3 ← `learn` لكل جديد ← `Stop` يرفض الإنهاء بلا handoff محدَّث ← push يشغّل scout.yml ← يحدّث docs وindex/HEALTH.md.

## ما يتحقق منه scout
ميت (private=T0، عام=T2) · imports غير مستخدمة (يُطبَّق `--apply-imports`) · أجسام دوال متطابقة · نصوص/أبعاد/مدد مكررة → token · دوال >80 سطراً · catch فارغ · أسرار (تُحجب في التقرير) · ألوان خارج BrandConfig · Material You افتراضي · balance مخزّن · حزم أيقونات · WebView · TODO/debug/emoji · أثر أسلوب آلي · R8 معطّل · cleartext/allowBackup · APIs مُهملة · تعديل migration قديمة (`--base REF`).

## منفَّذ في v2.1
1. **Auto-PR أسبوعي**: templates/workflows/auto-maintain.yml + scripts/auto_maintain.py (إصلاحات + imports + ترقيات patch/minor؛ major يُذكر فقط).
2. **fixes.json**: rules/fixes.json + scoutlib/fixes.py (`--apply-fixes`)؛ تعديل الكود الفعلي فقط وضبط imports، وبعض القواعد مشروطة باعتمادية المشروع.
3. **تأكيد الميت**: scoutlib/external.py يدمج SARIF من detekt (`--detekt-report`)؛ مؤكَّد = T0، غير مؤكَّد = T1. (ktlint لم يُدمج: وظيفته التنسيق لا الميت.)
4. **حارس من الخطأ**: scripts/guard_suggest.py + workflow brain-guard.yml (PR)؛ doctor يحذّر من خطأ بلا `guard:<id>`.
5. **يوميات الجلسة**: `learn --file journal` + journal/digest.md من scripts/journal_digest.py (يومياً في brain-daily)؛ boot يعرض تعثّرات المشروع.
6. **sajed-kit**: scripts/kit.py (`extract` من CROSS، `adopt` في المشاريع) + brain-kit.yml + templates/workflows/kit-adopt.yml.

## Roadmap — المتبقي
7. شبكة معرفة: روابط بين القرارات والأخطاء والمشاريع (`#وسم`/`@مشروع`) + backlinks.
8. تقادم المعرفة: `last_verified` للحقائق المتغيّرة وإعادة تحقق دورية.
9. Release notes تلقائية من commits منذ آخر tag.
10. حزمة أمان: linter لـFirestore Rules مقابل schemas، exported components، ثغرات OSV.
11. رادار أداء: Compose stability، حجم APK لكل push، baseline profiles.
12. رادار فجوات الاختبار: دوال المال/الرصيد/migration بلا اختبار.
13. حارس تصميم: تباين ≥4.5 لـOKLCH tokens، أهداف لمس ≥44dp، انعكاس الأيقونات RTL.
14. لوحة ويب حيّة (Artifact) من scout-history.tsv.
15. `new-project` يستدعي install_project تلقائياً مع هيكل BrandConfig/schema.
16. بحث عابر: `ask "كيف عملنا X"` على الفهارس وتاريخ git.
17. إزالة آلية للميت المؤكَّد (حدود التصريح/الـannotations) ثم دمجه في auto-maintain.
18. نشر الكيت: تثبيت مستودع GitHub Packages تلقائياً في settings.gradle.kts.

## حدود معلنة
- sajed-kit: الكود المولَّد لم يُترجَم (kotlinc/Gradle بلا شبكة هنا)؛ الاستخراج متحفّظ (JVM نقي، بلا اعتماد على المشروع)، والتبنّي PR مسوّدة بخطوات يدوية (مستودع الحزم والاعتماد).
- detekt-cli v1.23.8 وأمر التشغيل في scout.yml لم يُشغَّلا فعلياً؛ التكامل اختُبر بملف SARIF مُحاكى.
- auto-maintain: بلا GH_PAT لا يعمل build.yml على الـPR (قيد GitHub).
- ‎fixes: تغييرات T1 (ripple، collectAsStateWithLifecycle) تتطلب build قبل الدمج.
- أُختبر على fixture Kotlin وعلى git محلي؛ لم يُشغَّل على qayd/SMS-Barq الفعليين بعد.
- الـworkflows (brain-update، brain-daily، scout.yml) لم تُشغَّل على GitHub بعد؛ كُتبت بحقن آمن للمدخلات وتحتاج تشغيلاً أولياً.
- deps_radar لم يُختبر على الشبكة الحيّة (اختُبر بمصدر مُحاكى).
