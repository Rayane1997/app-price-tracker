"""
Quick test script for Amazon parser
Usage: python test_amazon_parser.py
"""
import asyncio
from app.parsers import AmazonParser, parser_engine

async def test_amazon():
    # Register Amazon parser
    parser_engine.register_parser(AmazonParser)

    # Test URLs (you can replace with real Amazon URLs)
    test_urls = [
        'https://www.amazon.fr/dp/B0D54HCKNR',  # Example Amazon.fr product
        # 'https://www.amazon.be/dp/XXXXXXXXX',  # Example Amazon.be product
    ]

    for url in test_urls:
        print(f"\n{'='*80}")
        print(f"Testing: {url}")
        print(f"{'='*80}")

        try:
            data = await parser_engine.parse(url)

            print(f"\n✅ SUCCESS!")
            print(f"Name: {data.name}")
            print(f"Price: {data.price} {data.currency}")
            print(f"Image: {data.image_url[:80] if data.image_url else 'N/A'}...")
            print(f"Available: {data.is_available}")
            print(f"Promo: {data.is_promo} ({data.promo_percentage}% off)" if data.is_promo else "Promo: No")
            print(f"Parsed at: {data.parsed_at}")

        except Exception as e:
            print(f"\n❌ FAILED: {e}")

if __name__ == "__main__":
    print("Amazon Parser Test Script")
    print("=" * 80)
    asyncio.run(test_amazon())
