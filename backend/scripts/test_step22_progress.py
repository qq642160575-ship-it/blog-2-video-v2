#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Step 22 test - Frontend generation progress page
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


def test_create_and_generate():
    """Test creating a project and starting generation"""
    print_section("1. Create Project and Start Generation")

    # Step 1: Create project
    test_data = {
        "title": "Step 22 测试文章",
        "source_type": "text",
        "content": """人工智能技术的发展正在深刻改变我们的生活方式。从智能手机到自动驾驶汽车，从医疗诊断到金融分析，AI的应用已经渗透到各个领域。这些技术的进步不仅提高了我们的工作效率，也为我们的日常生活带来了前所未有的便利。在医疗领域，AI辅助诊断系统能够帮助医生更准确地识别疾病。

机器学习作为人工智能的核心技术，通过大量数据的训练，使计算机能够自主学习和改进。深度学习的突破更是推动了图像识别、自然语言处理等领域的飞速发展。神经网络的多层结构使得机器能够理解更加复杂的模式和关系，从而在各种任务中表现出色。

然而，AI技术的发展也带来了一些挑战。数据隐私、算法偏见、就业影响等问题需要我们认真思考和应对。如何在推动技术进步的同时，确保技术的公平性和安全性，是我们面临的重要课题。我们需要建立完善的监管机制，确保AI技术的发展符合人类的根本利益。

展望未来，人工智能将继续在各个领域发挥重要作用。通过人机协作，我们可以创造出更加智能、高效的解决方案，为人类社会的发展做出更大贡献。同时，我们也需要建立完善的法律法规和伦理规范，确保AI技术的健康发展。教育和培训也将变得越来越重要，帮助人们适应AI时代的变化。这是一个充满机遇的时代。"""
    }

    print("Creating project...")
    response = requests.post(f"{BASE_URL}/projects", json=test_data)

    if response.status_code != 200:
        print(f"✗ Failed to create project: {response.text}")
        return None, None

    project_id = response.json()['project_id']
    print(f"✓ Project created: {project_id}")

    # Step 2: Start generation
    print(f"\nStarting generation job...")
    response = requests.post(f"{BASE_URL}/projects/{project_id}/jobs/generate")

    if response.status_code != 200:
        print(f"✗ Failed to start generation: {response.text}")
        return project_id, None

    job_id = response.json()['job_id']
    print(f"✓ Generation job started: {job_id}")

    return project_id, job_id


def test_poll_job_status(job_id: str, max_polls: int = 10):
    """Test polling job status"""
    print_section("2. Poll Job Status")

    print(f"Polling job {job_id} status (max {max_polls} times)...")

    for i in range(max_polls):
        response = requests.get(f"{BASE_URL}/jobs/{job_id}")

        if response.status_code != 200:
            print(f"✗ Failed to get job status: {response.text}")
            return False

        job = response.json()
        status = job['status']
        stage = job.get('stage', 'N/A')
        progress = job.get('progress', 0)

        print(f"[Poll {i+1}] Status: {status}, Stage: {stage}, Progress: {progress*100:.1f}%")

        if status == 'completed':
            print(f"\n✓ Job completed successfully")
            return True
        elif status == 'failed':
            print(f"\n✗ Job failed: {job.get('error', 'Unknown error')}")
            return False

        time.sleep(2)

    print(f"\n⚠ Job still running after {max_polls} polls")
    return True


def test_frontend_route():
    """Test if frontend route is accessible"""
    print_section("3. Frontend Route Test")

    # We can't easily test the React route without a browser,
    # but we can verify the frontend is running
    try:
        response = requests.get(FRONTEND_URL, timeout=5)
        if response.status_code == 200:
            print("✓ Frontend is accessible")
            return True
        else:
            print(f"✗ Frontend returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Cannot access frontend: {e}")
        return False


def main():
    print_section("Step 22 - Frontend Generation Progress Page Test")

    print("\nThis test will:")
    print("1. Create a project via API")
    print("2. Start a generation job via API")
    print("3. Poll the job status (simulating frontend behavior)")
    print("4. Verify frontend is accessible")

    # Test 1 & 2: Create project and start generation
    project_id, job_id = test_create_and_generate()

    if not project_id or not job_id:
        print("\n✗ Failed to create project or start generation")
        return

    # Test 3: Poll job status
    poll_success = test_poll_job_status(job_id, max_polls=10)

    # Test 4: Frontend accessibility
    frontend_ok = test_frontend_route()

    print_section("Step 22 Test Summary")

    if project_id and job_id:
        print("✓ Project creation and job start work correctly")
    else:
        print("✗ Project creation or job start failed")

    if poll_success:
        print("✓ Job status polling works correctly")
    else:
        print("✗ Job status polling has issues")

    if frontend_ok:
        print("✓ Frontend is accessible")
    else:
        print("✗ Frontend is not accessible")

    print("\nManual Testing:")
    print("1. Open http://localhost:3000 in your browser")
    print("2. Fill in the article form and submit")
    print("3. You should be redirected to /generate/{project_id}")
    print("4. Verify you see:")
    print("   - Status text (初始化中/排队中/生成中)")
    print("   - Current stage (解析文章/生成场景/生成语音/etc)")
    print("   - Progress bar updating every 2 seconds")
    print("   - Percentage text")
    print("5. Wait for completion and verify redirect to result page")


if __name__ == "__main__":
    main()
