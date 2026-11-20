# session-handoff — 2026-11-20 (توحيد الدماغ وفحص التعارض التلقائي)

## الحالة
- الدماغ موحّد: README (كتلة إحصاءات مولّدة تلقائياً) ← CLAUDE.md ← هذا الملف ← docs/repo-map.md ← index/MAP.md. لا تعارض بين الملفات؛ `scripts/brain_doctor.py` يفحص التعارض بـ`rules/consistency.json` ويفشل عنده.
- التحديث التلقائي: brain-daily (يومياً) ← organize → `brain_tidy.py` (فهرس الجلسات + اليوميات + الإحصاءات) → الخريطة → doctor + tests → commit. يحتاج GH_PAT (أضافه ساجد) لجمع المشاريع.
- تعليمات الحساب v3.5: `docs/account-instructions.md` (الكامل) و`docs/account-preferences-short.md` (المختصر). ساجد يلصقها بنفسه في الإعدادات.
- مكتبة الأصول `assets/`: أيقونات تصميم (Phosphor/Hugeicons/MingCute)، مؤثرات CC0 (sfx-kit + Kenney)، 33 خطاً عربياً مفهرساً بالأسلوب (`scripts/fonts_build.py`)، بلا إيموجي. رفع ساجد: Drive «sajed-brain مكتبة المونتاج» (8 مجلدات) ← `scripts/assets_ingest.py`.
- فيديو الكلام: `video-identity/talk/` يطبّق `references/motion/gold/GRAMMAR.md` (سطح نص واحد، كابشن بالعبارة، scene/flow/quotes، 8 انتقالات، إعادة إضاءة، عريض↔قريب، غلاف). مُتحقق بلقطات ثابتة؛ لا رندر حتى يطلب ساجد.
- الذاكرة: كل جلسة ← `sessions/`؛ «رتّب الدماغ» ← brain_tidy؛ «استورد محادثاتي» ← import_chats.py (ينتظر تصدير claude.ai من ساجد).

## القرارات
- لا إيموجي إطلاقاً؛ لا WebToApp؛ لا قيود حجم؛ ألوان فيديو الكلام من المزاج (التوقيع والخاتمة ثابتان).
- ملفات التاريخ (mistakes، sessions، journal، gold، library) تحفظ ما حدث ولا تُفحص للتعارض.

## مفتوح
- حزم ساجد (99Sounds×2، Cinecom، MyCreativeFX، Editors Keys، موسيقى Pixabay، صور المشاهد) — حين يتحسن النت ← «فهرس الجديد».
- تصدير claude.ai ← «استورد محادثاتي».
- اقتراح تحديث مهارة sajed-video عُرض على ساجد (بطاقة) — بانتظار حفظه.
- فروع قديمة مدموجة (log-bad-film، video-film، ccr-*) لا تُحذف من الجلسة؛ ساجد يحذفها يدوياً إن أراد.

## الخطوة التالية
ملاحظات ساجد أو حزمه؛ الرندر فقط بطلبه.
