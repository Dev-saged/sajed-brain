# ميزة: إشعارات الرسائل المحلية (GRCS v5.8.0)

- `MsgNotifier.check`: يقرأ `sync/pulse` (m وg)، فإن تغيّر التوقيع يجلب أحدث الرسائل ويعرض إشعاراً لكل محادثة (InboxStyle للمتعدد + ملخص مجموعة)
- `MsgWorker` كل 15 دقيقة (حد WorkManager الأدنى) بقيد الشبكة؛ لا إشعار والتطبيق ظاهر (`Fg.on`)، أول تشغيل يضبط الخط الزمني دون إغراق
- نقر الإشعار → `EXTRA_CHAT` → `ShellState.openChat` يفتح تبويب الرسائل
- الصادر `Messages.Outbox` يُفرَّغ بعد كل `sync` وبـ`BackgroundJobs.kick` عند فشل الإرسال
- الفوري الحقيقي يحتاج FCM + Cloudflare Worker (لم يُعتمد بقرار ساجد)
