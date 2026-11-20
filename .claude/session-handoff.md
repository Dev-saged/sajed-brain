# session-handoff — 2026-11-20 (محرّك فيديو الكلام v2 + مكتبة الأصول + الميزات الافتراضية)

## الحالة
- مكتبة أصول مفهرسة بالعربي: `assets/` — 1512 أيقونة Phosphor، 320 مؤثر صوتي CC0 (الإيموجي حُذف). بحث: `python3 assets/find.py "كاسة شاي" --type icon`. إعادة بناء: `scripts/assets_build.py`.
- خطوط جديدة في `video-identity/templates/fonts.css`: IBM Plex Sans Arabic، Noto Kufi، Reem Kufi، El Messiri، Aref Ruqaa Ink، Changa، Lalezar.
- talk v2: مزاج من المحتوى (MOODS: cozy/spiritual/tech/energy/hope/serious)، كابشن كتابي سطر ≤4 كلمات بلا تكرار/تكبير/وميض، بطاقات prop/icon/typo/image من المكتبة بالعربي، أقراص ui، رأس ورقي للـframes، أصوات حقيقية بنقطة تزامن، غلاف مصمم `<اسم>-غلاف.jpg` (cover.html).
- `features/defaults.md` (أدوار/دخول/استعادة/تذكرني، تحديث مخزّن يُحذف بعد التثبيت، نسخ يومي 3 أيام، إشعارات، صلاحيات) و`features/compat.md` (خط مكبّر، كل المتصفحات، PWA آيفون) — مربوطان في playbook وREADME.
- روابط المكتبات للتنزيل اليدوي: `video-identity/references/libraries.md`.

## القرارات
- العنوان لا يظهر داخل الفيديو؛ يذهب للغلاف (`cover`). `title` القديم يُقبل كبديل للغلاف.
- الكابشن دائماً IBM Plex Sans Arabic؛ خط العناوين يتبع المزاج.
- talk/icons حُذف (حلّت محله assets/icons).

## مفتوح
- 2026-11-20 (2): مراجع ذهبية `video-identity/references/motion/gold/` + محرّك بلا إيموجي (بلاطات زجاجية Phosphor) + إعادة إضاءة + عريض↔قريب + تسريب ضوئي/عودة ضبابية + كابشن بطبقتين. مقطع 30ث (12–42) أُرسل — بانتظار رأيه، ثم رندر كامل.
- مجلد رفع ساجد: Drive «sajed-brain مكتبة المونتاج» (7 مجلدات) ← `scripts/assets_ingest.py`.
- لا موسيقى خلفية في المكتبة بعد (يحتاج تنزيل ساجد من Pixabay/Mixkit إلى assets/incoming/).
- "تسجيل كل المحادثات" لا يحدث تلقائياً: المتاح يوميات الجلسة + استيراد تصدير بيانات claude.ai (conversations.json) عند رفعه.
- GH_PAT وتشغيل الـworkflows على GitHub ما زالا معلّقين.

## الخطوة التالية
ملاحظات ساجد على v2 ← تعديلات محددة فقط؛ فهرسة ما يرفعه في assets/incoming/.
