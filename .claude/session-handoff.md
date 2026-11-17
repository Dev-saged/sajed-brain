# session-handoff — 2026-11-17

## الحالة
Mission Control v2 مبني على فرع `ccr-1b5607e5-njtdv9`: scout + guards + deps radar + brief + doctor + crossref + خطافات مشروع + install + 3 workflows + CHARTER.
الاختبارات: `python3 -m unittest discover -s tests -t .`

## القرارات
- سلّم T0–T3 يحل تعارض "لا تبسّط/لا تحذف" مع طلب التنظيف الذاتي (محدَّث في mistakes.md وpreferences.md).
- لا ذيول أدوات في commits؛ commit-msg ينظّفها.
- التعلّم = كتابة إلى الدماغ عبر `learn` وworkflow brain-update، لا "تدريب".

## مفتوح
- features/{room-setup,icons,motion,firebase}.md مذكورة في README وغير موجودة.
- scout لم يُجرَّب على qayd/SMS-Barq؛ الـworkflows لم تُشغَّل على GitHub (يلزم GH_PAT في الدماغ).
- فرع التطوير لم يُدمج في main بعد.

## الخطوة التالية
ساجد يختار من Roadmap في docs/mission-control.md (أقترح 1 و2 و3)، ثم: تشغيل `install_project.py` على qayd وSMS-Barq وأول scout حقيقي.
