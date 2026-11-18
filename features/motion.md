# ميزة: Motion & life

- الشاشة الرئيسية حية: خلفية `Canvas` بتدرج/جزيئات عبر `rememberInfiniteTransition` (بطيئة، شفافية منخفضة).
- دخول متتابع للعناصر: `AnimatedVisibility` + تأخير `index * 40ms`، `spring(dampingRatio = 0.8f)`.
- التنقل: Compose Navigation + `SharedTransitionLayout` / `sharedElement` للبطاقة ← التفاصيل.
- ضغط البطاقات: `graphicsLayer { scaleX/Y = 0.97f }` عند الضغط + ripple.
- `HapticFeedback` للحفظ والحذف والنجاح فقط.
- تحميل: skeleton (`shimmer`) بدل spinner؛ pull-to-refresh عبر `PullToRefreshBox`.
- الأرقام: `AnimatedContent` للعدّادات في KPIs.
- الأداء: حرّك `graphicsLayer` (transform/alpha) فقط؛ احترم إعداد إزالة الحركات (`Settings.Global.ANIMATOR_DURATION_SCALE == 0` ← بلا حركة ولا haptics).
- تفاعل توقيع واحد لكل تطبيق، يُوثَّق في repo-map المشروع.
