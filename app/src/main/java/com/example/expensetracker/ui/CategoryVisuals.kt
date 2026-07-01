package com.example.expensetracker.ui

import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.CardGiftcard
import androidx.compose.material.icons.filled.DirectionsCar
import androidx.compose.material.icons.filled.Fastfood
import androidx.compose.material.icons.filled.Flight
import androidx.compose.material.icons.filled.LocalHospital
import androidx.compose.material.icons.filled.Payments
import androidx.compose.material.icons.filled.Receipt
import androidx.compose.material.icons.filled.School
import androidx.compose.material.icons.filled.ShoppingBag
import androidx.compose.material.icons.filled.ShoppingCart
import androidx.compose.material.icons.filled.SportsEsports
import androidx.compose.material.icons.filled.MoreHoriz
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.vector.ImageVector
import com.example.expensetracker.data.Category

/** Presentation-only mapping of a [Category] to an icon and accent color. */
data class CategoryVisuals(val icon: ImageVector, val color: Color)

fun Category.visuals(): CategoryVisuals = when (this) {
    Category.FOOD -> CategoryVisuals(Icons.Filled.Fastfood, Color(0xFFEF6C00))
    Category.GROCERIES -> CategoryVisuals(Icons.Filled.ShoppingCart, Color(0xFF558B2F))
    Category.TRANSPORT -> CategoryVisuals(Icons.Filled.DirectionsCar, Color(0xFF1565C0))
    Category.SHOPPING -> CategoryVisuals(Icons.Filled.ShoppingBag, Color(0xFFAD1457))
    Category.BILLS -> CategoryVisuals(Icons.Filled.Receipt, Color(0xFF6A1B9A))
    Category.ENTERTAINMENT -> CategoryVisuals(Icons.Filled.SportsEsports, Color(0xFF00838F))
    Category.HEALTH -> CategoryVisuals(Icons.Filled.LocalHospital, Color(0xFFC62828))
    Category.TRAVEL -> CategoryVisuals(Icons.Filled.Flight, Color(0xFF00695C))
    Category.EDUCATION -> CategoryVisuals(Icons.Filled.School, Color(0xFF4527A0))
    Category.SALARY -> CategoryVisuals(Icons.Filled.Payments, Color(0xFF2E7D32))
    Category.GIFTS -> CategoryVisuals(Icons.Filled.CardGiftcard, Color(0xFFD81B60))
    Category.OTHER -> CategoryVisuals(Icons.Filled.MoreHoriz, Color(0xFF546E7A))
}
