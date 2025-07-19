"""
Test script for ImageExtractorService with real Unsplash image

This demonstrates the image extractor using a real product image from Unsplash
to extract schema.org properties using GPT-4o vision.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.image_extractor import ImageExtractorService
from schemas.product import ScraperInput, ProductImages

def test_image_extraction():
    """
    Test the ImageExtractorService with a real Unsplash product image
    """
    print("🖼️  Image Extractor Service Test")
    print("=" * 50)
    
    # Initialize the service
    extractor = ImageExtractorService()
    
    # Show supported properties
    properties = extractor.get_target_properties()
    print(f"📋 Target properties ({len(properties)}):")
    for prop in properties:
        description = extractor.get_property_description(prop)
        print(f"  - {prop}: {description}")
    
    print("\n" + "=" * 50)
    print("🧪 Testing with real Unsplash product image...")
    print("📷 Image: Product image from Unsplash")
    print("🔗 Source: https://unsplash.com (verified working URL)")
    
    # Use the working Unsplash image URL provided by the user
    # This URL has been verified to return valid JPEG image data
    image_url = "https://images.unsplash.com/photo-1526170375885-4d8ecf77b99f?q=80&w=3888&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D"
    
    # Sample input with real product image
    sample_input = ScraperInput(
        product_html="<h1>Product Image Test</h1>",  # Not used by image extractor
        images=ProductImages(
            url_main_image=image_url,
            other_main_images=[]  # Testing with just the main image
        ),
        json_ld_schema={"@type": "Product", "name": "Test Product"}
    )
    
    try:
        print(f"\n🔄 Processing image: {image_url}")
        
        # Extract properties from the real image
        result = extractor.extract_image_contexts(
            scraper_input=sample_input,
            product_name="Test Product",
            product_url="https://unsplash.com/test-product"
        )
        
        print("✅ Image extraction completed!")
        print(f"📊 Properties processed: {len(result)}")
        
        # Show results with more detail
        successful_extractions = 0
        print("\n" + "=" * 50)
        print("📋 EXTRACTION RESULTS:")
        print("=" * 50)
        
        for property_name, context in result.items():
            if context.relevant_html_product_context.strip():
                successful_extractions += 1
                print(f"\n✅ {property_name.upper()}:")
                content = context.relevant_html_product_context.strip()
                print(f"   📝 {content}")
            else:
                print(f"\n❌ {property_name}: No data extracted")
        
        print("\n" + "=" * 50)
        print(f"📈 SUCCESS RATE: {successful_extractions}/{len(result)} properties ({successful_extractions/len(result)*100:.1f}%)")
        
        if successful_extractions > 0:
            print("🎉 Successfully extracted visual properties from the image!")
            print("🔍 The GPT-4o vision model was able to analyze the product image.")
        else:
            print("⚠️  No properties were extracted. This could be due to:")
            print("   - Network issues downloading the image")
            print("   - OpenAI API configuration")
            print("   - The image content not matching expected product properties")
        
    except Exception as e:
        print(f"❌ Error during extraction: {str(e)}")
        print("\n🔧 Troubleshooting:")
        print("   1. Check your OpenAI API key is set in environment variables")
        print("   2. Ensure you have internet connectivity")
        print("   3. Verify the image URL is accessible")

if __name__ == "__main__":
    test_image_extraction() 