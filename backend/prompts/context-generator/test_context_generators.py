"""
Context Generator Testing Framework
==================================

Comprehensive testing and validation script for all 6 context generators
against rich-schema.json examples with performance metrics and optimization.
"""

import json
import time
from typing import Dict, List, Any, Tuple
from pathlib import Path

# Import all context generators
from product_context_generator import (
    PRODUCT_CONTEXT_GENERATOR_PROMPT, 
    PRODUCT_CONTEXT_GENERATOR_COMPACT,
    validate_product_context
)
from commercial_context_generator import (
    COMMERCIAL_CONTEXT_GENERATOR_PROMPT,
    COMMERCIAL_CONTEXT_GENERATOR_COMPACT, 
    validate_commercial_context
)
from brand_context_generator import (
    BRAND_CONTEXT_GENERATOR_PROMPT,
    BRAND_CONTEXT_GENERATOR_COMPACT,
    validate_brand_context
)
from ux_context_generator import (
    UX_CONTEXT_GENERATOR_PROMPT,
    UX_CONTEXT_GENERATOR_COMPACT,
    validate_ux_context
)
from technical_context_generator import (
    TECHNICAL_CONTEXT_GENERATOR_PROMPT,
    TECHNICAL_CONTEXT_GENERATOR_COMPACT,
    validate_technical_context
)
from visual_context_generator import (
    VISUAL_CONTEXT_GENERATOR_PROMPT,
    VISUAL_CONTEXT_GENERATOR_COMPACT,
    validate_visual_context
)

