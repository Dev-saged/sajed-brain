# ميزة: Room + migrations

- قاعدة واحدة `AppDatabase` بـ`version` يزيد مع كل تغيير، WAL افتراضي.
- migrations مرقّمة append-only: `MIGRATION_1_2`، `MIGRATION_2_3`… لا تُعدَّل قديمة أبداً؛ خطأ قديم = migration جديدة.
- `exportSchema = true` ومجلد `schemas/` في git + اختبار `MigrationTestHelper` لكل migration.
- لا `fallbackToDestructiveMigration` في release.
- الأرصدة لا تُخزَّن: تُشتق من جدول حركات append-only؛ الحذف ناعم (`deletedAt`).
- كل جدول: `id` (UUID نصي للمزامنة)، `createdAt`، `updatedAt`، `deletedAt?`.
- DAO يرجع `Flow` للقراءة، `suspend` للكتابة؛ عمليات متعددة داخل `withTransaction`.
- نسخ احتياطي: تصدير كل الجداول JSON بإصدار المخطط، والاستيراد يمر عبر نفس الـmigrations.
