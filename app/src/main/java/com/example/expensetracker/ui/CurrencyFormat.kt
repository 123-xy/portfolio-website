package com.example.expensetracker.ui

import java.text.NumberFormat
import java.text.SimpleDateFormat
import java.util.Currency
import java.util.Date
import java.util.Locale

private val currencyFormat: NumberFormat = NumberFormat.getCurrencyInstance(Locale.US).apply {
    currency = Currency.getInstance("USD")
}

/** Formats a monetary amount, e.g. 1234.5 -> "$1,234.50". */
fun formatCurrency(amount: Double): String = currencyFormat.format(amount)

/** Formats a signed amount with an explicit leading +/-, e.g. "+$50.00". */
fun formatSignedCurrency(amount: Double): String {
    val sign = if (amount >= 0) "+" else "-"
    return sign + currencyFormat.format(kotlin.math.abs(amount))
}

private val dateFormat = SimpleDateFormat("MMM d, yyyy", Locale.getDefault())
private val dayHeaderFormat = SimpleDateFormat("EEEE, MMM d", Locale.getDefault())

fun formatDate(epochMillis: Long): String = dateFormat.format(Date(epochMillis))

fun formatDayHeader(epochMillis: Long): String = dayHeaderFormat.format(Date(epochMillis))