class ContextGeneratorTester:
    """Comprehensive testing framework for context generators."""
    
    def __init__(self):
        self.test_data_path = Path("../../data")
        self.results = {
            "coverage_metrics": {},
            "performance_metrics": {},
            "accuracy_metrics": {},
            "optimization_results": {}
        }
        
        # Load test data
        self.rich_schema = self._load_json("rich-schema.json")
        self.shallow_schema = self._load_json("shallow-schema.json")
        
        # Define context generators
        self.context_generators = {
            "product": {
                "prompt": PRODUCT_CONTEXT_GENERATOR_PROMPT,
                "compact": PRODUCT_CONTEXT_GENERATOR_COMPACT,
                "validator": validate_product_context,
                "primary_fields": ["name", "description", "category"],
                "token_budget": 1200
            },
            "commercial": {
                "prompt": COMMERCIAL_CONTEXT_GENERATOR_PROMPT,
                "compact": COMMERCIAL_CONTEXT_GENERATOR_COMPACT,
                "validator": validate_commercial_context,
                "primary_fields": ["offers", "price", "availability"],
                "token_budget": 1100
            },
            "brand": {
                "prompt": BRAND_CONTEXT_GENERATOR_PROMPT,
                "compact": BRAND_CONTEXT_GENERATOR_COMPACT,
                "validator": validate_brand_context,
                "primary_fields": ["brand", "manufacturer"],
                "token_budget": 1000
            },
            "ux": {
                "prompt": UX_CONTEXT_GENERATOR_PROMPT,
                "compact": UX_CONTEXT_GENERATOR_COMPACT,
                "validator": validate_ux_context,
                "primary_fields": ["aggregateRating", "review"],
                "token_budget": 1400
            },
            "technical": {
                "prompt": TECHNICAL_CONTEXT_GENERATOR_PROMPT,
                "compact": TECHNICAL_CONTEXT_GENERATOR_COMPACT,
                "validator": validate_technical_context,
                "primary_fields": ["material", "countryOfLastProcessing"],
                "token_budget": 1200
            },
            "visual": {
                "prompt": VISUAL_CONTEXT_GENERATOR_PROMPT,
                "compact": VISUAL_CONTEXT_GENERATOR_COMPACT,
                "validator": validate_visual_context,
                "primary_fields": ["color", "size", "dimensions"],
                "token_budget": 1300
            }
        }
    
    def _load_json(self, filename: str) -> Dict:
        """Load JSON test data file."""
        try:
            with open(self.test_data_path / filename, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Warning: {filename} not found")
            return {}
    
    def _count_tokens(self, text: str) -> int:
        """Estimate token count (approximate: 1 token ≈ 4 characters)."""
        return len(text) // 4
    
    def _simulate_html_from_schema(self, schema_data: Dict) -> str:
        """
        Simulate HTML content from rich schema data for testing.
        This represents what would be extracted from a real product page.
        """
        if isinstance(schema_data, list) and len(schema_data) > 0:
            # Handle list format (like rich-schema.json)
            product_group = schema_data[0]
        else:
            product_group = schema_data
            
        html_parts = []
        
        # Product name and description
        if "name" in product_group:
            html_parts.append(f'<h1 class="product-title">{product_group["name"]}</h1>')
        
        if "description" in product_group:
            html_parts.append(f'<div class="product-description">{product_group["description"]}</div>')
        
        # Brand information
        if "brand" in product_group:
            brand_name = product_group["brand"].get("name", "")
            html_parts.append(f'<div class="brand-info">{brand_name}</div>')
        
        # Audience information  
        if "audience" in product_group:
            gender = product_group["audience"].get("suggestedGender", "")
            html_parts.append(f'<div class="target-audience">{gender}</div>')
        
        # Variants with colors and sizes
        if "hasVariant" in product_group:
            colors = set()
            sizes = set()
            prices = set()
            availability = set()
            
            for variant in product_group["hasVariant"]:
                if "color" in variant:
                    colors.add(variant["color"])
                if "size" in variant:
                    sizes.add(variant["size"])
                if "offers" in variant:
                    offer = variant["offers"]
                    if "price" in offer:
                        prices.add(f"{offer['price']} {offer.get('priceCurrency', '')}")
                    if "availability" in offer:
                        availability.add(offer["availability"].split("/")[-1])
                if "sku" in variant:
                    html_parts.append(f'<span class="sku">{variant["sku"]}</span>')
                if "gtin" in variant:
                    html_parts.append(f'<span class="gtin">{variant["gtin"]}</span>')
            
            # Add color options
            if colors:
                color_html = '<div class="color-options">' + ''.join([
                    f'<span class="color-option" data-color="{color}">{color}</span>' 
                    for color in sorted(colors)
                ]) + '</div>'
                html_parts.append(color_html)
            
            # Add size options  
            if sizes:
                size_html = '<div class="size-options">' + ', '.join(sorted(sizes)) + '</div>'
                html_parts.append(size_html)
            
            # Add pricing information
            if prices:
                price_html = '<div class="pricing">' + ', '.join(prices) + '</div>'
                html_parts.append(price_html)
                
            # Add availability
            if availability:
                avail_html = '<div class="availability">' + ', '.join(availability) + '</div>'
                html_parts.append(avail_html)
        
        return '\n'.join(html_parts)
    
    def test_individual_generator(self, generator_name: str, html_content: str) -> Dict:
        """Test a single context generator and return metrics."""
        generator = self.context_generators[generator_name]
        
        # Test full prompt
        start_time = time.time()
        full_prompt = generator["prompt"].format(html_content=html_content)
        full_tokens = self._count_tokens(full_prompt)
        
        # Test compact prompt
        compact_prompt = generator["compact"].format(html_content=html_content)
        compact_tokens = self._count_tokens(compact_prompt)
        
        end_time = time.time()
        
        # Simulate context generation (in real implementation, this would call LLM)
        simulated_output = self._simulate_context_output(generator_name, html_content)
        
        # Validate output
        validation_result = generator["validator"](simulated_output)
        
        return {
            "generator": generator_name,
            "full_prompt_tokens": full_tokens,
            "compact_prompt_tokens": compact_tokens,
            "token_budget": generator["token_budget"],
            "budget_utilization": (full_tokens / generator["token_budget"]) * 100,
            "token_savings_compact": ((full_tokens - compact_tokens) / full_tokens) * 100,
            "processing_time": end_time - start_time,
            "validation_result": validation_result,
            "simulated_output": simulated_output
        }
    
    def _simulate_context_output(self, generator_name: str, html_content: str) -> str:
        """
        Simulate context generator output based on HTML content.
        In production, this would be actual LLM responses.
        """
        outputs = {
            "product": f"""
Product Name: Stoic - Women's SälkaSt. Tour Shorts - Shorts
Brand: Stoic
Product Category: Women's Outdoor Shorts
Description: Robuste Trekkingshorts mit Beintaschen - robust trekking shorts with leg pockets
Target Audience: Women
Activity Category: Trekking, Hiking, Outdoor Activities
Product Type: Outdoor apparel, technical clothing
            """.strip(),
            
            "commercial": f"""
Price Range: 29.99 EUR
Currency: EUR
Availability: InStock, OutOfStock (varies by variant)
Item Condition: New
Offer Type: Standard retail pricing
Market Position: Mid-range outdoor apparel
            """.strip(),
            
            "brand": f"""
Brand Name: Stoic
Brand Category: Outdoor apparel and equipment
Brand Positioning: Technical outdoor gear for active lifestyles
Brand Heritage: Scandinavian outdoor brand
Target Market: Outdoor enthusiasts, hikers, trekkers
            """.strip(),
            
            "ux": "No sufficient user experience context found",
            
            "technical": f"""
Materials: Canvas fabric, Softshell inserts
Technical Features: PFC-free DWR coating, Breathable, Stretch panels
Product Identifiers: SKU: 112-2189-0111, GTIN: 5714855001666
Item Condition: New
Material Category: Technical outdoor fabric
Performance Features: Water-resistant, breathable, flexible construction
            """.strip(),
            
            "visual": f"""
Available Colors: Black, Forest Green
Color Categories: Black, Green
Size Options: 34 (EU), 36 (EU), 38 (EU), 40 (EU), 42 (EU), 44 (EU), 46 (EU)
Size System: EU Women's apparel sizing
Style Description: Women's outdoor trekking shorts
Product Category: Apparel - Women's Shorts
Size Range: EU 34 to 46
            """.strip()
        }
        
        return outputs.get(generator_name, "No context generated")
    
    def test_all_generators(self) -> Dict:
        """Test all context generators against rich schema data."""
        # Generate HTML from rich schema
        html_content = self._simulate_html_from_schema(self.rich_schema)
        
        print("Generated Test HTML:")
        print("=" * 50)
        print(html_content)
        print("=" * 50)
        print()
        
        results = {}
        total_tokens = 0
        total_budget = 0
        
        for generator_name in self.context_generators.keys():
            print(f"Testing {generator_name.upper()} Context Generator...")
            result = self.test_individual_generator(generator_name, html_content)
            results[generator_name] = result
            
            total_tokens += result["full_prompt_tokens"]
            total_budget += result["token_budget"]
            
            print(f"  ✅ Tokens: {result['full_prompt_tokens']}/{result['token_budget']} "
                  f"({result['budget_utilization']:.1f}% of budget)")
            print(f"  💾 Compact saves: {result['token_savings_compact']:.1f}% tokens")
            print(f"  ✅ Validation: {result['validation_result']['is_valid']} "
                  f"(confidence: {result['validation_result']['confidence_score']:.2f})")
            print()
        
        # Overall metrics
        results["overall"] = {
            "total_tokens_used": total_tokens,
            "total_token_budget": total_budget,
            "budget_utilization": (total_tokens / total_budget) * 100,
            "generators_tested": len(self.context_generators),
            "html_content_length": len(html_content)
        }
        
        return results
    
    def analyze_field_coverage(self) -> Dict:
        """Analyze how well context generators cover rich schema fields."""
        rich_fields = set()
        
        # Extract all fields from rich schema
        if isinstance(self.rich_schema, list):
            product_group = self.rich_schema[0]
        else:
            product_group = self.rich_schema
            
        # Count fields in product group
        for key in product_group.keys():
            if key not in ["@context", "@type", "@id"]:
                rich_fields.add(key)
        
        # Count fields in variants
        if "hasVariant" in product_group:
            for variant in product_group["hasVariant"]:
                for key in variant.keys():
                    if key not in ["@type"]:
                        rich_fields.add(key)
                        
                # Count offer fields
                if "offers" in variant:
                    for key in variant["offers"].keys():
                        if key not in ["@type"]:
                            rich_fields.add(f"offers.{key}")
        
        # Map fields to context generators
        field_coverage = {}
        for generator_name, generator_info in self.context_generators.items():
            primary_fields = generator_info["primary_fields"]
            covered_fields = [field for field in rich_fields if any(pf in field for pf in primary_fields)]
            field_coverage[generator_name] = {
                "primary_fields": primary_fields,
                "covered_rich_fields": covered_fields,
                "coverage_count": len(covered_fields)
            }
        
        return {
            "total_rich_fields": len(rich_fields),
            "rich_fields_list": sorted(list(rich_fields)),
            "generator_coverage": field_coverage
        }
    
    def generate_optimization_report(self, test_results: Dict) -> Dict:
        """Generate optimization recommendations based on test results."""
        recommendations = []
        
        # Token efficiency recommendations
        total_tokens = test_results["overall"]["total_tokens_used"]
        budget_utilization = test_results["overall"]["budget_utilization"]
        
        if budget_utilization > 90:
            recommendations.append({
                "type": "token_efficiency",
                "priority": "high",
                "issue": f"High token utilization ({budget_utilization:.1f}%)",
                "recommendation": "Use compact versions for simple products or reduce examples"
            })
        
        # Individual generator recommendations
        for generator_name, result in test_results.items():
            if generator_name == "overall":
                continue
                
            if result["budget_utilization"] > 95:
                recommendations.append({
                    "type": "generator_optimization",
                    "priority": "medium",
                    "generator": generator_name,
                    "issue": f"Exceeds token budget ({result['budget_utilization']:.1f}%)",
                    "recommendation": f"Optimize {generator_name} prompt or use compact version"
                })
            
            if result["validation_result"]["confidence_score"] < 0.7:
                recommendations.append({
                    "type": "quality_improvement", 
                    "priority": "high",
                    "generator": generator_name,
                    "issue": f"Low confidence score ({result['validation_result']['confidence_score']:.2f})",
                    "recommendation": f"Improve {generator_name} prompt examples or validation logic"
                })
        
        return {
            "optimization_opportunities": len(recommendations),
            "recommendations": recommendations,
            "potential_token_savings": sum([
                result["token_savings_compact"] * result["full_prompt_tokens"] / 100
                for result in test_results.values() 
                if isinstance(result, dict) and "token_savings_compact" in result
            ])
        }
    
    def run_comprehensive_test(self) -> None:
        """Run complete testing suite and generate report."""
        print("🚀 Starting Comprehensive Context Generator Testing")
        print("=" * 60)
        print()
        
        # Test all generators
        test_results = self.test_all_generators()
        
        # Analyze field coverage
        coverage_analysis = self.analyze_field_coverage()
        
        # Generate optimization recommendations
        optimization_report = self.generate_optimization_report(test_results)
        
        # Print comprehensive report
        self._print_comprehensive_report(test_results, coverage_analysis, optimization_report)
        
        # Save results
        self.results = {
            "test_results": test_results,
            "coverage_analysis": coverage_analysis,
            "optimization_report": optimization_report,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }
    
    def _print_comprehensive_report(self, test_results: Dict, coverage_analysis: Dict, optimization_report: Dict) -> None:
        """Print detailed testing report."""
        print("📊 CONTEXT GENERATOR TESTING REPORT")
        print("=" * 60)
        print()
        
        # Overall metrics
        overall = test_results["overall"]
        print(f"🎯 OVERALL PERFORMANCE:")
        print(f"   Total Token Usage: {overall['total_tokens_used']:,} / {overall['total_token_budget']:,}")
        print(f"   Budget Utilization: {overall['budget_utilization']:.1f}%")
        print(f"   Generators Tested: {overall['generators_tested']}")
        print()
        
        # Field coverage
        print(f"📋 FIELD COVERAGE ANALYSIS:")
        print(f"   Rich Schema Fields: {coverage_analysis['total_rich_fields']} total")
        for gen_name, coverage in coverage_analysis['generator_coverage'].items():
            print(f"   {gen_name.title()}: {coverage['coverage_count']} fields covered")
        print()
        
        # Individual generator performance
        print("🔧 GENERATOR PERFORMANCE:")
        for gen_name, result in test_results.items():
            if gen_name == "overall":
                continue
            print(f"   {gen_name.upper()}:")
            print(f"     Tokens: {result['full_prompt_tokens']} ({result['budget_utilization']:.1f}% of budget)")
            print(f"     Validation: {'✅ Valid' if result['validation_result']['is_valid'] else '❌ Invalid'}")
            print(f"     Confidence: {result['validation_result']['confidence_score']:.2f}")
        print()
        
        # Optimization recommendations
        print("💡 OPTIMIZATION RECOMMENDATIONS:")
        if optimization_report["recommendations"]:
            for i, rec in enumerate(optimization_report["recommendations"], 1):
                priority_emoji = "🔥" if rec["priority"] == "high" else "⚠️"
                print(f"   {i}. {priority_emoji} {rec['recommendation']}")
        else:
            print("   ✅ No critical optimizations needed")
        print()
        
        print(f"💾 Potential Token Savings: {optimization_report['potential_token_savings']:.0f} tokens")
        print()
        print("✅ Testing Complete!")

def main():
    """Run the context generator testing framework."""
    tester = ContextGeneratorTester()
    tester.run_comprehensive_test()

if __name__ == "__main__":
    main() 