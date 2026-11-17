# ميزة: Schema-Driven Architecture
_كل وحدة = schema object، engine واحد يرسم كل شيء_

## المبدأ
بدلاً من Composable مخصص لكل وحدة:
- وحدة جديدة = schema object فقط (~10 سطور)
- Generic engine يرسم form/list/filter/detail/KPI من أي schema
- custom screens فقط عبر named hooks

## هيكل الـSchema
```kotlin
data class ModuleSchema(
    val name: String,
    val icon: ImageVector,
    val fields: List<FieldDef>,
    val listColumns: List<ColumnDef>,
    val filters: List<FilterDef>,
    val kpiCards: List<KpiDef>,
    val permissions: Set<Role>,
    val hooks: ModuleHooks = ModuleHooks()
)

data class FieldDef(
    val key: String,
    val label: String,
    val type: FieldType, // TEXT, NUMBER, DATE, AMOUNT, SELECT, BOOLEAN
    val required: Boolean = false,
    val options: List<String> = emptyList()
)
```

## مثال: وحدة ديون
```kotlin
val DebtsSchema = ModuleSchema(
    name = "الديون",
    icon = Icons.Debt,
    fields = listOf(
        FieldDef("personName", "اسم الشخص", FieldType.TEXT, required = true),
        FieldDef("amount", "المبلغ", FieldType.AMOUNT, required = true),
        FieldDef("dueDate", "تاريخ الاستحقاق", FieldType.DATE),
        FieldDef("direction", "نوع", FieldType.SELECT, options = listOf("لي", "علي"))
    ),
    listColumns = listOf(ColumnDef("personName"), ColumnDef("amount"), ColumnDef("dueDate")),
    kpiCards = listOf(KpiDef("totalOwed", "إجمالي المديونية", KpiType.SUM, field = "amount"))
)
```

## الـEngine (Composable)
```kotlin
@Composable
fun SchemaScreen(schema: ModuleSchema, viewModel: SchemaViewModel) {
    // يرسم list/form/filter/KPI تلقائياً من schema
    // hooks للـcustom behavior
}
```
