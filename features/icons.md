# ميزة: Icons.kt

- ملف واحد `ui/icons/Icons.kt` فيه كل الأيقونات كـ`ImageVector` مبنية بـ`ImageVector.Builder` + `path { }`.
- عائلة واحدة: شبكة 24dp، سماكة خط واحدة (1.75–2dp)، `StrokeCap.Round` و`StrokeJoin.Round`، نفس نصف قطر الزوايا.
- الطقم كامل من أول دفعة: التنقل السفلي، الإجراءات (إضافة، تعديل، حذف، بحث، فلتر، مشاركة، طباعة، تصدير)، الحالات (نجاح، تحذير، خطأ، offline، مزامنة)، الشاشات الفارغة.
- الاتجاهية (رجوع، سهم، تالي) تنعكس في RTL: `Modifier.graphicsLayer { scaleX = if (rtl) -1f else 1f }` أو `autoMirror = true`.
- اللون من الثيم دائماً (`LocalContentColor`) لا ألوان مثبتة.
- أيقونة التطبيق adaptive: foreground + background + monochrome، مبنية من ناتج مهارة logo-design.
- لا icon packs، لا emoji، لا Material Icons الجاهزة.
