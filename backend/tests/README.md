# Tests Directory

This directory contains test scripts for the AI-powered schema.org product enrichment platform services.

## Available Tests

### `test_image_extractor.py`

Tests the **ImageExtractorService** which uses GPT-4o vision model to extract schema.org properties from product images.

### `test_html_extractor.py`

Tests the **HtmlExtractorService** which uses GPT-4o-mini to extract schema.org properties from product HTML content.

## Prerequisites

Before running the tests, ensure you have:

1. **Environment Setup**:
   ```bash
   cd backend
   uv sync  # Install dependencies
   ```

2. **OpenAI API Key**:
   - Set your OpenAI API key in environment variables
   - Create a `.env` file in the backend directory:
     ```
     OPENAI_API_KEY=your_openai_api_key_here
     ```

3. **Internet Connection**:
   - Tests download images from URLs, so internet access is required

## Running the Image Extractor Test

### Quick Start

```bash
cd backend
uv run python tests/test_image_extractor.py
```

### What It Tests

The test script validates the **ImageExtractorService** by:

- 🖼️ Downloading a real product image from Unsplash
- 🤖 Using GPT-4o vision model to analyze the image
- 📋 Extracting 10 visual schema.org properties
- ✅ Displaying detailed results and success metrics

### Test Image Used

**Image URL**: `https://images.unsplash.com/photo-1526170375885-4d8ecf77b99f?q=80&w=3888&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D`

**Image Description**: A Polaroid instant camera product image from Unsplash

## Expected Test Results

Here are the actual results from a successful test run:

### ✅ Test Output Example

```
🖼️  Image Extractor Service Test
==================================================
📋 Target properties (10):
  - image: The main product image URL and any additional product images visible
  - color: The color or colors of the product visible in the image
  - material: The material the product appears to be made from (fabric, metal, plastic, wood, etc.)
  - brand: Any brand names, logos, or brand identifiers visible in the image
  - offers.itemCondition: The apparent condition of the product (new, used, refurbished, etc.) based on visual appearance
  - category: The product category or type that can be determined from the image
  - size: Any size information visible in the image (labels, size comparisons, dimensions)
  - additionalType: Additional product type details that can be visually identified
  - positiveNotes: Positive visual aspects, quality indicators, or appealing features visible in the image
  - negativeNotes: Any negative aspects, damage, or quality issues visible in the image

==================================================
🧪 Testing with real Unsplash product image...
📷 Image: Product image from Unsplash
🔗 Source: https://unsplash.com (verified working URL)

🔄 Processing image: https://images.unsplash.com/photo-1526170375885-4d8ecf77b99f?q=80&w=3888&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D

✅ Image extraction completed!
📊 Properties processed: 10

==================================================
📋 EXTRACTION RESULTS:
==================================================

✅ IMAGE:
   📝 ```json
{
  "image": "https://images.unsplash.com/photo-1534723452862-4a27de6e4191"
}
```

✅ COLOR:
   📝 ```json
{"color": "white and black"}
```

✅ MATERIAL:
   📝 ```json
{"material": "plastic"}
```

✅ BRAND:
   📝 ```json
{"brand": "Polaroid"}
```

✅ OFFERS.ITEMCONDITION:
   📝 ```json
{"offers.itemCondition": "new"}
```

✅ CATEGORY:
   📝 ```json
{"category": "Instant Camera"}
```

✅ SIZE:
   📝 ```json
{"size": ""}
```

✅ ADDITIONALTYPE:
   📝 ```json
{"additionalType": "instant camera"}
```

✅ POSITIVENOTES:
   📝 ```json
{
  "positiveNotes": "Stylish retro design, clear branding, compact size, and visible flash feature."
}
```

✅ NEGATIVENOTES:
   📝 ```json
{"negativeNotes": ""}
```

==================================================
📈 SUCCESS RATE: 10/10 properties (100.0%)
🎉 Successfully extracted visual properties from the image!
🔍 The GPT-4o vision model was able to analyze the product image.
```

### 🎯 Key Success Metrics

- **Success Rate**: 100% (10/10 properties extracted)
- **Brand Detection**: ✅ Correctly identified "Polaroid"
- **Color Analysis**: ✅ Accurate "white and black"
- **Category Classification**: ✅ Proper "Instant Camera" categorization
- **Material Recognition**: ✅ Identified "plastic" material
- **Condition Assessment**: ✅ Determined "new" condition
- **Quality Analysis**: ✅ Detailed positive notes about design features

## Running the HTML Extractor Test

### Quick Start

```bash
cd backend
uv run python tests/test_html_extractor.py
```

### What It Tests

The test script validates the **HtmlExtractorService** by:

- 📄 Processing comprehensive product HTML content
- 🤖 Using GPT-4o-mini model to analyze HTML structure
- 📋 Extracting 22 text-based schema.org properties
- ✅ Displaying detailed results and success metrics

### Test Data Used

**HTML Content**: Comprehensive product page HTML (6,203 characters) including:
- Product pricing and availability information
- Detailed product descriptions and features
- Customer reviews and ratings
- Product specifications (color, material, size)
- Return policies and shipping information
- Product categories and target audience data

**Product Example**: Premium Wireless Bluetooth Headphones (Sony)

## Expected Test Results - HTML Extractor

Here are the actual results from a successful HTML extractor test run:

### ✅ HTML Test Output Example

