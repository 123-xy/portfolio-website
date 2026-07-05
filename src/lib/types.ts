export type Category =
  | "Hot Coffee"
  | "Cold Coffee"
  | "Espresso"
  | "Cappuccino"
  | "Latte"
  | "Mocha"
  | "Tea"
  | "Smoothies"
  | "Mocktails"
  | "Sandwiches"
  | "Burgers"
  | "Pizza"
  | "Pasta"
  | "Desserts"
  | "Cakes"
  | "Ice Cream"
  | "Breakfast"
  | "Snacks";

export interface MenuItem {
  id: string;
  name: string;
  description: string;
  ingredients: string[];
  price: number;
  calories: number;
  rating: number;
  category: Category;
  image: string;
  veg: boolean;
  bestseller?: boolean;
  featured?: boolean;
}

export interface CartItem extends MenuItem {
  quantity: number;
}
