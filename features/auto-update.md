# ميزة: auto-update
_كل app Android لساجد تحتوي هذه الميزة_

## المنطق
1. عند فتح التطبيق (أو في الخلفية بـWorkManager)، اطلب GitHub Release API
2. قارن `versionCode` المحلي مع `versionCode` في الـRelease
3. إذا الـRelease أحدث → اعرض بانر RTL في الأعلى مع رابط التحميل
4. إذا فشل الطلب → تجاهل بصمت (try/catch، offline-first)

## مقارنة الإصدار (مهم)
- الوسم قد يكون `v5.6.0-b81`: قصّ ما بعد `-` واستخرج الأرقام بـregex ثم قارن عنصراً عنصراً (لا `Number()` مباشرة → NaN)
- الإصدار الواحد قد يُبنى أكثر من مرة: قارن أيضاً `BASE_CODE + build` مع `VERSION_CODE`
- نسخة الويب لها `APP_VERSION` و`version.json` يجب أن يطابقا إصدار التطبيق

## التنفيذ
```kotlin
// في BrandConfig.kt
const val GITHUB_OWNER = "Dev-saged"
const val GITHUB_REPO = "app-name"

// نقطة النهاية
"https://api.github.com/repos/$GITHUB_OWNER/$GITHUB_REPO/releases/tags/latest-build"
```

## بنية الـRelease
- tag: `latest-build` (يُحدَّث في كل push عبر build.yml)
- في body الـRelease: `versionCode=123`
- Claude يقرأ هذا الرقم ويقارنه بـ`BuildConfig.VERSION_CODE`

## البانر
- RTL، يظهر في أعلى الشاشة
- زر "تحديث" يفتح رابط الـAPK من assets الـRelease
- زر "إغلاق" يخفيه للجلسة الحالية (SessionState، لا SharedPreferences)

## workflow
```yaml
# في build.yml — ينشئ/يحدّث latest-build tag
- name: Update latest-build release
  run: |
    gh release delete latest-build --yes || true
    gh release create latest-build \
      app/build/outputs/apk/release/*.apk \
      --title "Latest Build" \
      --notes "versionCode=${{ env.VERSION_CODE }}"
```
