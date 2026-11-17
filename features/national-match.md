# ميزة: مطابقة السجل الوطني (GRCS)

- `NatStream.readXlsx`: ZipFile متعدد المرور (صفوف العناوين ← فهرس النصوص المشتركة لهويات المسجَّلين ← مرور واحد للورقة ← حلّ النصوص للصفوف المحتفَظ بها فقط)
- `NatRef.Reconcile`: يملأ الحقول الفارغة فقط؛ health→diseaseDetails، originCity→customFields، housing→livingSituation، الجوال يُطبَّع (9 أرقام تبدأ 5 → 05…)
- يتجاهل أعمدة مندوب/مسؤول/كلمة المرور
- اختبار: `NatStreamTest` (ملف حقيقي عبر env `GRCS_SAMPLE`)
