import { Product } from "schema-dts"

export const originalProduct: Product = {
  "@type": "Product",
  name: "Wireless Bluetooth Headphones",
  description: "High-quality wireless headphones with noise cancellation",
  brand: { "@type": "Brand", name: "TechSound" },
  category: "Electronics",
  offers: {
    "@type": "Offer",
    price: 79.99,
    priceCurrency: "USD",
    availability: "https://schema.org/InStock",
    inventoryLevel: { "@type": "QuantitativeValue", value: 45 }
  },
  keywords: "wireless, bluetooth, headphones"
}

export const enrichedProduct: Product = {
  "@type": "Product",
  name: "Wireless Bluetooth Headphones",
  description: "High-quality wireless headphones with noise cancellation. Premium wireless Bluetooth headphones featuring advanced active noise cancellation technology, delivering crystal-clear audio with deep bass and crisp highs. Perfect for music lovers, commuters, and professionals.",
  brand: { "@type": "Brand", name: "TechSound" },
  manufacturer: { "@type": "Organization", name: "TechSound Electronics Inc." },
  model: "TSH-900X",
  sku: "TSH900X-BLK",
  gtin13: "1234567890123",
  color: "Black",
  material: "Aluminum, Synthetic Leather, Plastic",
  image: [
    "https://example.com/images/headphones-front.jpg",
    "https://example.com/images/headphones-side.jpg"
  ],
  weight: {
    "@type": "QuantitativeValue",
    value: 250,
    unitCode: "GRM"
  },
  height: {
    "@type": "QuantitativeValue",
    value: 20,
    unitCode: "CMT"
  },
  width: {
    "@type": "QuantitativeValue",
    value: 18,
    unitCode: "CMT"
  },
  depth: {
    "@type": "QuantitativeValue",
    value: 8,
    unitCode: "CMT"
  },
  releaseDate: "2023-09-15",
  category: "Electronics",
  offers: {
    "@type": "Offer",
    price: 79.99,
    priceCurrency: "USD",
    availability: "https://schema.org/InStock",
    inventoryLevel: { "@type": "QuantitativeValue", value: 45 }
  },
  aggregateRating: {
    "@type": "AggregateRating",
    ratingValue: 4.3,
    reviewCount: 1247
  },
  keywords: "wireless, bluetooth, headphones, noise-cancelling, premium, audio, over-ear, lightweight, comfortable"
}
