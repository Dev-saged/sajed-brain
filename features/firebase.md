# ميزة: Firebase + Cloudflare

- فقط عند الحاجة لمزامنة بين أجهزة أو بيانات مشتركة؛ غير ذلك Room وحدها.
- Firestore بـoffline persistence؛ كل وثيقة تحمل `shopId`/`tenantId` + `updatedAt` (serverTimestamp).
- Security Rules هي الحماية الحقيقية: عزل المستأجر، الأدوار من custom claims أو وثيقة `members`، الميزات المدفوعة؛ فحوص العميل شكلية فقط.
- `google-services.json` عام بطبيعته — الحماية في القواعد، لا في إخفائه.
- عمليات الأدمن الحساسة (إنشاء مستأجر، منح دور، ترخيص) عبر Cloudflare Worker بمفتاح service account مخزن كسر في Worker.
- اختبر القواعد بالمحاكي قبل النشر؛ انشر بسكربت ثابت ثم smoke test.
- حدود: لا قراءة مجموعات كاملة من العميل؛ استعلامات مفهرسة بـ`limit`.
- مهارة `firebase-rules` عند كتابة القواعد.
