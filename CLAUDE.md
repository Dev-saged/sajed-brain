# sajed-brain
مستودع الدماغ المركزي لساجد + مركز العمليات (scout، deps radar، حرّاس، خطافات).

## ابدأ هنا
- اقرأ: هذا الملف، `.claude/session-handoff.md`، `docs/repo-map.md`. لا مسح للريبو.
- الدستور: `CHARTER.md`. التفاصيل والـroadmap: `docs/mission-control.md`.
- README.md يُجلب كل جلسة من كل مشروع ← أبقِه <6KB؛ التفاصيل في ملفات فرعية.

## قواعد هذا الريبو
- اختبارات: `python3 -m unittest discover -s tests -t .` يجب أن تنجح قبل أي push.
- `python3 scripts/brain_doctor.py` بلا أخطاء. لا أسرار في أي ملف.
- كل خطأ جديد ← سطر في mistakes.md + حارس في rules/guards.json إن أمكن.
- workflows: المدخلات تُمرَّر عبر env فقط، ولا كتابة خارج *.md في brain-update.
- بلا ذيول أدوات في commits (Co-Authored-By/Generated).
