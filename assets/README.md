# مكتبة الأصول المفهرسة (assets/)

مكتبة مجانية مرخّصة للاستخدام التجاري، مفهرسة بالعربي والإنجليزي حتى يُختار الأصل الصحيح فوراً بالمعنى (قلب ← قلب).

| المجلد | المحتوى | العدد | الترخيص |
|---|---|---|---|
| `icons/duotone`, `icons/fill` | Phosphor — أيقونات خطية SVG | 1512 | MIT |
| `icons3d/` | Fluent Emoji 3D — **إيموجي، ممنوع في الفيديو والتصميم بقرار ساجد (2026-11-20)**؛ المحرّك يرفضه. بانتظار قراره بالحذف | 1563 | MIT |
| `sfx/<فئة>/` | SFX Kit (wyzowl) — مؤثرات صوتية OGG بنقطة تزامن | 320 | CC0 |
| `index.json` | فهرس موحّد: id، نوع، ملف، وسوم en، كلمات ar (CLDR + ar-concepts.json)، وللأصوات: وصف، مدة، sync | — | كلمات CLDR: Unicode License |

## الاستخدام
```bash
python3 assets/find.py قلب                       # أفضل الأصول من كل الأنواع
python3 assets/find.py "كاسة شاي" --type icon3d -n 3
python3 assets/find.py انتقال --type sfx
```
- في بطاقات الفيديو (`talk.json`): `"icon": "مطر"` تكفي؛ `compose.resolve_icon` تحلّها لأيقونة تصميم Phosphor داخل بلاطة زجاجية بلون المزاج (`"style": "fill"` للوزن المصمت).
- كلمة عربية لا تُطابق جيداً ← أضفها إلى `ar-concepts.json` (عربي ← أسماء إنجليزية) ثم أعد البناء.

## إعادة البناء / التحديث
`python3 scripts/assets_build.py` (يتطلب npm, node, git, ffmpeg). يُعيد تنزيل المصادر ويكتب الفهرس من جديد.

## ما ينقص (أضفه متى توفّر)
- موسيقى خلفية خالية من الحقوق: Pixabay Music / Mixkit (روابط في `video-identity/references/libraries.md`).
- أيقونات متحركة Lottie: يمكن إضافة مجلد `lottie/` وتسجيله في assets_build.py.

## رفع ساجد لأصوله (الطريق الأساسي — يوفّر البحث والتوكنز)
1. يرفع إلى Drive: مجلد **«sajed-brain مكتبة المونتاج»** https://drive.google.com/drive/folders/1YHP-lxsaWe4uIWyB2mQHbiZPXiaZDhG4
   (1-خطوط · 2-أيقونات · 3-مؤثرات-صوتية · 4-موسيقى · 5-حركات-نصوص · 6-انتقالات-وإضاءة · 7-مراجع-فيديو) — zip مقبول.
2. يقول «فهرس الجديد» ← Claude ينزّلها إلى `assets/incoming/<fonts|icons|sfx|music|text-motion|transitions|refs>/`، يشاهد/يسمع كل ملف ويكتب له وصفاً وكلمات عربية في ملف meta.json داخل incoming.
3. `python3 scripts/assets_ingest.py` ← تحويل (OGG للصوت، SVG بلون currentColor للأيقونات، الخطوط للقوالب، الفيديو لمراجع الموشن) وإضافة للفهرس بمصدر `sajed`؛ ما رفعه ساجد يتقدّم في البحث تلقائياً.
