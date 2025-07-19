import { NextResponse } from 'next/server';

export async function POST(request: Request) {
  const body = await request.json();
  const { url } = body;
  
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
    return NextResponse.json(data);
  } catch (error) {
    console.error('Error calling scraper:', error);
    return NextResponse.json(
      { error: 'Failed to scrape product data' },
      { status: 500 }
    );
  }
} 