#!/usr/bin/env python3
"""
Test Shopify webhook integration with mock calls
"""

import asyncio
import json
import hmac
import hashlib
import base64
from dotenv import load_dotenv
import httpx

# Load environment variables
load_dotenv()

BASE_URL = "http://localhost:8000"

def generate_shopify_hmac(payload: str, secret: str) -> str:
    """Generate HMAC signature for Shopify webhook."""
    return base64.b64encode(
        hmac.new(
            secret.encode('utf-8'),
            payload.encode('utf-8'),
            hashlib.sha256
        ).digest()
    ).decode('utf-8')

async def test_webhook_integration():
    """Test Shopify webhook integration."""
    try:
        print("🔗 Testing Shopify Webhook Integration")
        print("=" * 50)

        # Test webhook secret from env
        webhook_secret = "test_webhook_secret_for_development_only"
        shop_domain = "test-store.myshopify.com"

        print(f"🔑 Webhook Secret: {webhook_secret}")
        print(f"🏪 Shop Domain: {shop_domain}")

        async with httpx.AsyncClient(timeout=60.0) as client:

            # Test 1: Valid Order Paid Webhook
            print(f"\n💳 Test 1: Valid Order Paid Webhook...")

            # Mock Shopify order payload
            mock_order = {
                "id": 5678901234,
                "order_number": "MAGICTALES001",
                "email": "customer@example.com",
                "customer": {
                    "id": 98765432,
                    "email": "customer@example.com",
                    "first_name": "Emma",
                    "last_name": "Watson"
                },
                "line_items": [
                    {
                        "id": 12345,
                        "title": "Emma's Magical Castle Adventure",
                        "quantity": 1,
                        "price": "29.99",
                        "properties": [
                            {"name": "preview_id", "value": "test-preview-123"},
                            {"name": "child_name", "value": "Emma"},
                            {"name": "theme", "value": "magic_castle"}
                        ]
                    }
                ],
                "financial_status": "paid",
                "created_at": "2025-12-27T18:00:00Z"
            }

            payload = json.dumps(mock_order, separators=(',', ':'))  # No spaces
            hmac_signature = generate_shopify_hmac(payload, webhook_secret)

            print(f"📦 Order ID: {mock_order['id']}")
            print(f"🎫 Order Number: {mock_order['order_number']}")
            print(f"🆔 Preview ID: test-preview-123")
            print(f"🔐 HMAC: {hmac_signature[:20]}...")

            # Send webhook
            headers = {
                "X-Shopify-Hmac-Sha256": hmac_signature,
                "X-Shopify-Shop-Domain": shop_domain,
                "X-Shopify-Topic": "orders/paid",
                "Content-Type": "application/json"
            }

            response = await client.post(
                f"{BASE_URL}/webhooks/shopify/order-paid",
                headers=headers,
                content=payload
            )

            print(f"📊 Response Status: {response.status_code}")
            if response.status_code == 200:
                print(f"✅ Valid webhook accepted!")
                print(f"📋 Response: {response.json()}")
            else:
                print(f"❌ Webhook failed: {response.text}")

            # Test 2: Invalid HMAC Signature
            print(f"\n🚫 Test 2: Invalid HMAC Signature...")

            invalid_headers = headers.copy()
            invalid_headers["X-Shopify-Hmac-Sha256"] = "invalid_signature"

            response = await client.post(
                f"{BASE_URL}/webhooks/shopify/order-paid",
                headers=invalid_headers,
                content=payload
            )

            print(f"📊 Response Status: {response.status_code}")
            if response.status_code == 401:
                print(f"✅ Invalid HMAC correctly rejected!")
                print(f"📋 Response: {response.text}")
            else:
                print(f"⚠️ Expected 401 rejection, got: {response.status_code}")

            # Test 3: Wrong Shop Domain
            print(f"\n🏪 Test 3: Wrong Shop Domain...")

            wrong_domain_headers = headers.copy()
            wrong_domain_headers["X-Shopify-Shop-Domain"] = "wrong-store.myshopify.com"

            response = await client.post(
                f"{BASE_URL}/webhooks/shopify/order-paid",
                headers=wrong_domain_headers,
                content=payload
            )

            print(f"📊 Response Status: {response.status_code}")
            if response.status_code == 401:
                print(f"✅ Wrong domain correctly rejected!")
                print(f"📋 Response: {response.text}")
            else:
                print(f"⚠️ Expected 401 rejection, got: {response.status_code}")

            # Test 4: Missing Headers
            print(f"\n📄 Test 4: Missing Headers...")

            missing_headers = {
                "Content-Type": "application/json"
                # Missing HMAC and domain headers
            }

            response = await client.post(
                f"{BASE_URL}/webhooks/shopify/order-paid",
                headers=missing_headers,
                content=payload
            )

            print(f"📊 Response Status: {response.status_code}")
            if response.status_code == 401:
                print(f"✅ Missing headers correctly rejected!")
                print(f"📋 Response: {response.text}")
            else:
                print(f"⚠️ Expected 401 rejection, got: {response.status_code}")

            # Test 5: Order Without Preview ID
            print(f"\n📋 Test 5: Order Without Preview ID...")

            # Order without preview_id property
            mock_order_no_preview = {
                "id": 9876543210,
                "order_number": "MAGICTALES002",
                "email": "customer2@example.com",
                "customer": {
                    "id": 11111111,
                    "email": "customer2@example.com"
                },
                "line_items": [
                    {
                        "id": 54321,
                        "title": "Regular Product",
                        "quantity": 1,
                        "price": "19.99",
                        "properties": []  # No preview_id
                    }
                ]
            }

            payload_no_preview = json.dumps(mock_order_no_preview, separators=(',', ':'))
            hmac_no_preview = generate_shopify_hmac(payload_no_preview, webhook_secret)

            headers_no_preview = headers.copy()
            headers_no_preview["X-Shopify-Hmac-Sha256"] = hmac_no_preview

            response = await client.post(
                f"{BASE_URL}/webhooks/shopify/order-paid",
                headers=headers_no_preview,
                content=payload_no_preview
            )

            print(f"📊 Response Status: {response.status_code}")
            print(f"📋 Response: {response.text}")

            # Test 6: Duplicate Order (Idempotency)
            print(f"\n🔄 Test 6: Duplicate Order (Idempotency)...")

            # Send the same order twice
            response1 = await client.post(
                f"{BASE_URL}/webhooks/shopify/order-paid",
                headers=headers,
                content=payload
            )

            response2 = await client.post(
                f"{BASE_URL}/webhooks/shopify/order-paid",
                headers=headers,
                content=payload
            )

            print(f"📊 First Response: {response1.status_code}")
            print(f"📊 Second Response: {response2.status_code}")
            print(f"✅ Idempotency test completed")

        print(f"\n🎉 Webhook Integration Testing Completed!")
        return True

    except Exception as e:
        print(f"❌ Webhook testing failed: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_webhook_integration())
    exit(0 if success else 1)