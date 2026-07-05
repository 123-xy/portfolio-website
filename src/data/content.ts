const img = (id: string, w = 800) =>
  `https://images.unsplash.com/photo-${id}?auto=format&fit=crop&w=${w}&q=80`;

export const reviews = [
  {
    name: "Aarav Mehta",
    role: "Coffee Enthusiast",
    rating: 5,
    text: "Easily the best cold brew in the city. The ambience is warm and every cup feels crafted with care.",
    avatar: img("1500648767791-00dcc994a43e", 200),
  },
  {
    name: "Sofia Rodriguez",
    role: "Food Blogger",
    rating: 5,
    text: "The truffle mushroom pizza and Belgian mocha are a dream pairing. Premium Café sets the bar for luxury cafés.",
    avatar: img("1494790108377-be9c29b29330", 200),
  },
  {
    name: "Rohan Kapoor",
    role: "Regular Guest",
    rating: 5,
    text: "Reserved a table for our anniversary — impeccable service, gorgeous interiors and unforgettable desserts.",
    avatar: img("1506794778202-cad84cf45f1d", 200),
  },
  {
    name: "Emily Chen",
    role: "Remote Worker",
    rating: 4,
    text: "My favourite spot to work from. Fast wifi, endless refills and the friendliest baristas around.",
    avatar: img("1438761681033-6461ffad8d80", 200),
  },
];

export const stats = [
  { label: "Cups Served", value: "1.2M+" },
  { label: "Happy Guests", value: "85K+" },
  { label: "Signature Blends", value: "40+" },
  { label: "Years of Craft", value: "12" },
];

export const offers = [
  {
    title: "Weekday Morning Ritual",
    description: "20% off all hot coffees before 11 AM, Monday to Friday.",
    badge: "20% OFF",
    code: "MORNING20",
  },
  {
    title: "Sweet Pairing",
    description: "Any dessert free with two specialty beverages.",
    badge: "FREE DESSERT",
    code: "SWEETPAIR",
  },
  {
    title: "Loyalty Rewards",
    description: "Earn a point per ₹100 spent and redeem for free drinks.",
    badge: "REWARDS",
    code: "JOINCLUB",
  },
];

export const whyChooseUs = [
  {
    title: "Ethically Sourced",
    description: "Single-origin beans from partner farms with fair-trade practices.",
    icon: "Leaf",
  },
  {
    title: "Master Roasters",
    description: "Small-batch roasting perfected over 12 years of craft.",
    icon: "Flame",
  },
  {
    title: "Crafted to Order",
    description: "Every cup is hand-prepared by award-winning baristas.",
    icon: "Coffee",
  },
  {
    title: "Fast Delivery",
    description: "Piping hot orders delivered to your door in under 30 minutes.",
    icon: "Bike",
  },
];

export const galleryImages = [
  { src: img("1554118811-1e0d58224f24"), category: "Interior", alt: "Café interior" },
  { src: img("1445116572660-236099ec97a0"), category: "Food", alt: "Fresh pastries" },
  { src: img("1447933601403-0c6688de566e"), category: "Coffee", alt: "Latte art" },
  { src: img("1559496417-e7f25cb247f3"), category: "Interior", alt: "Cozy seating" },
  { src: img("1509042239860-f550ce710b93"), category: "Coffee", alt: "Coffee beans" },
  { src: img("1504674900247-0877df9cc836"), category: "Food", alt: "Gourmet plate" },
  { src: img("1521017432531-fbd92d768814"), category: "Events", alt: "Café event" },
  { src: img("1442512595331-e89e73853f31"), category: "Coffee", alt: "Pour over" },
  { src: img("1600093463592-8e36ae95ef56"), category: "Interior", alt: "Bar counter" },
];

export const team = [
  {
    name: "Isabella Rossi",
    role: "Founder & Head Roaster",
    bio: "A third-generation roaster who turned a family passion into Premium Café.",
    avatar: img("1544005313-94ddf0286df2", 400),
  },
  {
    name: "Marcus Bennett",
    role: "Executive Chef",
    bio: "Michelin-trained chef crafting our seasonal food menu.",
    avatar: img("1519085360753-af0119f7cbe7", 400),
  },
  {
    name: "Priya Sharma",
    role: "Master Barista",
    bio: "National latte-art champion leading our barista academy.",
    avatar: img("1531123897727-8f129e1688ce", 400),
  },
];

export const timeline = [
  { year: "2013", title: "The First Cup", text: "Premium Café opens as a tiny six-seat roastery." },
  { year: "2016", title: "Award-Winning", text: "Named Best Independent Café in the region." },
  { year: "2019", title: "Going Global", text: "Sourcing partnerships across four continents." },
  { year: "2023", title: "Digital First", text: "Launched online ordering, delivery and rewards." },
];

export const blogPosts = [
  {
    slug: "art-of-the-perfect-pour-over",
    title: "The Art of the Perfect Pour-Over",
    excerpt: "Master the ritual of pour-over coffee at home with our barista's step-by-step guide.",
    category: "Coffee Tips",
    date: "2026-06-18",
    image: img("1442512595331-e89e73853f31"),
    readTime: "6 min read",
  },
  {
    slug: "homemade-tiramisu-recipe",
    title: "Our Signature Tiramisu, Recreated at Home",
    excerpt: "The exact recipe behind our most-loved dessert, simplified for your kitchen.",
    category: "Recipes",
    date: "2026-06-02",
    image: img("1571877227200-a0d98ea607e9"),
    readTime: "8 min read",
  },
  {
    slug: "summer-menu-launch",
    title: "Introducing Our Summer Menu",
    excerpt: "Cooling cold brews, fruit-forward mocktails and light bites for the season.",
    category: "News",
    date: "2026-05-20",
    image: img("1461023058943-07fcbe16d735"),
    readTime: "4 min read",
  },
];

export const faqs = [
  {
    q: "Do you offer home delivery?",
    a: "Yes! We deliver within a 10 km radius in under 30 minutes. Choose delivery at checkout and track your order live.",
  },
  {
    q: "Can I reserve a table in advance?",
    a: "Absolutely. Use our reservation page to book a table for dine-in, including special requests for celebrations.",
  },
  {
    q: "Are there vegetarian and vegan options?",
    a: "Most of our menu is vegetarian, and every item is clearly labelled Veg or Non-Veg. Ask our staff for vegan swaps.",
  },
  {
    q: "How does the loyalty program work?",
    a: "Earn one point for every ₹100 you spend. Points can be redeemed for free drinks, desserts and exclusive offers.",
  },
];
