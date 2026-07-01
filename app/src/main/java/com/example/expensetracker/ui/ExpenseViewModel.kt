package com.example.expensetracker.ui

import androidx.lifecycle.ViewModel
import androidx.lifecycle.ViewModelProvider
import androidx.lifecycle.viewModelScope
import androidx.lifecycle.viewmodel.viewModelFactory
import androidx.lifecycle.ViewModelProvider.AndroidViewModelFactory.Companion.APPLICATION_KEY
import com.example.expensetracker.ExpenseTrackerApplication
import com.example.expensetracker.data.Category
import com.example.expensetracker.data.Expense
import com.example.expensetracker.data.ExpenseRepository
import com.example.expensetracker.data.TransactionType
import kotlinx.coroutines.flow.SharingStarted
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.combine
import kotlinx.coroutines.flow.stateIn
import kotlinx.coroutines.launch

/** Immutable snapshot of everything the Home screen needs to render. */
data class HomeUiState(
    val balance: Double = 0.0,
    val totalIncome: Double = 0.0,
    val totalExpense: Double = 0.0,
    /** Transactions grouped by day (epoch millis at start of day), newest first. */
    val groupedTransactions: List<DayGroup> = emptyList(),
    val isLoading: Boolean = true
)

data class DayGroup(
    val dateMillis: Long,
    val transactions: List<Expense>
)

class ExpenseViewModel(private val repository: ExpenseRepository) : ViewModel() {

    val uiState: StateFlow<HomeUiState> = combine(
        repository.allExpenses,
        repository.totalIncome,
        repository.totalExpense
    ) { expenses, income, expense ->
        HomeUiState(
            balance = income - expense,
            totalIncome = income,
            totalExpense = expense,
            groupedTransactions = expenses.groupByDay(),
            isLoading = false
        )
    }.stateIn(
        scope = viewModelScope,
        started = SharingStarted.WhileSubscribed(5_000),
        initialValue = HomeUiState()
    )

    fun addTransaction(
        title: String,
        amount: Double,
        category: Category,
        type: TransactionType,
        date: Long,
        note: String
    ) = viewModelScope.launch {
        repository.upsert(
            Expense(
                title = title.trim(),
                amount = amount,
                category = category,
                type = type,
                date = date,
                note = note.trim()
            )
        )
    }

    fun updateTransaction(expense: Expense) = viewModelScope.launch {
        repository.upsert(expense)
    }

    fun deleteTransaction(expense: Expense) = viewModelScope.launch {
        repository.delete(expense)
    }

    suspend fun getTransaction(id: Long): Expense? = repository.getExpenseById(id)

    companion object {
        val Factory: ViewModelProvider.Factory = viewModelFactory {
            initializer {
                val app = (this[APPLICATION_KEY] as ExpenseTrackerApplication)
                ExpenseViewModel(app.repository)
            }
        }
    }
}

/** Groups a date-sorted list of transactions into per-day buckets. */
private fun List<Expense>.groupByDay(): List<DayGroup> {
    return this.groupBy { startOfDay(it.date) }
        .map { (day, items) -> DayGroup(day, items) }
        .sortedByDescending { it.dateMillis }
}

private fun startOfDay(epochMillis: Long): Long {
    val cal = java.util.Calendar.getInstance()
    cal.timeInMillis = epochMillis
    cal.set(java.util.Calendar.HOUR_OF_DAY, 0)
    cal.set(java.util.Calendar.MINUTE, 0)
    cal.set(java.util.Calendar.SECOND, 0)
    cal.set(java.util.Calendar.MILLISECOND, 0)
    return cal.timeInMillis
}
