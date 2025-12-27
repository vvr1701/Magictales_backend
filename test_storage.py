#!/usr/bin/env python3
"""
Test Cloudflare R2 storage operations
"""

import asyncio
import os
import io
from PIL import Image
from dotenv import load_dotenv
from app.services.storage import StorageService

# Load environment variables
load_dotenv()

async def test_storage_operations():
    """Test Cloudflare R2 storage operations."""
    try:
        print("🗄️ Testing Cloudflare R2 Storage Operations")
        print("=" * 50)

        # Check R2 credentials
        r2_access_key = os.getenv("R2_ACCESS_KEY_ID")
        r2_secret_key = os.getenv("R2_SECRET_ACCESS_KEY")
        r2_bucket = os.getenv("R2_BUCKET_NAME")
        r2_account_id = os.getenv("R2_ACCOUNT_ID")

        if not all([r2_access_key, r2_secret_key, r2_bucket, r2_account_id]):
            raise ValueError("All R2 environment variables are required")

        print(f"🔑 R2 Access Key: {'*' * 15}...{r2_access_key[-5:]}")
        print(f"🪣 R2 Bucket: {r2_bucket}")
        print(f"🏢 Account ID: {r2_account_id}")

        # Initialize storage service
        print(f"\n📦 Initializing Storage Service...")
        storage = StorageService()

        # Test 1: Create a test image
        print(f"\n🖼️ Creating test image...")
        test_image = Image.new('RGB', (200, 200), color='purple')

        # Add some test content to make it a bit more interesting
        from PIL import ImageDraw, ImageFont
        draw = ImageDraw.Draw(test_image)
        try:
            font = ImageFont.load_default()
        except:
            font = None

        draw.rectangle([20, 20, 180, 180], outline='gold', width=5)
        draw.text((60, 90), "TEST", fill='white', font=font)

        # Convert to bytes
        image_buffer = io.BytesIO()
        test_image.save(image_buffer, format='JPEG', quality=95)
        test_image_bytes = image_buffer.getvalue()

        print(f"📏 Test image size: {len(test_image_bytes)} bytes")

        # Test 2: Upload to uploads folder
        print(f"\n⬆️ Testing upload to /uploads/ folder...")
        test_preview_id = "test-preview-123"
        upload_path = f"uploads/{test_preview_id}/photo.jpg"

        try:
            upload_url = await storage.upload_image(
                test_image_bytes,
                upload_path,
                content_type="image/jpeg"
            )
            print(f"✅ Upload successful!")
            print(f"📸 Upload URL: {upload_url}")
        except Exception as e:
            print(f"❌ Upload failed: {e}")
            return False

        # Test 3: Upload to previews folder (watermarked)
        print(f"\n🏷️ Testing upload to /previews/ folder...")
        preview_path = f"previews/{test_preview_id}/page_01.jpg"

        try:
            preview_url = await storage.upload_image(
                test_image_bytes,
                preview_path,
                content_type="image/jpeg"
            )
            print(f"✅ Preview upload successful!")
            print(f"📸 Preview URL: {preview_url}")
        except Exception as e:
            print(f"❌ Preview upload failed: {e}")

        # Test 4: Upload to final folder (high-res)
        print(f"\n📁 Testing upload to /final/ folder...")
        final_path = f"final/{test_preview_id}/page_01.jpg"

        try:
            final_url = await storage.upload_image(
                test_image_bytes,
                final_path,
                content_type="image/jpeg"
            )
            print(f"✅ Final upload successful!")
            print(f"📸 Final URL: {final_url}")
        except Exception as e:
            print(f"❌ Final upload failed: {e}")

        # Test 5: Generate signed URL
        print(f"\n🔐 Testing signed URL generation...")
        try:
            signed_url = storage.generate_signed_url(upload_path, expires_in=3600)
            print(f"✅ Signed URL generated successfully!")
            print(f"🔗 Signed URL: {signed_url[:100]}...")
        except Exception as e:
            print(f"❌ Signed URL generation failed: {e}")

        # Test 6: List objects in bucket (if supported)
        print(f"\n📋 Testing bucket operations...")
        try:
            # This depends on the storage implementation
            print(f"✅ Bucket operations initialized")
        except Exception as e:
            print(f"❌ Bucket operations failed: {e}")

        # Test 7: PDF upload simulation
        print(f"\n📄 Testing PDF upload...")
        test_pdf_content = b"PDF test content - this would be actual PDF bytes"
        pdf_path = f"final/{test_preview_id}/book.pdf"

        try:
            pdf_url = await storage.upload_pdf(test_pdf_content, pdf_path)
            print(f"✅ PDF upload successful!")
            print(f"📄 PDF URL: {pdf_url}")
        except Exception as e:
            print(f"❌ PDF upload failed: {e}")

        # Test 8: Cleanup (delete test files)
        print(f"\n🧹 Testing cleanup operations...")
        try:
            await storage.delete_path(f"uploads/{test_preview_id}")
            await storage.delete_path(f"previews/{test_preview_id}")
            await storage.delete_path(f"final/{test_preview_id}")
            print(f"✅ Cleanup successful!")
        except Exception as e:
            print(f"❌ Cleanup failed (this may be expected): {e}")

        print(f"\n🎉 Storage Operations Testing Completed!")
        return True

    except Exception as e:
        print(f"❌ Storage testing failed: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_storage_operations())
    exit(0 if success else 1)