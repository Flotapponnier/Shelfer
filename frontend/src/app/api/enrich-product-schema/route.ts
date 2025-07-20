import { NextResponse } from 'next/server';
import { enrichedProduct, originalProduct } from '@/data/sample-products';

export async function POST(request: Request) {
  const body = await request.json();
  const { url } = body;

  // DEV_MODE: Return static sample data if enabled
  if (process.env.DEV_MODE === 'true') {
    return NextResponse.json({
      enrichedProductSchema: enrichedProduct,
      originalProductSchema: originalProduct,
    });
  }
  
    // Always throw on error, never return an error property in the response
  // Only return the success shape
  // The frontend will only receive the success shape if result is not empty
  // If an error occurs, the response will have a non-2xx status and the frontend will not set result
  try {
    // Call the backend enrich-product-schema endpoint with your scrapeProductContext function
    const response = await fetch('http://localhost:8000/enrich-product-schema', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ url }),
    });
    
    if (!response.ok) {
      throw new Error(`Backend error: ${response.status}`);
    }

    const data = await response.json();
    return NextResponse.json({enrichedProductSchema: data.enriched_product_schema, originalProductSchema: data.original_product_schema});
  } catch (error) {
    console.error('Error calling scraper:', error);
    // Throw to ensure only the success shape is ever returned
    throw error;
  }
} 