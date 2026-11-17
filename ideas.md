# أفكار وقرارات متراكمة
_سياق يتراكم عبر الجلسات_

## قرارات معمارية مهمة (Nov 2026)
- **android-template** = نقطة البداية لكل مشروع جديد، لا repo فارغ
- **BrandConfig.kt** = المصدر الوحيد لكل شيء له علاقة بالعلامة التجارية
- **schema-driven** = لا Composable مخصص لكل وحدة، schema object + generic engine
- **Material You** = opt-in في BrandConfig بعد أن كان default (تعارض مع brand palette)
- **docs/code-index.md** = auto-generated، لا تُعدَّل يدوياً، Grep فقط
- **git log --oneline -15** = بديل خفيف لمسح الملفات عند عودة الجلسة

## نظام الذاكرة (Nov 2026)
- هذا الـrepo (sajed-brain) = الدماغ المركزي، يُقرأ أول جلسة
- كل مشروع لديه: CLAUDE.md + docs/repo-map.md + .claude/session-handoff.md
- session-handoff.md = max 25 سطراً، يُعاد كتابته كل جلسة
- repo-map.md = تحت 5KB، يُحدَّث بسطرين بعد كل تغيير

## أفكار لم تُنفَّذ بعد
- white-label: كل عميل = BrandConfig مختلف فقط، نفس الكود
- نظام subscriptions/license expiry في BrandConfig

## ملاحظات على المشاريع
- **قيد**: نظام متاجر متعدد (PlayStation sessions, debts, electricity, messages)
  - Balance يُشتق من transactions append-only، لا يُخزَّن
  - PlayStation sessions: timestamp مطلق للبداية، الـUI يحسب المدة
  - Security Rules تفرض shopId isolation + roles + paid features
- **SMS Barq**: SMS engine في حزمة sms/ (SendEngine، SendQueue، SendDrainer، ...)
- **Sport Monitor AI**: Python Flask على Termux، Android WebView bridge

## GRCS (Nov 2026)
- نسخة الويب تتبع التطبيق في الإصدار؛ فكّر بتوليد `version.json` تلقائياً من `gradle.properties` في CI
- قرار: المندوب والمستفيد قد يحتاجان نبضاً خاصاً؛ حالياً النبض للمدير والمندوب
- فكرة: سجل مركزي لأخطاء المشاريع في هذا المستودع يُقرأ أول كل جلسة (خريطة محادثات/مشاريع)
