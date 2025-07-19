"""
User Experience Context Generator Prompt
=======================================

Tier 1 Context Generator for extracting comprehensive customer feedback,
reviews, ratings, and sentiment analysis from product pages.
This prompt implements research-backed techniques for high-accuracy extraction.

Expected Performance Improvements:
- System Role Assignment: 10-50% accuracy improvement
- Chain-of-Thought: 50-100% accuracy improvement  
- Few-Shot Learning: 26-47% performance gains
- Emotion Prompting: 8-115% performance boost

Primary Context For Fields:
- aggregateRating, review, negativeNotes, positiveNotes

Secondary Context For Fields:
- description, offers.itemCondition, hasMerchantReturnPolicy, isFamilyFriendly
"""

UX_CONTEXT_GENERATOR_PROMPT = """# System Role
You are an **expert customer experience analyst** with 15+ years of experience in extracting and analyzing customer feedback, reviews, ratings, and sentiment from e-commerce product pages. You specialize in natural language processing, sentiment analysis, and customer behavior insights across multiple languages, product categories, and review platforms.

## Task Definition
Your task is to analyze HTML content and extract comprehensive **User Experience Context** through this methodical process:

1. **Locate Review Sections**: Identify customer reviews, ratings, testimonials, and feedback areas
2. **Extract Rating Data**: Gather star ratings, numerical scores, and aggregated rating information
3. **Analyze Sentiment**: Categorize positive and negative feedback themes and patterns
4. **Summarize Feedback**: Create balanced summaries of customer experiences and opinions
5. **Generate UX Context**: Compile user experience insights for schema generation

## Context & Specifics
This extraction is **vital for creating rich customer experience data** that enhances product trustworthiness and search visibility. Quality user experience context directly improves click-through rates, customer confidence, and helps potential buyers make informed decisions.

**Business Impact**: Your thorough UX analysis enables accurate aggregateRating, review, positiveNotes, and negativeNotes schema.org fields that build customer trust, improve search rankings, and provide authentic social proof that drives conversions.

## Examples (Few-Shot)

### Example 1
**Input HTML**: `<div class="rating">4.5/5 stars (127 reviews)</div><div class="review">Great quality shorts, very durable and comfortable</div><div class="review">Pockets are perfect size for hiking essentials</div><div class="review">Runs slightly small, recommend sizing up</div><div class="review">Material feels premium, worth the price</div>`

**Output UX Context**:
```
Aggregate Rating: 4.5 out of 5 stars
Total Reviews: 127
Review Sample Count: 4 reviews analyzed
Positive Themes: Quality, Durability, Comfort, Pocket design, Premium materials, Value for money
Negative Themes: Sizing runs small
Sample Positive Reviews: "Great quality shorts, very durable and comfortable", "Material feels premium, worth the price"
Sample Negative Reviews: "Runs slightly small, recommend sizing up"
Overall Sentiment: Highly positive with minor sizing concerns
Customer Satisfaction: High (4.5/5 rating with substantial review volume)
```

### Example 2
**Input HTML**: `<span class="stars">★★★★☆</span><p class="review-summary">Customers love the sound quality but mention comfort issues</p><div class="pros">Excellent noise cancellation, Clear audio, Long battery life</div><div class="cons">Tight fit for large heads, Heavy weight, Expensive</div><div class="rating-breakdown">5 stars: 45%, 4 stars: 30%, 3 stars: 15%, 2 stars: 7%, 1 star: 3%</div>`

**Output UX Context**:
```
Aggregate Rating: 4 out of 5 stars
Rating Distribution: 5★(45%), 4★(30%), 3★(15%), 2★(7%), 1★(3%)
Positive Themes: Sound quality, Noise cancellation, Clear audio, Long battery life
Negative Themes: Comfort issues, Tight fit for large heads, Heavy weight, Price concerns
Sample Positive Reviews: "Excellent noise cancellation", "Clear audio", "Long battery life"
Sample Negative Reviews: "Tight fit for large heads", "Heavy weight", "Expensive"
Overall Sentiment: Positive with notable comfort concerns
Review Summary: Customers love sound quality but mention comfort issues
Customer Satisfaction: Good (4/5 with mixed feedback on comfort)
```

### Example 3
**Input HTML**: `<div class="reviews-section"><h3>Customer Reviews (89)</h3><div class="avg-rating">3.2 stars</div><div class="review negative">Poor quality, broke after 2 weeks</div><div class="review negative">Not worth the money, cheap materials</div><div class="review positive">Good value for the price point</div><div class="review negative">Arrived damaged, return process difficult</div></div>`

**Output UX Context**:
```
Aggregate Rating: 3.2 out of 5 stars
Total Reviews: 89
Review Sample Count: 4 reviews analyzed
Positive Themes: Good value for price point
Negative Themes: Poor quality, Durability issues, Cheap materials, Shipping damage, Return process difficulties
Sample Positive Reviews: "Good value for the price point"
Sample Negative Reviews: "Poor quality, broke after 2 weeks", "Not worth the money, cheap materials", "Arrived damaged, return process difficult"
Overall Sentiment: Mostly negative with quality concerns
Customer Satisfaction: Below average (3.2/5 with significant quality complaints)
```

### Example 4
**Input HTML**: `<div class="testimonials"><blockquote>"Absolutely love this product! Game changer for my daily routine."</blockquote><blockquote>"Best purchase I've made this year, highly recommend!"</blockquote><blockquote>"Quality exceeded expectations, fast shipping too."</blockquote></div><div class="rating-widget">4.8/5 based on verified purchases</div>`

**Output UX Context**:
```
Aggregate Rating: 4.8 out of 5 stars
Review Type: Verified purchase testimonials
Review Sample Count: 3 testimonials analyzed
Positive Themes: Life-changing product, Highly recommended, Exceeded expectations, Quality, Fast shipping
Negative Themes: None identified
Sample Positive Reviews: "Absolutely love this product! Game changer for my daily routine", "Best purchase I've made this year, highly recommend!", "Quality exceeded expectations, fast shipping too"
Sample Negative Reviews: None available
Overall Sentiment: Extremely positive
Customer Satisfaction: Excellent (4.8/5 with enthusiastic testimonials)
```

### Example 5
**Input HTML**: `<div class="review-placeholder">No customer reviews yet</div><div class="rating-section">Be the first to review this product!</div><div class="review-count">0 reviews</div>`

**Output UX Context**:
```
Aggregate Rating: No ratings available
Total Reviews: 0
Review Status: No customer reviews yet
Positive Themes: None available
Negative Themes: None available
Sample Positive Reviews: None available
Sample Negative Reviews: None available
Overall Sentiment: No customer feedback available
Customer Satisfaction: Unrated (new product or limited exposure)
```

### Example 6
**Input HTML**: `<div class="external-reviews">Reviews from Amazon: 4.3/5 (2,156 reviews)</div><div class="google-reviews">Google Reviews: 4.1/5 (89 reviews)</div><p class="review-note">See detailed reviews on product manufacturer website</p>`

**Output UX Context**:
```
Aggregate Rating: 4.3/5 (Amazon), 4.1/5 (Google)
Total Reviews: 2,156 (Amazon) + 89 (Google)
Review Sources: External platforms (Amazon, Google)
Positive Themes: Not directly available (external reviews)
Negative Themes: Not directly available (external reviews)
Overall Sentiment: Positive based on external ratings
Customer Satisfaction: Good across multiple platforms
Review Note: Detailed reviews available on external platforms
```

### Example 7
**Input HTML**: `<div class="product-specs">Technical specifications</div><div class="shipping-info">Delivery details</div><nav>Menu items</nav>`

**Output UX Context**:
```
No sufficient user experience context found
```

## Critical Reminders
- Extract ONLY customer feedback and rating information explicitly present in the HTML content
- Preserve original customer quote language when summarizing feedback
- Distinguish between verified and unverified reviews if indicated
- Separate positive and negative themes objectively without bias
- Return "No sufficient user experience context found" if no reviews or ratings are present
- Note external review sources (Amazon, Google, etc.) when present
- Maintain objectivity when summarizing customer sentiment
- Include sample review quotes to provide authentic voice of customer
- Calculate or extract aggregate ratings with proper scale notation
- Do not hallucinate customer feedback or ratings not clearly present in the content

**Input HTML Content**: {html_content}"""

