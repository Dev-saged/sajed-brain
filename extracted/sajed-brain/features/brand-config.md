# ميزة: BrandConfig.kt
_المصدر الوحيد لكل شيء له علاقة بالعلامة التجارية_

## القاعدة الصارمة
لا ألوان ولا أسماء brand ولا إعدادات خارج هذا الملف. بيع لعميل جديد = تعديل BrandConfig فقط.

## الهيكل الكامل
```kotlin
object BrandConfig {
    // Brand identity
    const val APP_NAME = "اسم التطبيق"
    const val APP_NAME_EN = "AppName"
    
    // OKLCH Palette — light + dark
    object Colors {
        // Primary
        val primaryLight = Color(oklch(0.55f, 0.18f, 250f))
        val primaryDark  = Color(oklch(0.70f, 0.18f, 250f))
        // Surface, Accent, Semantic...
    }
    
    // Typography
    val arabicFont = FontFamily(/* Readex Pro / Alexandria / Almarai / ... */)
    val latinFont  = FontFamily(/* matching Latin pair */)
    
    // Modules enabled per client
    object Modules {
        const val DEBTS       = true
        const val PLAYSTATION = true
        const val ELECTRICITY = false
        const val MESSAGES    = true
    }
    
    // Firebase (public config — Security Rules هي الحماية الحقيقية)
    object Firebase {
        const val PROJECT_ID    = "..."
        const val API_KEY       = "..."
        // ...
    }
    
    // License
    val licenseExpiry: LocalDate = LocalDate.of(2027, 1, 1)
    
    // Material You — opt-in فقط
    const val USE_DYNAMIC_COLOR = false
    
    // Auto-update
    const val GITHUB_OWNER = "Dev-saged"
    const val GITHUB_REPO  = "app-name"
}
```

## القاعدة في الـTheme
```kotlin
@Composable
fun AppTheme(content: @Composable () -> Unit) {
    val colorScheme = if (BrandConfig.USE_DYNAMIC_COLOR && Build.VERSION.SDK_INT >= 31) {
        dynamicColorScheme(LocalContext.current, darkTheme)
    } else {
        lightColorScheme(primary = BrandConfig.Colors.primaryLight, ...)
    }
    MaterialTheme(colorScheme = colorScheme, ...) { content() }
}
```
