package com.example.expensetracker.data

import kotlinx.coroutines.flow.Flow

/** Single point of access to expense data for the rest of the app. */
class ExpenseRepository(private val dao: ExpenseDao) {

    val allExpenses: Flow<List<Expense>> = dao.getAllExpenses()
    val totalIncome: Flow<Double> = dao.getTotalIncome()
    val totalExpense: Flow<Double> = dao.getTotalExpense()

    suspend fun getExpenseById(id: Long): Expense? = dao.getExpenseById(id)

    suspend fun upsert(expense: Expense) {
        if (expense.id == 0L) dao.insert(expense) else dao.update(expense)
    }

    suspend fun delete(expense: Expense) = dao.delete(expense)

    suspend fun deleteAll() = dao.deleteAll()
}
