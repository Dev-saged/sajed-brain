# session-handoff — 2026-11-17

## الحالة
v2.1 على فرع `ccr-1b5607e5-njtdv9`: نُفّذت البنود 1–6 (auto-maintain، fixes، detekt، guard_suggest، journal، sajed-kit) فوق v2.
الاختبارات: `python3 -m unittest discover -s tests -t .` (59، واحد يُتخطّى بلا شبكة Gradle).

## القرارات
- سلّم T0–T3 (CHARTER)؛ تنظيف مُثبَت بالـbuild آلي، حذف العام/المهاجرات بإذن.
- لا ذيول أدوات في commits؛ commit-msg ينظّفها.
- الكيت JVM نقي فقط؛ تبنّيه PR مسوّدة بخطوات يدوية.
- التعلّم = كتابة للدماغ (`learn`)، وmistakes الجديدة تحتاج `guard:<id>` أو `noguard`.

## مفتوح
- لم يُشغَّل شيء على GitHub: يلزم GH_PAT في sajed-brain وكل مشروع، وتفعيل "Allow Actions to create PRs".
- الكود المولَّد في sajed-kit لم يُترجَم؛ detekt لم يُشغَّل فعلياً.
- features/{room-setup,icons,motion,firebase}.md مفقودة.
- الفرع غير مدموج في main.

## الخطوة التالية
دمج الفرع → إضافة GH_PAT → `install_project.py` على qayd وSMS-Barq → تشغيل brain-daily ثم brain-kit يدوياً وقراءة index/HEALTH.md.