```
📄 HTML Extractor Service Test
==================================================
📋 Target properties (22):
  - offers.price: The selling price of the product, including any sale prices, discounts, or price ranges
  - offers.priceCurrency: The currency used for the product price (e.g., USD, EUR, GBP)
  - offers.availability: The availability status of the product (in stock, out of stock, limited availability, etc.)
  - description: The product description, features, specifications, and detailed information about the product
  - brand: The brand or manufacturer name of the product
  - offers.itemCondition: The condition of the product (new, used, refurbished, damaged, etc.)
  - color: The color or colors available for the product
  - material: The material the product is made from (fabric, metal, plastic, wood, etc.)
  - aggregateRating: Customer ratings, review scores, star ratings, and rating summaries
  - review: Customer reviews, testimonials, and user feedback about the product
  - category: The product category, type, or classification (electronics, clothing, home goods, etc.)
  - keywords: Keywords, tags, or descriptive terms associated with the product
  - manufacturer: The manufacturer or company that produces the product
  - size: Size information, dimensions, measurements, or size charts for the product
  - audience: Target audience, age group, or intended users for the product
  - additionalType: Additional product types, subcategories, or classification details
  - hasMerchantReturnPolicy: Return policy, exchange policy, warranty information, or return terms
  - negativeNotes: Negative aspects, warnings, limitations, or cautions about the product
  - positiveNotes: Positive highlights, benefits, special features, or selling points of the product
  - nsn: NATO Stock Number, part number, SKU, or unique product identifier
  - countryOfLastProcessing: Country of origin, manufacturing location, or where the product was processed
  - isFamilyFriendly: Whether the product is appropriate for children or families, age restrictions

==================================================
🧪 Testing with comprehensive product HTML...
📝 HTML: Rich product page with multiple data points

🔄 Processing HTML content (6203 characters)
✅ HTML extraction completed!
📊 Properties processed: 22
📋 JSON-LD schema forwarded: True

==================================================
📋 EXTRACTION RESULTS:
==================================================

✅ OFFERS.PRICE:
   📝 <span class="current-price">$299.99</span>

✅ OFFERS.PRICECURRENCY:
   📝 <span class="currency">USD</span>

✅ OFFERS.AVAILABILITY:
   📝 <span class="stock-status">In Stock</span>

✅ BRAND:
   📝 <span class="brand-name">Sony</span>

✅ COLOR:
   📝 <span class="spec-value">Midnight Black</span>

✅ MATERIAL:
   📝 <span class="spec-value">Premium leather headband with metal frame</span>

✅ AGGREGATERATING:
   📝 <span class="rating-score">4.7</span> out of 5 stars (1,234 reviews)

✅ CATEGORY:
   📝 Audio Equipment > Headphones > Wireless Headphones

✅ HASMERCHANTRETURNPOLICY:
   📝 30-day money-back guarantee. Free returns and exchanges.

==================================================
📈 SUCCESS RATE: 22/22 properties (100.0%)
🎉 Successfully extracted properties from HTML content!
🔍 The GPT-4o-mini model was able to analyze the product HTML.
```

### 🎯 HTML Extractor Success Metrics

- **Success Rate**: 100% (22/22 properties extracted)
- **Price Detection**: ✅ Correctly identified "$299.99" and "USD"
- **Brand Recognition**: ✅ Accurate "Sony" brand identification
- **Availability Status**: ✅ Proper "In Stock" detection
- **Product Specifications**: ✅ Color, material, size accurately extracted
- **Review Analysis**: ✅ Ratings and review sentiment captured
- **Policy Information**: ✅ Return policy and terms extracted
- **Categorization**: ✅ Proper product hierarchy identified
- **Geographic Data**: ✅ Country of origin detected

## Troubleshooting

### Common Issues

1. **No properties extracted (0% success rate)**:
   - Check your OpenAI API key configuration
   - Verify internet connectivity
   - Ensure the image URL is accessible

2. **Network errors**:
   - Check if the image URL is accessible from your network
   - Try with a different image URL if needed

3. **API rate limiting**:
   - The test processes 10 properties sequentially
   - If you hit rate limits, wait a moment and try again

4. **Import errors**:
   - Make sure you're running from the `backend` directory
   - Ensure all dependencies are installed with `uv sync`

## Test Development

### Adding New Tests

To add new test cases:

1. Create new test files in this `tests/` directory
2. Follow the naming convention: `test_[service_name].py`
3. Include comprehensive logging and result reporting
4. Update this README with new test documentation

### Modifying Existing Tests

When modifying the test scripts:

**For `test_image_extractor.py`:**
- Update the image URL if needed
- Modify the expected properties list if the service changes
- Update the README with new expected results

**For `test_html_extractor.py`:**
- Update the sample HTML content if needed
- Modify the expected properties list if the service changes
- Adjust the HTML content to test specific property extraction scenarios

## Integration with CI/CD

These tests can be integrated into automated testing pipelines:

```bash
# Run both tests
cd backend && uv run python tests/test_image_extractor.py
cd backend && uv run python tests/test_html_extractor.py

# Or run them in parallel
cd backend && uv run python tests/test_image_extractor.py & uv run python tests/test_html_extractor.py
```

## Related Documentation

- [Main README](../README.md) - Full project documentation
- [Image Extractor Service](../services/image_extractor.py) - Service implementation
- [HTML Extractor Service](../services/html_extractor.py) - Complementary HTML extraction service 