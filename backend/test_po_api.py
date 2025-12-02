"""
Test Purchase Order API endpoint
"""
import asyncio
import sys
from pathlib import Path
from dotenv import load_dotenv

sys.path.append(str(Path(__file__).resolve().parent.parent))

load_dotenv()

from core.plex_client import plex_client

async def test_po():
    """Test getting purchase order from Plex"""
    print("Testing Purchase Order API...")
    print("=" * 60)
    
    po_number = "062486"
    print(f"Fetching PO: {po_number}")
    
    try:
        result = await plex_client.get_purchase_order(po_number)
        print("\n✅ SUCCESS!")
        print(f"PO Data Type: {type(result)}")
        if isinstance(result, list):
            print(f"Array length: {len(result)}")
            if len(result) > 0:
                result = result[0]
        print(f"\nPO Number: {result.get('poNumber') or result.get('po_number', 'N/A')}")
        print(f"Status: {result.get('status', 'N/A')}")
        print(f"Total Amount: {result.get('totalAmount') or result.get('total_amount', 'N/A')}")
        print(f"Currency: {result.get('currencyCode') or result.get('currency', 'N/A')}")
        if result.get('lineItems') or result.get('line_items'):
            line_items = result.get('lineItems') or result.get('line_items', [])
            print(f"\nLine Items: {len(line_items)}")
            for i, item in enumerate(line_items[:3]):  # Show first 3
                print(f"  {i+1}. {item.get('description', 'N/A')} - Qty: {item.get('quantity', 0)}")
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_po())

