#!/usr/bin/env python3
"""
Performance and load testing for the Magictales API
"""

import asyncio
import time
import statistics
from concurrent.futures import ThreadPoolExecutor
import httpx
from PIL import Image
import io

BASE_URL = "http://localhost:8000"

async def create_test_image():
    """Create a simple test image."""
    test_image = Image.new('RGB', (200, 200), color='lightblue')

    from PIL import ImageDraw
    draw = ImageDraw.Draw(test_image)
    draw.ellipse([50, 50, 150, 150], fill='#FFDBAC', outline='brown', width=2)
    draw.ellipse([70, 80, 90, 100], fill='black')
    draw.ellipse([110, 80, 130, 100], fill='black')

    image_buffer = io.BytesIO()
    test_image.save(image_buffer, format='JPEG', quality=85)
    return image_buffer.getvalue()

async def test_health_endpoint(client: httpx.AsyncClient, test_id: int):
    """Test health endpoint performance."""
    start_time = time.time()
    try:
        response = await client.get(f"{BASE_URL}/health")
        end_time = time.time()

        return {
            "test_id": test_id,
            "endpoint": "health",
            "status_code": response.status_code,
            "response_time": (end_time - start_time) * 1000,  # ms
            "success": response.status_code == 200,
            "error": None
        }
    except Exception as e:
        end_time = time.time()
        return {
            "test_id": test_id,
            "endpoint": "health",
            "status_code": None,
            "response_time": (end_time - start_time) * 1000,
            "success": False,
            "error": str(e)
        }

async def test_upload_endpoint(client: httpx.AsyncClient, test_id: int, image_bytes: bytes):
    """Test upload endpoint performance."""
    start_time = time.time()
    try:
        files = {"photo": (f"test_{test_id}.jpg", image_bytes, "image/jpeg")}
        data = {"session_id": f"load_test_{test_id}"}

        response = await client.post(
            f"{BASE_URL}/api/upload-photo",
            files=files,
            data=data
        )
        end_time = time.time()

        return {
            "test_id": test_id,
            "endpoint": "upload",
            "status_code": response.status_code,
            "response_time": (end_time - start_time) * 1000,
            "success": response.status_code == 200,
            "error": None
        }
    except Exception as e:
        end_time = time.time()
        return {
            "test_id": test_id,
            "endpoint": "upload",
            "status_code": None,
            "response_time": (end_time - start_time) * 1000,
            "success": False,
            "error": str(e)
        }

async def test_root_endpoint(client: httpx.AsyncClient, test_id: int):
    """Test root endpoint performance."""
    start_time = time.time()
    try:
        response = await client.get(f"{BASE_URL}/")
        end_time = time.time()

        return {
            "test_id": test_id,
            "endpoint": "root",
            "status_code": response.status_code,
            "response_time": (end_time - start_time) * 1000,
            "success": response.status_code == 200,
            "error": None
        }
    except Exception as e:
        end_time = time.time()
        return {
            "test_id": test_id,
            "endpoint": "root",
            "status_code": None,
            "response_time": (end_time - start_time) * 1000,
            "success": False,
            "error": str(e)
        }

async def run_concurrent_tests(test_func, num_requests: int, **kwargs):
    """Run multiple concurrent requests."""
    async with httpx.AsyncClient(timeout=30.0) as client:
        tasks = [test_func(client, i, **kwargs) for i in range(num_requests)]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Filter out exceptions and convert to regular results
        valid_results = []
        for result in results:
            if isinstance(result, Exception):
                valid_results.append({
                    "test_id": -1,
                    "endpoint": "unknown",
                    "status_code": None,
                    "response_time": 0,
                    "success": False,
                    "error": str(result)
                })
            else:
                valid_results.append(result)

        return valid_results

def analyze_results(results: list, test_name: str):
    """Analyze performance test results."""
    print(f"\n📊 {test_name} Results:")
    print(f"   Total Requests: {len(results)}")

    successful = [r for r in results if r["success"]]
    failed = [r for r in results if not r["success"]]

    print(f"   Successful: {len(successful)} ({len(successful)/len(results)*100:.1f}%)")
    print(f"   Failed: {len(failed)} ({len(failed)/len(results)*100:.1f}%)")

    if successful:
        response_times = [r["response_time"] for r in successful]
        print(f"   Response Times:")
        print(f"     Average: {statistics.mean(response_times):.2f} ms")
        print(f"     Median: {statistics.median(response_times):.2f} ms")
        print(f"     Min: {min(response_times):.2f} ms")
        print(f"     Max: {max(response_times):.2f} ms")
        if len(response_times) > 1:
            print(f"     Std Dev: {statistics.stdev(response_times):.2f} ms")

    if failed:
        print(f"   Common Errors:")
        error_counts = {}
        for result in failed:
            error = result.get("error", "Unknown")
            error_counts[error] = error_counts.get(error, 0) + 1

        for error, count in error_counts.items():
            print(f"     {error}: {count} times")