# Alternative shorter version for token-constrained scenarios
UX_CONTEXT_GENERATOR_COMPACT = """You are an expert customer experience analyst. Extract customer feedback and rating information from the HTML below and format as structured UX context.

Return format:
```
Aggregate Rating: [rating with scale]
Total Reviews: [number of reviews]
Positive Themes: [main positive points]
Negative Themes: [main negative points]
Overall Sentiment: [positive/negative/mixed/neutral]
```

If no customer feedback is available, return: "No sufficient user experience context found"

HTML Content: {html_content}"""

# Context generator configuration
UX_CONTEXT_CONFIG = {
    "max_tokens": 1400,
    "temperature": 0.15,  # Slightly higher for nuanced sentiment analysis
    "timeout": 35,
    "retry_attempts": 2,
    "validation_required": True,
    "confidence_threshold": 0.6
}

def validate_ux_context(context_output: str) -> dict:
    """
    Validate the UX context output format and completeness.
    
    Args:
        context_output: The raw output from the UX context generator
        
    Returns:
        dict: Validation result with status and extracted fields
    """
    validation_result = {
        "is_valid": False,
        "extracted_fields": {},
        "missing_fields": [],
        "confidence_score": 0.0,
        "errors": []
    }
    
    # Check for "no sufficient user experience context" response
    if "no sufficient user experience context found" in context_output.lower():
        validation_result["is_valid"] = True
        validation_result["confidence_score"] = 1.0
        validation_result["extracted_fields"]["status"] = "insufficient_data"
        return validation_result
    
    # Expected fields in UX context
    core_fields = ["aggregate rating", "overall sentiment"]
    valuable_fields = ["total reviews", "positive themes", "negative themes"]
    optional_fields = ["review sample count", "customer satisfaction"]
    
    # Parse structured output
    lines = context_output.strip().split('\n')
    for line in lines:
        if ':' in line:
            key, value = line.split(':', 1)
            field_name = key.strip().lower()
            field_value = value.strip()
            
            if field_value and field_value not in ["None available", "Not available", "None identified"]:
                validation_result["extracted_fields"][field_name] = field_value
    
    # Check for core UX fields
    has_rating = any("rating" in key for key in validation_result["extracted_fields"].keys())
    has_sentiment = any("sentiment" in key for key in validation_result["extracted_fields"].keys())
    has_themes = any("themes" in key for key in validation_result["extracted_fields"].keys())
    has_reviews = any("reviews" in key for key in validation_result["extracted_fields"].keys())
    
    # Calculate confidence score
    confidence_factors = []
    
    if has_rating:
        confidence_factors.append(0.3)  # Rating is most valuable
    
    if has_sentiment:
        confidence_factors.append(0.2)  # Sentiment analysis is important
        
    if has_themes:
        confidence_factors.append(0.2)  # Themes provide valuable insights
        
    if has_reviews:
        confidence_factors.append(0.2)  # Review data adds credibility
    
    # Sample reviews bonus
    has_sample_reviews = any("sample" in key and "review" in key for key in validation_result["extracted_fields"].keys())
    if has_sample_reviews:
        confidence_factors.append(0.1)
    
    validation_result["confidence_score"] = sum(confidence_factors)
    validation_result["is_valid"] = validation_result["confidence_score"] >= 0.6
    
    # Track missing valuable fields
    if not has_rating:
        validation_result["missing_fields"].append("aggregate rating")
    if not has_sentiment:
        validation_result["missing_fields"].append("overall sentiment")
    if not has_themes:
        validation_result["missing_fields"].append("positive/negative themes")
    
    if not validation_result["is_valid"]:
        validation_result["errors"].append("Insufficient user experience data extracted")
    
    return validation_result

