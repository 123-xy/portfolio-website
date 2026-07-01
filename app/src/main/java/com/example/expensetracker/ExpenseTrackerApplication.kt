package com.example.expensetracker

import android.app.Application
import com.example.expensetracker.data.AppDatabase
import com.example.expensetracker.data.ExpenseRepository

/**
 * Application subclass that owns the database and repository so they live for
 * the whole process and can be reached from the ViewModel factory.
 */
class ExpenseTrackerApplication : Application() {
    val database: AppDatabase by lazy { AppDatabase.getInstance(this) }
    val repository: ExpenseRepository by lazy { ExpenseRepository(database.expenseDao()) }
}
