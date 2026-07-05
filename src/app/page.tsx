import { Hero } from "@/components/sections/hero";
import {
  AboutPreview,
  BestSellers,
  FeaturedCoffee,
  GalleryPreview,
  InstagramFeed,
  Offers,
  Reviews,
  Stats,
  WhyChooseUs,
} from "@/components/sections/home";
import { NewsletterCTA } from "@/components/sections/newsletter-cta";

export default function HomePage() {
  return (
    <>
      <Hero />
      <FeaturedCoffee />
      <BestSellers />
      <Reviews />
      <AboutPreview />
      <Stats />
      <Offers />
      <WhyChooseUs />
      <GalleryPreview />
      <InstagramFeed />
      <NewsletterCTA />
    </>
  );
}
