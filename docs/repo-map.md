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
- كتابة آمنة للدماغ: .github/workflows/brain-update.yml ← scripts/update_brain.py

## القرارات
- سلّم T0–T3 بدل المنع المطلق في mistakes.md: تنظيف مُثبَت بالـbuild مسموح، حذف العام/المهاجرات بإذن.
- تحليل نصّي بدل compiler: بلا اعتماديات، يعمل في CI بثوانٍ؛ الثمن إيجابيات كاذبة ← العام يبقى T2.
- المخرجات في docs/ تُستثنى من المسح كي لا تُحسب مراجع.
- commit-msg يزيل ذيول الأدوات تلقائياً (طلب ساجد: لا تمييز لعمل الذكاء الاصطناعي).

## أخطاء محلولة
- regex الـimports كان يلتقط `\n` فيفشل تطابق النص ← `[ \t]*$` بدل `\s*$`.

## مشاكل مفتوحة
- README يشير إلى features/{room-setup,icons,motion,firebase}.md وهي غير موجودة (doctor يحذّر).
- لم يُشغَّل scout على qayd/SMS-Barq؛ لم تُشغَّل الـworkflows على GitHub.
