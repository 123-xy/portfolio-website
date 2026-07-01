package com.example.expensetracker.ui.components

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.material3.Icon
import androidx.compose.material3.ListItem
import androidx.compose.material3.ListItemDefaults
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import com.example.expensetracker.data.Expense
import com.example.expensetracker.data.TransactionType
import com.example.expensetracker.ui.formatSignedCurrency
import com.example.expensetracker.ui.theme.ExpenseRed
import com.example.expensetracker.ui.theme.IncomeGreen
import com.example.expensetracker.ui.visuals

/** A single transaction line: category icon, title/note, and signed amount. */
@Composable
fun TransactionRow(
    expense: Expense,
    modifier: Modifier = Modifier
) {
    val visuals = expense.category.visuals()
    val amountColor = if (expense.type == TransactionType.INCOME) IncomeGreen else ExpenseRed

    ListItem(
        modifier = modifier,
        colors = ListItemDefaults.colors(containerColor = MaterialTheme.colorScheme.surface),
        leadingContent = {
            Box(
                modifier = Modifier
                    .size(44.dp)
                    .clip(CircleShape)
                    .background(visuals.color.copy(alpha = 0.15f)),
                contentAlignment = Alignment.Center
            ) {
                Icon(
                    imageVector = visuals.icon,
                    contentDescription = expense.category.label,
                    tint = visuals.color,
                    modifier = Modifier.size(24.dp)
                )
            }
        },
        headlineContent = {
            Text(
                text = expense.title,
                style = MaterialTheme.typography.bodyLarge,
                fontWeight = FontWeight.Medium
            )
        },
        supportingContent = {
            val subtitle = expense.note.ifBlank { expense.category.label }
            Text(text = subtitle, style = MaterialTheme.typography.labelMedium)
        },
        trailingContent = {
            Text(
                text = formatSignedCurrency(expense.signedAmount),
                style = MaterialTheme.typography.bodyLarge,
                fontWeight = FontWeight.SemiBold,
                color = amountColor
            )
        }
    )
}
