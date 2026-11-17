# ميزة: CI/CD — GitHub Actions
_كل push → بناء + توقيع + نشر APK تلقائياً_

## Workflows الموجودة في كل مشروع
| الملف | الغرض |
|-------|-------|
| build.yml | بناء + توقيع + نشر APK على "latest-build" Release |
| unpack-zip.yml | فك zip مرفوع من الهاتف، نسخ الملفات، push → يُطلق build.yml |
| repomap.yml | توليد docs/code-index.md عند كل push |
| apply-to-all-repos.yml | توزيع unpack-zip.yml وrepomap.yml على كل repos (في android-template) |

## أسرار التوقيع المطلوبة في كل repo
```
KEYSTORE_BASE64         # keystore مشفّر base64
SIGNING_STORE_PASSWORD  # كلمة سر الـkeystore
SIGNING_KEY_ALIAS       # اسم الـkey
SIGNING_KEY_PASSWORD    # كلمة سر الـkey
GH_PAT                  # classic PAT (repo + workflow scopes) لـapply-to-all
```

## VERSION_NAME وVERSION_CODE
```properties
# gradle.properties
VERSION_NAME=1.0.0
BASE_VERSION_CODE=1000
```
```kotlin
// build.gradle.kts
versionCode = (System.getenv("GITHUB_RUN_NUMBER")?.toInt() ?: 0) + BASE_VERSION_CODE
versionName = VERSION_NAME
```

## رفع zip من الهاتف
- أضف `.github/workflows/unpack-zip.yml` → يقبل artifact اسمه "project-zip"
- ارفع الـzip عبر GitHub Actions UI أو gh CLI
- الـworkflow يفكّه، ينسخ الملفات، يعمل push → يُطلق build.yml تلقائياً
- **تحذير:** الـzip يجب أن يكون flat (بلا مجلد wrapper داخلي)
