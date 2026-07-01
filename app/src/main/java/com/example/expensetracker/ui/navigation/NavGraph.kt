package com.example.expensetracker.ui.navigation

import androidx.compose.runtime.Composable
import androidx.navigation.NavType
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.rememberNavController
import androidx.navigation.navArgument
import com.example.expensetracker.ui.ExpenseViewModel
import com.example.expensetracker.ui.screens.AddEditScreen
import com.example.expensetracker.ui.screens.HomeScreen

private const val ROUTE_HOME = "home"
private const val ROUTE_ADD = "add_edit?id={id}"
private const val ARG_ID = "id"

@Composable
fun NavGraph(viewModel: ExpenseViewModel) {
    val navController = rememberNavController()

    NavHost(navController = navController, startDestination = ROUTE_HOME) {

        composable(ROUTE_HOME) {
            HomeScreen(
                viewModel = viewModel,
                onAddClick = { navController.navigate("add_edit?id=-1") },
                onTransactionClick = { id -> navController.navigate("add_edit?id=$id") }
            )
        }

        composable(
            route = ROUTE_ADD,
            arguments = listOf(
                navArgument(ARG_ID) {
                    type = NavType.LongType
                    defaultValue = -1L
                }
            )
        ) { backStackEntry ->
            val id = backStackEntry.arguments?.getLong(ARG_ID)
            AddEditScreen(
                viewModel = viewModel,
                editId = id,
                onNavigateBack = { navController.popBackStack() }
            )
        }
    }
}
