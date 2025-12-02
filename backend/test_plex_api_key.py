"""
Test Plex API with API Key authentication
"""
import asyncio
import httpx
from config import settings

async def test_plex_with_api_key():
    """Test Plex API using API Key authentication"""
    print("=" * 70)
    print("Testing Plex API with API Key Authentication")
    print("=" * 70)
    
    base_url = settings.plex_api_url
    api_key = settings.plex_api_key
    
    headers = {
        "X-API-Key": api_key,
        "Content-Type": "application/json"
    }
    
    # Test 1: Purchase Order API
    print("\n" + "=" * 70)
    print("Test 1: Get Purchase Order (pONumber=061856)")
    print("=" * 70)
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                f"{base_url}/purchasing/v1/purchase-orders",
                params={"pONumber": "061856"},
                headers=headers
            )
            
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print("✅ SUCCESS!")
                if isinstance(data, list) and len(data) > 0:
                    po = data[0]
                    print(f"PO Number: {po.get('poNumber')}")
                    print(f"Status: {po.get('status')}")
                    print(f"Currency: {po.get('currencyCode')}")
                else:
                    print(f"Response: {data}")
            else:
                print(f"❌ Error: {response.status_code}")
                print(f"Response: {response.text[:200]}")
                
    except Exception as e:
        print(f"❌ Exception: {type(e).__name__}: {e}")
    
    # Test 2: AP Invoices - Find RECEIVED invoices
    print("\n" + "=" * 70)
    print("Test 2: Get RECEIVED Invoices")
    print("=" * 70)
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                f"{base_url}/accounting/v1/ap-invoices",
                params={
                    "invoiceNumber": "Received",
                    "status": "new"
                },
                headers=headers
            )
            
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print("✅ SUCCESS!")
                print(f"Found {len(data) if isinstance(data, list) else 0} RECEIVED invoices")
                if isinstance(data, list) and len(data) > 0:
                    invoice = data[0]
                    print(f"Invoice ID: {invoice.get('id')}")
                    print(f"Invoice Number: {invoice.get('invoiceNumber')}")
                    print(f"Supplier Code: {invoice.get('supplierCode')}")
            else:
                print(f"❌ Error: {response.status_code}")
                print(f"Response: {response.text[:200]}")
                
    except Exception as e:
        print(f"❌ Exception: {type(e).__name__}: {e}")
    
    print("\n" + "=" * 70)
    print("Test Complete")
    print("=" * 70)

if __name__ == "__main__":
    asyncio.run(test_plex_with_api_key())

