package com.example.expensetracker.data

import androidx.room.Entity
import androidx.room.PrimaryKey

/**
 * A single money transaction. Despite the app name, this models both income
 * and expenses (distinguished by [type]) so a running balance can be shown.
 */
@Entity(tableName = "expenses")
data class Expense(
    @PrimaryKey(autoGenerate = true)
    val id: Long = 0,
    val title: String,
    val amount: Double,
    val category: Category,
    val type: TransactionType,
    /** Transaction date as epoch milliseconds. */
    val date: Long = System.currentTimeMillis(),
    val note: String = ""
) {
    /** Amount signed by type: positive for income, negative for expense. */
    val signedAmount: Double
        get() = if (type == TransactionType.INCOME) amount else -amount
}
