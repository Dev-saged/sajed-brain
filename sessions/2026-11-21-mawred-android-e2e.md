---
date: 2026-11-21
project: Morud
title: مورد — Android (M10–M12) وE2E على أربعة متصفحات (M13c)
status: in-progress
---

## الطلب
الاستمرار المتواصل في بناء «مورد» وحفظ واختبار ورفع كل مرحلة.

## ما نُفّذ
- M10 أساس Android (Kotlin + Compose + Hilt + Room): رموز OKLCH مولّدة من spec، خطوط Alexandria وIBM Plex Sans Arabic، أيقونات مطابقة للويب، أيقونة تكيفية من الشعار، دخول موحد عبر Identity Toolkit REST ورمز تحديث مشفّر بـ Keystore، توجيه بالدور، كتالوج بلا نت، مسودة سلة، محرك schema، #test، تحديث تلقائي، CI android.yml.
- M11 المحل: إرسال عبر outbox بمفتاح idempotency ثابت وWorkManager، موافقة تغيّر السعر، طلباتي مع مراحل ومؤقت SLA، كشف الحساب.
- M12 الإدارة والمندوب: لوحة الطلبات وإجراءاتها والإسناد، التوفر، تفريغ الصور على الجهاز بـ ML Kit ورفعها، التسليم بإثبات والتعذّر.
- M13c: Playwright على بناء الإنتاج الحقيقي — Chrome وجوال محلياً + Firefox وWebKit في CI؛ كشف خللين حقيقيين (شريط الإدارة على الجوال، نافذة تثبيت آيفون فوق زر الدخول) وأُصلحا.
- الأرقام: خادم 168، ويب 20 Vitest + 6 Playwright (12 في CI)، Android 24 JUnit. كل CI أخضر.

## القرارات
- D12: لا Firebase SDK على Android — REST + Keystore.
- D13: مشروع Android داخل المستودع الموحد بـ workflow مكيّف من android-template.
- Android للإدارة الميدانية السريعة؛ الإدارة الكاملة على الويب.

## الأخطاء والدروس
- في mistakes.md: Playwright وubuntu 26.04، نافذة التثبيت، تباين النص فوق البرتقالي، CORS في WebKit، jvmToolchain.

## التالي
- M14: FCM وWeb Push (يحتاج إعداد Firebase من ساجد: appId/projectId/senderId/VAPID)، أسرار توقيع Android ومتغيرات MAWRED_API_URL، تقرير الأمان، اختبار استعادة staging، أدلة الاستخدام، MFA للأدوار الحساسة، v1.0.0.
