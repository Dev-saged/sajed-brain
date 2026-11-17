# فهرس المشاريع النشطة
_يُحدَّث عند بدء مشروع جديد أو تغيير حالة_

## قيد — نظام إدارة متاجر
- **المستودع:** Dev-saged/qayd (خاص)
- **Stack:** Kotlin + Jetpack Compose، minSdk 26، Firebase Auth+Firestore (offline persistence)، Cloudflare Worker
- **الوحدات:** ديون، PlayStation sessions، كهرباء، رسائل SMS
- **الحالة:** نشط
- **آخر قرار:** Balance يُشتق من transactions append-only، لا يُخزَّن أبداً
- **خصوصية:** secrets/ يحتوي keystore + Firebase service account + Cloudflare token — المستودع خاص دائماً
- **PlayStation sessions:** يخزن timestamp مطلق لبداية الجلسة، الـUI يحسب المدة
- **Security Rules:** تفرض shopId isolation + roles + paid features، client checks cosmetic فقط

## SMS Barq — تطبيق رسائل SMS
- **المستودع:** Dev-saged/SMS-Barq (خاص)
- **Stack:** Kotlin + Jetpack Compose، minSdk 26
- **المحرك:** حزمة sms/ (SendEngine، SendQueue، SendDrainer، SendTracker، SendLimit، ScheduleManager، gateway/)
- **MMS:** حزمة mms/ مستقلة
- **الحالة:** نشط

## android-template — القالب الرئيسي
- **المستودع:** Dev-saged/android-template (خاص)
- **الغرض:** نقطة البداية لكل مشروع جديد عبر new-project.yml workflow
- **الـworkflows:** build.yml، unpack-zip.yml، repomap.yml، apply-to-all-repos.yml، new-project.yml
- **المتطلبات:** تفعيل "Template repository" في إعدادات GitHub، سر GH_PAT

## Sport Monitor AI — مراقبة رياضية
- **المستودع:** Dev-saged/sport-monitor-ai
- **Stack:** Python Flask (Termux)، Android WebView bridge (Java، compileSdk 34)
- **الحزم:** core/ (database.py، relay.py، arabic_matcher.py)، platforms/ (platform per module)
- **التخزين:** SQLite WAL، credentials مشفّرة بـFernet
- **الحالة:** نشط
