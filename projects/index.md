# فهرس المشاريع النشطة
_يُحدَّث عند بدء مشروع جديد أو تغيير حالة_

## مورد MAWRED — منصة توريد بالجملة
- **المستودع:** Dev-saged/Morud
- **Stack:** Kotlin + Compose (Android)، Cloudflare Worker TS + Firebase Auth/Firestore + R2 + FCM، React + TS PWA
- **الحالة:** نشط — M0 مغلقة (مواصفات + spec JSON + اختبارات)، التالي M1 نواة المنطق
- **آخر قرار:** لا كتابة من العميل إلى Firestore؛ كل كتابة عبر Worker. المرجع `Morud→docs/SRS` + انحرافات `Morud→docs/architecture`

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

## GRCS — منظومة مخيمات النزوح (Android الأصلي + نسخة ويب)
- **المستودع:** Dev-saged/wasla-system (الكود الأصلي في `android/`، نسخة الويب `index.html`)
- **Stack:** Kotlin + Compose، package `dev.saged.grcs`، Firestore عبر REST (`Fs`)، كاش SQLite (FamCache)، WorkManager
- **الإصدار:** v5.7.0 (feature/sync-export-brain)؛ الإصدارات تُنشر `vX.Y.Z-bN` من main عبر workflow_dispatch `publish=true`
- **المزامنة:** عدّادات `sync/pulse` (c/m/u/g)؛ الويب يستمع realtime، التطبيق يفحص النبض كل 45ث أثناء الفتح + عامل خلفية كل 6 ساعات
- **التصدير:** xlsx منسّق + كشف أفقي (صف لكل أسرة) + «أرباب فقط»، خدمة foreground بإشعار تقدّم، الحفظ `Documents/<BACKUP_DIR>/الكشوف`
- **مطابقة السجل الوطني:** قراءة تدفقية `NatStream` لملفات ضخمة (مرور واحد، فقط أرباب الأسر المسجّلين)
- **قرار:** الويب والتطبيق يتشاركان رقم الإصدار؛ تحديث الويب يتبع التطبيق
