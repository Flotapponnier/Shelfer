import { NextResponse } from 'next/server';
import { enrichedProduct } from '../../../../data/sample-products';

export async function POST(request: Request) {
  const body = await request.json();
  const { url } = body;
  // For now, we ignore the url and always return the dummy data
  return NextResponse.json(enrichedProduct);
} 