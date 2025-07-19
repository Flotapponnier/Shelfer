"""
Test script for HtmlExtractorService

This demonstrates how to use the HTML extractor to process product HTML
and extract schema.org properties using GPT-4o-mini.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.html_extractor import HtmlExtractorService
from schemas.product import ScraperInput, ProductImages

def test_html_extraction():
    """
    Test the HtmlExtractorService with comprehensive sample product HTML
    """
    print("📄 HTML Extractor Service Test")
    print("=" * 50)
    
    # Initialize the service
    extractor = HtmlExtractorService()
    
    # Show supported properties
    properties = extractor.get_target_properties()
    print(f"📋 Target properties ({len(properties)}):")
    for prop in properties:
        description = extractor.get_property_description(prop)
        print(f"  - {prop}: {description}")
    
    print("\n" + "=" * 50)
    print("🧪 Testing with comprehensive product HTML...")
    print("📝 HTML: Rich product page with multiple data points")
    
    # Comprehensive sample HTML with various product information
    sample_html = """
    <div class="product-page">
        <header class="product-header">
            <h1 class="product-title">Premium Wireless Bluetooth Headphones</h1>
            <div class="brand-info">
                <span class="brand-name">Sony</span>
                <span class="manufacturer">Manufactured by Sony Electronics Inc.</span>
            </div>
        </header>
        
        <div class="pricing-section">
            <div class="price-container">
                <span class="current-price">$299.99</span>
                <span class="original-price">$399.99</span>
                <span class="currency">USD</span>
                <div class="discount">25% OFF</div>
            </div>
            <div class="availability-status">
                <span class="stock-status">In Stock</span>
                <span class="quantity">15 units available</span>
            </div>
            <div class="condition-info">
                <span class="item-condition">Brand New</span>
                <span class="warranty">2-year manufacturer warranty</span>
            </div>
        </div>
        
        <div class="product-description">
            <h2>Product Description</h2>
            <p>Experience superior sound quality with these premium wireless Bluetooth headphones. 
            Featuring advanced noise cancellation technology, 30-hour battery life, and premium 
            comfort padding. Perfect for music enthusiasts, commuters, and professionals.</p>
            
            <h3>Key Features:</h3>
            <ul>
                <li>Active Noise Cancellation (ANC)</li>
                <li>30-hour battery life with quick charge</li>
                <li>Premium leather and metal construction</li>
                <li>Bluetooth 5.0 connectivity</li>
                <li>Built-in microphone for calls</li>
            </ul>
        </div>
        
        <div class="product-details">
            <h3>Product Specifications</h3>
            <div class="specs">
                <div class="spec-item">
                    <span class="spec-label">Color:</span>
                    <span class="spec-value">Midnight Black</span>
                </div>
                <div class="spec-item">
                    <span class="spec-label">Material:</span>
                    <span class="spec-value">Premium leather headband with metal frame</span>
                </div>
                <div class="spec-item">
                    <span class="spec-label">Size:</span>
                    <span class="spec-value">Over-ear, adjustable (fits head sizes 54-62cm)</span>
                </div>
                <div class="spec-item">
                    <span class="spec-label">Category:</span>
                    <span class="spec-value">Audio Equipment > Headphones > Wireless Headphones</span>
                </div>
                <div class="spec-item">
                    <span class="spec-label">Target Audience:</span>
                    <span class="spec-value">Adults, Music professionals, Audiophiles</span>
                </div>
            </div>
        </div>
        
        <div class="reviews-section">
            <h3>Customer Reviews</h3>
            <div class="rating-summary">
                <div class="overall-rating">
                    <span class="rating-score">4.7</span>
                    <span class="rating-scale">out of 5 stars</span>
                    <span class="review-count">(1,234 reviews)</span>
                </div>
            </div>
            
            <div class="review-highlights">
                <div class="positive-reviews">
                    <h4>What customers love:</h4>
                    <ul>
                        <li>"Exceptional sound quality and comfortable fit"</li>
                        <li>"Great battery life, lasts all day"</li>
                        <li>"Premium build quality worth the price"</li>
                        <li>"Excellent noise cancellation for travel"</li>
                    </ul>
                </div>
                
                <div class="negative-reviews">
                    <h4>Areas for improvement:</h4>
                    <ul>
                        <li>"Could be lighter for extended use"</li>
                        <li>"App could be more intuitive"</li>
                    </ul>
                </div>
            </div>
            
            <div class="recent-review">
                <div class="reviewer">John D. - Verified Purchase</div>
                <div class="review-rating">5 stars</div>
                <div class="review-text">"Amazing headphones! The sound quality is incredible and they're 
                very comfortable for long listening sessions. The noise cancellation works perfectly 
                on flights. Highly recommended for audiophiles."</div>
            </div>
        </div>
        
        <div class="additional-info">
            <div class="product-tags">
                <span class="tag">wireless</span>
                <span class="tag">bluetooth</span>
                <span class="tag">noise-cancelling</span>
                <span class="tag">premium</span>
                <span class="tag">audiophile</span>
                <span class="tag">travel</span>
            </div>
            
            <div class="return-policy">
                <h4>Return Policy</h4>
                <p>30-day money-back guarantee. Free returns and exchanges. 
                Original packaging required for returns.</p>
            </div>
            
            <div class="origin-info">
                <span class="made-in">Made in Japan</span>
                <span class="processing-location">Final assembly in Tokyo, Japan</span>
            </div>
            
            <div class="safety-info">
                <span class="family-friendly">Suitable for all ages</span>
                <span class="safety-rating">Family-friendly product</span>
            </div>
            
            <div class="product-codes">
                <span class="sku">SKU: WH-1000XM5-B</span>
                <span class="model">Model: WH-1000XM5</span>
            </div>
        </div>
    </div>
    """
    
    # Sample input with comprehensive HTML
    sample_input = ScraperInput(
        product_html=sample_html,
        images=ProductImages(
            url_main_image="https://example.com/headphones-main.jpg",  # Not processed by HTML extractor
            other_main_images=["https://example.com/headphones-alt.jpg"]
        ),
        json_ld_schema={"@type": "Product", "name": "Premium Wireless Bluetooth Headphones"}
    )
    
    try:
        print(f"\n🔄 Processing HTML content ({len(sample_html)} characters)")
        
        # Extract properties from the HTML
        result = extractor.extract_html_contexts(sample_input)
        
        print("✅ HTML extraction completed!")
        print(f"📊 Properties processed: {len(result.html_contexts)}")
        print(f"📋 JSON-LD schema forwarded: {result.json_ld_schema is not None}")
        
        # Show results with more detail
        successful_extractions = 0
        print("\n" + "=" * 50)
        print("📋 EXTRACTION RESULTS:")
        print("=" * 50)
        
        for property_name, context in result.html_contexts.items():
            if context.relevant_html_product_context.strip():
                successful_extractions += 1
                print(f"\n✅ {property_name.upper()}:")
                content = context.relevant_html_product_context.strip()
                # Truncate very long content for display
                if len(content) > 200:
                    preview = content[:200] + "..."
                else:
                    preview = content
                print(f"   📝 {preview}")
            else:
                print(f"\n❌ {property_name}: No data extracted")
        
        print("\n" + "=" * 50)
        print(f"📈 SUCCESS RATE: {successful_extractions}/{len(result.html_contexts)} properties ({successful_extractions/len(result.html_contexts)*100:.1f}%)")
        
        if successful_extractions > 0:
            print("🎉 Successfully extracted properties from HTML content!")
            print("🔍 The GPT-4o-mini model was able to analyze the product HTML.")
            
            # Show some key extractions
            key_properties = ["offers.price", "brand", "description", "color", "aggregateRating"]
            print("\n🎯 Key extractions preview:")
            for prop in key_properties:
                if prop in result.html_contexts and result.html_contexts[prop].relevant_html_product_context.strip():
                    content = result.html_contexts[prop].relevant_html_product_context.strip()
                    preview = content[:100] + "..." if len(content) > 100 else content
                    print(f"   • {prop}: {preview}")
        else:
            print("⚠️  No properties were extracted. This could be due to:")
            print("   - OpenAI API configuration issues")
            print("   - Network connectivity problems")
            print("   - Model processing errors")
        
    except Exception as e:
        print(f"❌ Error during extraction: {str(e)}")
        print("\n🔧 Troubleshooting:")
        print("   1. Check your OpenAI API key is set in environment variables")
        print("   2. Ensure you have internet connectivity")
        print("   3. Verify the HTML content is properly formatted")

if __name__ == "__main__":
    test_html_extraction() 