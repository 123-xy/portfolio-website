package com.example.expensetracker.data

/**
 * Spending / income categories. Stored in the database by [name] via a
 * Room TypeConverter, so renaming an entry would require a migration.
 */
enum class Category(val label: String) {
    FOOD("Food & Drink"),
    GROCERIES("Groceries"),
    TRANSPORT("Transport"),
    SHOPPING("Shopping"),
    BILLS("Bills & Utilities"),
    ENTERTAINMENT("Entertainment"),
    HEALTH("Health"),
    TRAVEL("Travel"),
    EDUCATION("Education"),
    SALARY("Salary"),
    GIFTS("Gifts"),
    OTHER("Other");

    companion object {
        /** Categories that make sense for income transactions. */
        val incomeCategories = listOf(SALARY, GIFTS, OTHER)

        /** Categories that make sense for expense transactions. */
        val expenseCategories = listOf(
            FOOD, GROCERIES, TRANSPORT, SHOPPING, BILLS,
            ENTERTAINMENT, HEALTH, TRAVEL, EDUCATION, OTHER
        )
    }
}
