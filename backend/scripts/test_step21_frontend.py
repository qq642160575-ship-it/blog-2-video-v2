#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Step 21 test - Frontend article input page
"""
import requests
import time

BASE_URL = "http://localhost:8000"
FRONTEND_URL = "http://localhost:3000"


def print_section(title: str) -> None:
    print()
    print("=" * 72)
    print(title)
    print("=" * 72)


def test_frontend_accessible():
    """Test if frontend is accessible"""
    print_section("1. Frontend Accessibility Test")

    try:
        response = requests.get(FRONTEND_URL, timeout=5)
        print(f"Status: {response.status_code}")

        if response.status_code == 200:
            print("✓ Frontend is accessible")
            return True
        else:
            print(f"✗ Frontend returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Cannot access frontend: {e}")
        return False


def test_create_project_api():
    """Test the POST /projects API that the frontend will call"""
    print_section("2. Create Project API Test")

    test_data = {
        "title": "前端测试文章",
        "source_type": "text",
        "content": """人工智能技术的发展正在深刻改变我们的生活方式。从智能手机到自动驾驶汽车，从医疗诊断到金融分析，AI的应用已经渗透到各个领域。这些技术的进步不仅提高了我们的工作效率，也为我们的日常生活带来了前所未有的便利。在医疗领域，AI辅助诊断系统能够帮助医生更准确地识别疾病。

机器学习作为人工智能的核心技术，通过大量数据的训练，使计算机能够自主学习和改进。深度学习的突破更是推动了图像识别、自然语言处理等领域的飞速发展。神经网络的多层结构使得机器能够理解更加复杂的模式和关系，从而在各种任务中表现出色。

然而，AI技术的发展也带来了一些挑战。数据隐私、算法偏见、就业影响等问题需要我们认真思考和应对。如何在推动技术进步的同时，确保技术的公平性和安全性，是我们面临的重要课题。我们需要建立完善的监管机制，确保AI技术的发展符合人类的根本利益。

展望未来，人工智能将继续在各个领域发挥重要作用。通过人机协作，我们可以创造出更加智能、高效的解决方案，为人类社会的发展做出更大贡献。同时，我们也需要建立完善的法律法规和伦理规范，确保AI技术的健康发展。教育和培训也将变得越来越重要，帮助人们适应AI时代的变化。这是一个充满机遇的时代。"""
    }

    print(f"Title: {test_data['title']}")
    print(f"Source Type: {test_data['source_type']}")
    print(f"Content Length: {len(test_data['content'])} 字符")

    try:
        response = requests.post(f"{BASE_URL}/projects", json=test_data)
        print(f"\nStatus: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            print(f"✓ Project created successfully")
            print(f"  Project ID: {result.get('project_id', 'N/A')}")
            print(f"  Response: {result}")
            return result.get('project_id')
        else:
            print(f"✗ API returned status {response.status_code}")
            print(f"  Response: {response.text}")
            return None
    except Exception as e:
        print(f"✗ API call failed: {e}")
        return None


def test_cors():
    """Test CORS configuration"""
    print_section("3. CORS Configuration Test")

    try:
        response = requests.options(
            f"{BASE_URL}/projects",
            headers={
                "Origin": FRONTEND_URL,
                "Access-Control-Request-Method": "POST"
            }
        )

        print(f"Status: {response.status_code}")

        cors_headers = {
            "Access-Control-Allow-Origin": response.headers.get("Access-Control-Allow-Origin"),
            "Access-Control-Allow-Methods": response.headers.get("Access-Control-Allow-Methods"),
            "Access-Control-Allow-Headers": response.headers.get("Access-Control-Allow-Headers")
        }

        print("\nCORS Headers:")
        for key, value in cors_headers.items():
            print(f"  {key}: {value}")

        if cors_headers["Access-Control-Allow-Origin"]:
            print("\n✓ CORS is configured")
        else:
            print("\n⚠ CORS may not be configured properly")

    except Exception as e:
        print(f"✗ CORS test failed: {e}")


def main():
    print_section("Step 21 - Frontend Article Input Page Test")

    print("\nFrontend URL: http://localhost:3000")
    print("Backend API URL: http://localhost:8000")

    # Test 1: Frontend accessibility
    frontend_ok = test_frontend_accessible()

    # Test 2: API functionality
    project_id = test_create_project_api()

    # Test 3: CORS
    test_cors()

    print_section("Step 21 Test Summary")

    if frontend_ok:
        print("✓ Frontend is running on http://localhost:3000")
    else:
        print("✗ Frontend is not accessible")

    if project_id:
        print("✓ POST /projects API works correctly")
    else:
        print("✗ POST /projects API has issues")

    print("\nManual Testing:")
    print("1. Open http://localhost:3000 in your browser")
    print("2. Fill in the form:")
    print("   - Title: 测试文章")
    print("   - Source Type: 文本")
    print("   - Content: (paste some text)")
    print("3. Verify word count updates as you type")
    print("4. Click '创建项目' button")
    print("5. Verify success message appears with project ID")


if __name__ == "__main__":
    main()
