# repo-map
_تحت 5KB، بلا كود_

## الميزات (ميزة ← ملف ← رمز للبحث)
- فهرس رموز وفحص: scripts/scoutlib/cli.py ← `run`؛ تعريفات: symbols.py ← `extract`
- قواعد/حرّاس: rules/guards.json، rules/deprecated.json؛ التطبيق: findings.py ← `apply_rules`
- ميت/imports/مكرر: findings.py ← `dead_symbols`، `unused_imports`، `dup_bodies`
- migration معدّلة: findings.py ← `migration_edits` (يحتاج `--base`)
- رادار اعتماديات: scripts/deps_radar.py ← `run`، `apply`
- استرجاع سياق: scripts/brief.py ← `brief`؛ مرادفات rules/synonyms.json
- سلامة الدماغ: scripts/brain_doctor.py ← `check`
- عبر المشاريع: scripts/crossref.py ← `analyse`؛ التجميع scripts/collect.py (يحتاج GH_PAT + projects.json)
- طبقة المشروع: templates/claude/brain_hooks.py (boot/stop/learn/scout/commit-msg)، تثبيت scripts/install_project.py
- إصلاحات آلية: rules/fixes.json ← scoutlib/fixes.py `apply_fixes`؛ `cli.maintain` للصيانة
- detekt: scoutlib/external.py ← `merge`؛ الإعداد templates/detekt.yml
- صيانة أسبوعية: scripts/auto_maintain.py ← `main`؛ templates/workflows/auto-maintain.yml
- حارس من خطأ: scripts/guard_suggest.py ← `make_entry`، `add_entry`؛ workflow brain-guard.yml
- يوميات: scripts/journal_digest.py ← `run`؛ hooks `learn --file journal`
- sajed-kit: scripts/kit.py ← `extract`، `adopt`؛ workflows brain-kit.yml، kit-adopt.yml
- كتابة آمنة للدماغ: .github/workflows/brain-update.yml ← scripts/update_brain.py
- هوية الفيديو: video-identity/tokens.json (المصدر الوحيد)، icons/platforms.json
- تركيب فيديو: video-identity/templates/render.py ← `load_brand`، `film`؛ المشاهد video.html ← `scenes`؛ أرشفة render.py ← `archive`، `index_line` → video-identity/library/index.md؛ أفكار ideas/playbook.md
- فيديو كلام: video-identity/talk/talk.py ← `transcribe`، `auto_keep`، `plan`، `cut_source`؛ الكابشن talk.html

## القرارات
- سلّم T0–T3 بدل المنع المطلق في mistakes.md: تنظيف مُثبَت بالـbuild مسموح، حذف العام/المهاجرات بإذن.
- تحليل نصّي بدل compiler: بلا اعتماديات، يعمل في CI بثوانٍ؛ الثمن إيجابيات كاذبة ← العام يبقى T2.
- المخرجات في docs/ تُستثنى من المسح كي لا تُحسب مراجع.
- commit-msg يزيل ذيول الأدوات تلقائياً (طلب ساجد: لا تمييز لعمل الذكاء الاصطناعي).

- الفيديو يُؤرشف كـcontent.json + مصغّرة لا mp4: إعادة إنتاج حتمية وتوفير توكنز ومساحة.
- الفيديو: قوالب HTML تُصوَّر إطاراً إطاراً بـplaywright ← ffmpeg (حتمي وبلا شبكة، خطوط محلية).

## أخطاء محلولة
- faster-whisper فشل بـ`metadata_errors` (تعارض PyAV) ← تمرير الصوت مصفوفة numpy من wav بدل المسار.
- video.html كان يبني كل المشاهد فيتعطل بلا demo ← المشاهد تُبنى كسولاً (المطلوب فقط).
- build_pattern الأول لم يسمح بمسافات داخل الاستدعاء ← فاصل `\s*` بين كل رمزين، `\s+` بين كلمتين فقط.
- regex الـimports كان يلتقط `\n` فيفشل تطابق النص ← `[ \t]*$` بدل `\s*$`.

## مشاكل مفتوحة
- README يشير إلى features/{room-setup,icons,motion,firebase}.md وهي غير موجودة (doctor يحذّر).
- لم يُشغَّل scout على qayd/SMS-Barq؛ الـworkflows (brain-*، scout، auto-maintain، kit-adopt) لم تُشغَّل على GitHub.
- الكود المولَّد في sajed-kit لم يُترجَم؛ detekt لم يُشغَّل فعلياً.
- لا إزالة آلية للميت المؤكَّد بعد (تبقى يدوية بالتقرير).
