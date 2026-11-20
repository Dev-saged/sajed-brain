# مكتبة الأصول المفهرسة (assets/)

مكتبة مجانية مرخّصة للاستخدام التجاري، مفهرسة بالعربي والإنجليزي حتى يُختار الأصل الصحيح فوراً بالمعنى (قلب ← قلب).

| المجلد | المحتوى | العدد | الترخيص |
|---|---|---|---|
| `icons/duotone`, `icons/fill` | Phosphor — أيقونات خطية SVG | 1512 | MIT |
| `icons3d/` | Microsoft Fluent Emoji 3D — مجسمات مفرغة WebP شفاف 256px | 1563 | MIT |
| `sfx/<فئة>/` | SFX Kit (wyzowl) — مؤثرات صوتية OGG بنقطة تزامن | 320 | CC0 |
| `index.json` | فهرس موحّد: id، نوع، ملف، وسوم en، كلمات ar (CLDR + ar-concepts.json)، وللأصوات: وصف، مدة، sync | — | كلمات CLDR: Unicode License |

## الاستخدام
```bash
python3 assets/find.py قلب                       # أفضل الأصول من كل الأنواع
python3 assets/find.py "كاسة شاي" --type icon3d -n 3
python3 assets/find.py انتقال --type sfx
```
- في بطاقات الفيديو (`talk.json`): `"icon": "مطر"` تكفي؛ `compose.resolve_icon` تحلّها من المكتبة. `"style": "line"` لأيقونة Phosphor بدل المجسم.
- كلمة عربية لا تُطابق جيداً ← أضفها إلى `ar-concepts.json` (عربي ← أسماء إنجليزية) ثم أعد البناء.

## إعادة البناء / التحديث
`python3 scripts/assets_build.py` (يتطلب npm, node, git, ffmpeg). يُعيد تنزيل المصادر ويكتب الفهرس من جديد.

## ما ينقص (أضفه متى توفّر)
- موسيقى خلفية خالية من الحقوق: Pixabay Music / Mixkit (روابط في `video-identity/references/libraries.md`).
- أيقونات متحركة Lottie: يمكن إضافة مجلد `lottie/` وتسجيله في assets_build.py.
