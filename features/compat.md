# التوافق الكامل — كل جوال، كل متصفح، كل شاشة، آيفون كـPWA
_نفس الميزات في كل مكان، بلا تداخل نصوص/أيقونات، بلا أخطاء. يُفحص قبل كل تسليم._

## Android (Compose)
- النصوص دائماً `sp`، والأبعاد `dp`. **لا ارتفاع ثابت لأي حاوية فيها نص**: `heightIn(min = 48.dp)` بدل `height(48.dp)`، و`wrapContentHeight`.
- الخط المكبّر حتى 200% (Android 14 nonlinear scaling): صفوف أفقية تتحول لعمودية عند الضيق — `FlowRow` أو `BoxWithConstraints`/`LocalDensity.current.fontScale > 1.3` ⇒ تخطيط عمودي.
- `maxLines` + `TextOverflow.Ellipsis` فقط للعناوين الثانوية؛ النص المهم يلتف ولا يُقطع.
- أيقونة بجانب نص: `Row(verticalAlignment = CenterVertically)` مع `Modifier.weight(1f)` للنص — الأيقونة لا تُدفع خارج الشاشة.
- الأزرار: `defaultMinSize` 48dp، والنص داخلها يلتف. Bottom nav: تسميات تختفي عند fontScale عالٍ وتبقى في contentDescription.
- Insets: `enableEdgeToEdge()` + `WindowInsets.safeDrawing` + `imePadding()` (Android 15 يفرض edge-to-edge).
- شاشات: `WindowSizeClass` (compact/medium/expanded) للأجهزة اللوحية والطيّ، واتجاه أفقي مدعوم.
- minSdk 26: كل API أحدث خلف `Build.VERSION.SDK_INT` مع بديل.
- فحص إلزامي: Paparazzi/Roborazzi snapshots بـ `fontScale = 1.0, 1.5, 2.0` × `RTL` × (فاتح/داكن) × (360dp, 600dp)؛ وCompose UI test يتحقق من عدم تداخل الحدود (`assertIsDisplayed` + مقارنة bounds).

## الويب (كل المتصفحات والشاشات)
- `rem` للخطوط و`clamp()` للتدرج، لا `px` ثابت لحجم الخط؛ احترام تكبير المتصفح حتى 200% بلا تمرير أفقي.
- container queries + `flex-wrap` + `min-width: 0` على عناصر flex؛ لا `height` ثابت لعناصر نصية (`min-height`).
- `100dvh` بدل `100vh`، و`env(safe-area-inset-*)` للنوتش. خصائص منطقية (`margin-inline-start`) لـRTL.
- اكتشاف الميزات (`@supports`، `'x' in window`) مع بديل لكل API حديث (View Transitions، Popover، @starting-style، light-dark()).
- مستهدف: Chrome/Edge/Firefox/Safari آخر إصدارين + Samsung Internet + Safari iOS 16.4+. فحص Playwright على chromium + webkit + firefox بمقاسات 360/768/1366/1920.

## آيفون — PWA قابل للتثبيت (Safari وChrome)
- manifest: `name`, `short_name`, `start_url`, `scope`, `display: "standalone"`, `theme_color`, `background_color`, `icons` (192, 512, maskable).
- iOS يحتاج أيضاً في `<head>`:
  ```html
  <link rel="apple-touch-icon" href="/icons/apple-180.png">
  <meta name="apple-mobile-web-app-capable" content="yes">
  <meta name="mobile-web-app-capable" content="yes">
  <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
  <meta name="apple-mobile-web-app-title" content="الاسم">
  <meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
  ```
  + شاشات بداية `apple-touch-startup-image` (أو لون خلفية مناسب).
- **نافذة التثبيت:**
  - Android/Chrome/Edge: التقط `beforeinstallprompt` ⇒ ورقة سفلية بتصميم التطبيق وزر "ثبّت" ⇒ `prompt()`.
  - iOS (Safari، وChrome على iOS 16.4+ يدعم الإضافة للشاشة الرئيسية): لا يوجد `beforeinstallprompt` ⇒ ورقة مخصصة تظهر إن لم يكن `navigator.standalone` ولا `matchMedia('(display-mode: standalone)')`، بخطوات مرسومة: زر المشاركة ⇒ "إضافة إلى الشاشة الرئيسية" (في Chrome iOS: زر المشاركة بجانب شريط العنوان).
  - تظهر بعد تفاعل ذي معنى لا فوراً، تُغلق وتُؤجَّل 7 أيام (localStorage داخل try/catch)، ولا تظهر داخل التطبيق المثبت.
- قيود iOS يجب تصميم بديل لها: التخزين قد يُمسح بعد أسابيع من عدم الاستخدام ⇒ `navigator.storage.persist()` + نسخ احتياطي/سحابة؛ Push فقط بعد التثبيت (16.4+)؛ لا Background Sync ⇒ مزامنة عند الفتح؛ لا اهتزاز (navigator.vibrate غير مدعوم) ⇒ تجاهل بصمت.
- Service worker: cache-first للأصول، network-first للبيانات، صفحة offline، وتحديث بالبانر (`features/defaults.md` §2).

## قائمة الفحص قبل التسليم
- [ ] Android: لقطات fontScale 1/1.5/2 × RTL بلا تداخل أو قص.
- [ ] الويب: 360→1920 بلا تمرير أفقي، تكبير 200% سليم، webkit + firefox + chromium.
- [ ] PWA: Lighthouse installable، نافذة تثبيت Android تعمل، ورقة iOS تظهر في Safari وChrome iOS وتختفي بعد التثبيت.
- [ ] نفس الميزات في كل منصة، أو بديل موثّق لكل قيد.