def extract_rating_data(ux_context: str) -> dict:
    """
    Extract structured rating data from UX context.
    
    Args:
        ux_context: Raw UX context output
        
    Returns:
        dict: Structured rating information
    """
    import re
    
    rating_data = {
        "rating_value": None,
        "best_rating": None,
        "rating_count": None,
        "rating_scale": None
    }
    
    # Extract rating value and scale
    rating_patterns = [
        r'aggregate rating:\s*(\d+(?:\.\d+)?)\s*(?:out of|/)?\s*(\d+)',
        r'(\d+(?:\.\d+)?)\s*/\s*(\d+)\s*stars?',
        r'(\d+(?:\.\d+)?)\s*out of\s*(\d+)'
    ]
    
    for pattern in rating_patterns:
        match = re.search(pattern, ux_context.lower())
        if match:
            rating_data["rating_value"] = float(match.group(1))
            rating_data["best_rating"] = int(match.group(2))
            break
    
    # Extract review count
    count_patterns = [
        r'total reviews?:\s*(\d+)',
        r'(\d+)\s*reviews?',
        r'based on\s*(\d+)\s*reviews?'
    ]
    
    for pattern in count_patterns:
        match = re.search(pattern, ux_context.lower())
        if match:
            rating_data["rating_count"] = int(match.group(1))
            break
    
    return rating_data

def analyze_sentiment_themes(ux_context: str) -> dict:
    """
    Analyze positive and negative sentiment themes from UX context.
    
    Args:
        ux_context: Raw UX context output
        
    Returns:
        dict: Sentiment analysis results
    """
    sentiment_analysis = {
        "positive_themes": [],
        "negative_themes": [],
        "overall_sentiment": None,
        "sentiment_balance": None
    }
    
    lines = ux_context.strip().split('\n')
    
    for line in lines:
        if ':' in line:
            key, value = line.split(':', 1)
            field_name = key.strip().lower()
            field_value = value.strip()
            
            if "positive themes" in field_name and field_value not in ["None available", "None identified"]:
                # Split themes by common delimiters
                themes = [theme.strip() for theme in field_value.replace(',', ';').split(';')]
                sentiment_analysis["positive_themes"] = themes
                
            elif "negative themes" in field_name and field_value not in ["None available", "None identified"]:
                themes = [theme.strip() for theme in field_value.replace(',', ';').split(';')]
                sentiment_analysis["negative_themes"] = themes
                
            elif "overall sentiment" in field_name:
                sentiment_analysis["overall_sentiment"] = field_value
    
    # Calculate sentiment balance
    pos_count = len(sentiment_analysis["positive_themes"])
    neg_count = len(sentiment_analysis["negative_themes"])
    
    if pos_count > 0 and neg_count > 0:
        sentiment_analysis["sentiment_balance"] = f"{pos_count} positive : {neg_count} negative themes"
    elif pos_count > 0:
        sentiment_analysis["sentiment_balance"] = "Predominantly positive"
    elif neg_count > 0:
        sentiment_analysis["sentiment_balance"] = "Predominantly negative"
    else:
        sentiment_analysis["sentiment_balance"] = "No clear themes identified"
    
    return sentiment_analysis 