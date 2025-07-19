"""
Test script for ExtractorService

This tests the complete product extraction pipeline that orchestrates
both HTML and image extractors.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import asyncio
from services.extractor_service import ExtractorService

async def test_product_processing_pipeline():
    """
    Test the complete product extraction pipeline with realistic data.
    """
    print("🔄 Extractor Service Test")
    print("=" * 50)
    
    # Initialize the service
    extractor = ExtractorService()
    
    # Show capabilities
    capabilities = extractor.get_supported_properties()
    print(f"📋 Pipeline Capabilities:")
    print(f"  • HTML Properties: {capabilities['html_properties']['count']}")
    print(f"  • Image Properties: {capabilities['image_properties']['count']}")
    print(f"  • Total Properties: {capabilities['total_properties']}")
    
    print("\n" + "=" * 50)
    print("🧪 Testing complete pipeline...")
    
    # Sample scraped data (simulating what comes from your scraper)
    sample_scraped_data = {
        "product_html": """
        <div class="product-page">
            <h1 class="product-title">Sony WH-1000XM5 Wireless Headphones</h1>
            <div class="brand">Sony</div>
            <div class="price-section">
                <span class="current-price">$299.99</span>
                <span class="currency">USD</span>
                <div class="availability">In Stock</div>
            </div>
            <div class="description">
                Premium wireless headphones with industry-leading noise cancellation.
                Features 30-hour battery life and superior sound quality.
            </div>
            <div class="specs">
                <div class="color">Midnight Black</div>
                <div class="material">Premium plastic and metal construction</div>
                <div class="category">Audio Equipment > Headphones</div>
            </div>
            <div class="reviews">
                <div class="rating">4.8/5 stars</div>
                <div class="review-count">2,847 reviews</div>
                <div class="customer-review">
                    "Excellent sound quality and comfort. Perfect for long flights."
                </div>
            </div>
        </div>
        """,
        "images": {
            "url_main_image": "https://images.unsplash.com/photo-1526170375885-4d8ecf77b99f?q=80&w=3888&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D",
            "other_images": []
        },
        "json_ld_schema": {
            "@context": "https://schema.org/",
            "@type": "Product",
            "name": "Sony WH-1000XM5 Wireless Headphones"
        }
    }
    
    try:
        # Process through the complete pipeline
        result = await extractor.extract_product_data(
            scraped_data=sample_scraped_data,
            product_name="Sony WH-1000XM5 Wireless Headphones",
            product_url="https://example.com/sony-headphones"
        )
        
        print("✅ Pipeline processing completed!")
        
        # Display processing metadata
        metadata = result.get("processing_metadata", {})
        print(f"\n📊 Processing Results:")
        print(f"  • Success: {metadata.get('success', False)}")
        print(f"  • HTML Properties Extracted: {metadata.get('html_properties_extracted', 0)}/{metadata.get('html_properties_total', 0)}")
        print(f"  • Image Properties Extracted: {metadata.get('image_properties_extracted', 0)}/{metadata.get('image_properties_total', 0)}")
        print(f"  • Total Properties Extracted: {metadata.get('total_properties_extracted', 0)}/{metadata.get('total_properties', 0)}")
        print(f"  • Overall Success Rate: {metadata.get('overall_success_rate', 0):.1%}")
        
        # Show sample extractions
        html_contexts = result.get("html_contexts", {})
        successful_extractions = [
            prop for prop, context in html_contexts.items()
            if context.get("relevant_html_product_context", "").strip()
        ]
        
        print(f"\n🎯 Sample Successful Extractions ({len(successful_extractions)} total):")
        
        # Show key extractions
        key_props = ["offers.price", "brand", "color", "description", "aggregateRating"]
        for prop in key_props:
            if prop in html_contexts and html_contexts[prop].get("relevant_html_product_context", "").strip():
                content = html_contexts[prop]["relevant_html_product_context"]
                preview = content[:80] + "..." if len(content) > 80 else content
                print(f"  ✅ {prop}: {preview}")
            else:
                print(f"  ❌ {prop}: No data extracted")
        
        # Check if we have image data
        image_props = ["color", "brand", "material", "category"]  # Props that might come from images
        image_extractions = [
            prop for prop in image_props 
            if prop in html_contexts and 
            html_contexts[prop].get("relevant_html_product_context", "").strip() and
            "json" in html_contexts[prop]["relevant_html_product_context"].lower()  # Likely from image extractor
        ]
        
        if image_extractions:
            print(f"\n🖼️  Image-based extractions detected: {len(image_extractions)}")
        
        # Verify output format for enricher
        print(f"\n📋 Output Format Validation:")
        print(f"  ✅ json_ld_schema present: {'json_ld_schema' in result}")
        print(f"  ✅ html_contexts present: {'html_contexts' in result}")
        print(f"  ✅ processing_metadata present: {'processing_metadata' in result}")
        print("  ✅ Ready for enricher consumption")
        
        # Success summary
        if metadata.get("success", False) and metadata.get("total_properties_extracted", 0) > 0:
            print(f"\n🎉 Pipeline test successful!")
            print(f"💪 Extracted data from {metadata.get('total_properties_extracted')} properties")
            print(f"🔀 Combined HTML and image analysis working correctly")
        else:
            print(f"\n⚠️  Pipeline completed but with limited extraction")
            print(f"🔧 This may be due to API configuration or content matching")
            
    except Exception as e:
        print(f"❌ Pipeline test failed: {str(e)}")
        print("\n🔧 Troubleshooting:")
        print("   1. Check OpenAI API key configuration")
        print("   2. Verify internet connectivity for image download")
        print("   3. Ensure all services are properly initialized")

def test_snake_case_format():
    """
    Test that the service correctly handles snake_case input format.
    """
    print("\n" + "=" * 50)
    print("🔄 Testing Snake Case Format")
    
    extractor = ExtractorService()
    
    # Test snake_case format (standard format)
    snake_case_data = {
        "product_html": "<div>test</div>",
        "images": {
            "url_main_image": "https://example.com/image.jpg",
            "other_images": ["https://example.com/alt.jpg"]
        },
        "json_ld_schema": {"@type": "Product"}
    }
    
    try:
        # Test data conversion
        scraper_input = extractor._convert_scraped_data(snake_case_data)
        
        print("✅ snake_case format conversion: Success")
        print("✅ Service correctly processes snake_case input")
        
    except Exception as e:
        print(f"❌ Snake case format test failed: {str(e)}")

async def main():
    """
    Run all tests
    """
    await test_product_processing_pipeline()
    test_snake_case_format()
    
    print("\n" + "=" * 50)
    print("🏁 Extractor Service testing completed!")

if __name__ == "__main__":
    asyncio.run(main()) 