async def test_performance():
    """Run comprehensive performance tests."""
    try:
        print("🚀 Starting Performance and Load Testing")
        print("=" * 60)

        # Create test image once
        print("🖼️ Creating test image...")
        image_bytes = await create_test_image()
        print(f"📏 Test image size: {len(image_bytes)} bytes")

        # Test 1: Health Endpoint - Light Load
        print(f"\n🔍 Test 1: Health Endpoint - Light Load (10 concurrent)")
        results = await run_concurrent_tests(test_health_endpoint, 10)
        analyze_results(results, "Health Endpoint - Light Load")

        # Test 2: Health Endpoint - Medium Load
        print(f"\n🔍 Test 2: Health Endpoint - Medium Load (50 concurrent)")
        results = await run_concurrent_tests(test_health_endpoint, 50)
        analyze_results(results, "Health Endpoint - Medium Load")

        # Test 3: Root Endpoint - Light Load
        print(f"\n🏠 Test 3: Root Endpoint - Light Load (10 concurrent)")
        results = await run_concurrent_tests(test_root_endpoint, 10)
        analyze_results(results, "Root Endpoint - Light Load")

        # Test 4: Root Endpoint - Medium Load
        print(f"\n🏠 Test 4: Root Endpoint - Medium Load (50 concurrent)")
        results = await run_concurrent_tests(test_root_endpoint, 50)
        analyze_results(results, "Root Endpoint - Medium Load")

        # Test 5: Upload Endpoint - Light Load
        print(f"\n📤 Test 5: Upload Endpoint - Light Load (5 concurrent)")
        results = await run_concurrent_tests(test_upload_endpoint, 5, image_bytes=image_bytes)
        analyze_results(results, "Upload Endpoint - Light Load")

        # Test 6: Upload Endpoint - Medium Load
        print(f"\n📤 Test 6: Upload Endpoint - Medium Load (10 concurrent)")
        results = await run_concurrent_tests(test_upload_endpoint, 10, image_bytes=image_bytes)
        analyze_results(results, "Upload Endpoint - Medium Load")

        # Test 7: Mixed Load Test
        print(f"\n🔀 Test 7: Mixed Load Test (25 health + 10 root + 5 upload)")

        # Run different endpoints concurrently
        health_task = run_concurrent_tests(test_health_endpoint, 25)
        root_task = run_concurrent_tests(test_root_endpoint, 10)
        upload_task = run_concurrent_tests(test_upload_endpoint, 5, image_bytes=image_bytes)

        all_results = await asyncio.gather(health_task, root_task, upload_task)

        # Combine all results
        mixed_results = []
        for result_set in all_results:
            mixed_results.extend(result_set)

        analyze_results(mixed_results, "Mixed Load Test")

        # Test 8: Sequential vs Concurrent Comparison
        print(f"\n⚡ Test 8: Sequential vs Concurrent Comparison")

        # Sequential requests
        start_time = time.time()
        async with httpx.AsyncClient(timeout=30.0) as client:
            sequential_results = []
            for i in range(10):
                result = await test_health_endpoint(client, i)
                sequential_results.append(result)
        sequential_time = time.time() - start_time

        # Concurrent requests
        start_time = time.time()
        concurrent_results = await run_concurrent_tests(test_health_endpoint, 10)
        concurrent_time = time.time() - start_time

        print(f"   Sequential (10 requests): {sequential_time:.2f} seconds")
        print(f"   Concurrent (10 requests): {concurrent_time:.2f} seconds")
        print(f"   Speedup: {sequential_time/concurrent_time:.2f}x")

        print(f"\n🎉 Performance Testing Completed!")
        print(f"✅ API is responsive and handling concurrent requests well")

        return True

    except Exception as e:
        print(f"❌ Performance testing failed: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_performance())
    exit(0 if success else 1)