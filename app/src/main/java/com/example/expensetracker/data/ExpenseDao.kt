package com.example.expensetracker.data

import androidx.room.Dao
import androidx.room.Delete
import androidx.room.Insert
import androidx.room.OnConflictStrategy
import androidx.room.Query
import androidx.room.Update
import kotlinx.coroutines.flow.Flow

@Dao
interface ExpenseDao {

    @Query("SELECT * FROM expenses ORDER BY date DESC")
    fun getAllExpenses(): Flow<List<Expense>>

    @Query("SELECT * FROM expenses WHERE id = :id")
    suspend fun getExpenseById(id: Long): Expense?

    /** Total of all income transactions. Returns 0 when there are none. */
    @Query("SELECT COALESCE(SUM(amount), 0) FROM expenses WHERE type = 'INCOME'")
    fun getTotalIncome(): Flow<Double>

    /** Total of all expense transactions. Returns 0 when there are none. */
    @Query("SELECT COALESCE(SUM(amount), 0) FROM expenses WHERE type = 'EXPENSE'")
    fun getTotalExpense(): Flow<Double>

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insert(expense: Expense): Long

    @Update
    suspend fun update(expense: Expense)

    @Delete
    suspend fun delete(expense: Expense)

    @Query("DELETE FROM expenses")
    suspend fun deleteAll()
}
