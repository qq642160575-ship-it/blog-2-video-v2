#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Step 28 test - Asset management and storage
"""
import requests
import os
import tempfile
import time

BASE_URL = "http://localhost:8000"


def print_section(title: str) -> None:
    print()
    print("=" * 72)
    print(title)
    print("=" * 72)


def create_test_project(title: str) -> str:
    """Create a test project"""
    project_data = {
        "title": title,
        "content": f"测试资产管理的项目内容 - {title}。" * 50,
        "source_type": "text"
    }

    response = requests.post(f"{BASE_URL}/projects", json=project_data)
    if response.status_code == 200:
        return response.json()['project_id']
    return None


def create_test_job(project_id: str) -> str:
    """Create a test job"""
    response = requests.post(f"{BASE_URL}/projects/{project_id}/jobs/generate")
    if response.status_code == 200:
        return response.json()['job_id']
    return None


def create_test_file(content: str = "test content") -> str:
    """Create a temporary test file"""
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
        f.write(content)
        return f.name


def test_create_asset():
    """Test creating an asset record"""
    print_section("1. Test: Create Asset Record")

    # Create project and job
    project_id = create_test_project("测试资产创建")
    if not project_id:
        print("✗ Failed to create project")
        return False

    job_id = create_test_job(project_id)
    if not job_id:
        print("✗ Failed to create job")
        return False

    print(f"Created project: {project_id}")
    print(f"Created job: {job_id}")

    # Create a test file
    test_file = create_test_file("This is a test audio file")
    file_size = os.path.getsize(test_file)

    print(f"\nCreated test file: {test_file}")
    print(f"File size: {file_size} bytes")

    # Create asset record
    asset_data = {
        "project_id": project_id,
        "job_id": job_id,
        "asset_type": "audio",
        "file_path": test_file,
        "file_size": file_size,
        "mime_type": "audio/mpeg",
        "metadata": {
            "duration": 10.5,
            "sample_rate": 44100
        }
    }

    response = requests.post(f"{BASE_URL}/assets", json=asset_data)

    print(f"\nStatus: {response.status_code}")

    if response.status_code == 200:
        result = response.json()
        print(f"✓ Asset created: {result['asset_id']}")
        print(f"  Type: {result['asset_type']}")
        print(f"  Path: {result['file_path']}")
        print(f"  Size: {result['file_size']} bytes")

        # Clean up test file
        os.remove(test_file)

        return result['asset_id']
    else:
        print(f"✗ Failed to create asset: {response.text}")
        os.remove(test_file)
        return None


def test_get_asset(asset_id: str):
    """Test getting asset by ID"""
    print_section("2. Test: Get Asset by ID")

    response = requests.get(f"{BASE_URL}/assets/{asset_id}")

    print(f"Status: {response.status_code}")

    if response.status_code == 200:
        asset = response.json()
        print(f"✓ Asset retrieved: {asset['asset_id']}")
        print(f"  Project: {asset['project_id']}")
        print(f"  Job: {asset['job_id']}")
        print(f"  Type: {asset['asset_type']}")
        print(f"  Path: {asset['file_path']}")
        print(f"  Size: {asset['file_size']} bytes")
        print(f"  Deleted: {asset['is_deleted']}")
        return True
    else:
        print(f"✗ Failed to get asset: {response.text}")
        return False


def test_get_project_assets():
    """Test getting all assets for a project"""
    print_section("3. Test: Get Project Assets")

    # Create project and job
    project_id = create_test_project("测试项目资产查询")
    if not project_id:
        print("✗ Failed to create project")
        return False

    job_id = create_test_job(project_id)
    if not job_id:
        print("✗ Failed to create job")
        return False

    print(f"Created project: {project_id}")
    print(f"Created job: {job_id}")

    # Create multiple assets
    asset_types = ["audio", "subtitle", "video"]
    created_assets = []

    for asset_type in asset_types:
        test_file = create_test_file(f"Test {asset_type} content")
        asset_data = {
            "project_id": project_id,
            "job_id": job_id,
            "asset_type": asset_type,
            "file_path": test_file,
            "file_size": os.path.getsize(test_file),
            "mime_type": f"{asset_type}/test"
        }

        response = requests.post(f"{BASE_URL}/assets", json=asset_data)
        if response.status_code == 200:
            created_assets.append(response.json()['asset_id'])
            print(f"  ✓ Created {asset_type} asset")
        os.remove(test_file)

    # Get all project assets
    print(f"\nQuerying assets for project {project_id}...")
    response = requests.get(f"{BASE_URL}/projects/{project_id}/assets")

    print(f"Status: {response.status_code}")

    if response.status_code == 200:
        result = response.json()
        print(f"✓ Retrieved {result['total']} assets")
        for asset in result['assets']:
            print(f"  - {asset['asset_type']}: {asset['asset_id']}")
        return len(result['assets']) == 3
    else:
        print(f"✗ Failed to get project assets: {response.text}")
        return False


def test_get_job_assets():
    """Test getting all assets for a job"""
    print_section("4. Test: Get Job Assets")

    # Create project and job
    project_id = create_test_project("测试任务资产查询")
    if not project_id:
        print("✗ Failed to create project")
        return False

    job_id = create_test_job(project_id)
    if not job_id:
        print("✗ Failed to create job")
        return False

    print(f"Created project: {project_id}")
    print(f"Created job: {job_id}")

    # Create assets
    test_file = create_test_file("Test content")
    asset_data = {
        "project_id": project_id,
        "job_id": job_id,
        "asset_type": "video",
        "file_path": test_file,
        "file_size": os.path.getsize(test_file),
        "mime_type": "video/mp4"
    }

    response = requests.post(f"{BASE_URL}/assets", json=asset_data)
    os.remove(test_file)

    if response.status_code != 200:
        print("✗ Failed to create asset")
        return False

    # Get job assets
    print(f"\nQuerying assets for job {job_id}...")
    response = requests.get(f"{BASE_URL}/jobs/{job_id}/assets")

    print(f"Status: {response.status_code}")

    if response.status_code == 200:
        result = response.json()
        print(f"✓ Retrieved {result['total']} assets for job")
        for asset in result['assets']:
            print(f"  - {asset['asset_type']}: {asset['asset_id']}")
        return result['total'] > 0
    else:
        print(f"✗ Failed to get job assets: {response.text}")
        return False


def test_filter_by_type():
    """Test filtering assets by type"""
    print_section("5. Test: Filter Assets by Type")

    # Create project and job
    project_id = create_test_project("测试资产类型过滤")
    if not project_id:
        print("✗ Failed to create project")
        return False

    job_id = create_test_job(project_id)
    if not job_id:
        print("✗ Failed to create job")
        return False

    print(f"Created project: {project_id}")

    # Create multiple asset types
    for asset_type in ["audio", "audio", "video"]:
        test_file = create_test_file(f"Test {asset_type}")
        asset_data = {
            "project_id": project_id,
            "job_id": job_id,
            "asset_type": asset_type,
            "file_path": test_file,
            "file_size": os.path.getsize(test_file)
        }
        requests.post(f"{BASE_URL}/assets", json=asset_data)
        os.remove(test_file)

    # Filter by audio type
    print(f"\nFiltering for 'audio' assets...")
    response = requests.get(f"{BASE_URL}/projects/{project_id}/assets?asset_type=audio")

    print(f"Status: {response.status_code}")

    if response.status_code == 200:
        result = response.json()
        print(f"✓ Found {result['total']} audio assets")
        all_audio = all(asset['asset_type'] == 'audio' for asset in result['assets'])
        if all_audio and result['total'] == 2:
            print("✓ Filter working correctly")
            return True
        else:
            print("✗ Filter returned incorrect results")
            return False
    else:
        print(f"✗ Failed to filter assets: {response.text}")
        return False


def test_soft_delete():
    """Test soft deleting an asset"""
    print_section("6. Test: Soft Delete Asset")

    # Create asset
    project_id = create_test_project("测试软删除")
    job_id = create_test_job(project_id)
    test_file = create_test_file("Test content")

    asset_data = {
        "project_id": project_id,
        "job_id": job_id,
        "asset_type": "audio",
        "file_path": test_file,
        "file_size": os.path.getsize(test_file)
    }

    response = requests.post(f"{BASE_URL}/assets", json=asset_data)
    if response.status_code != 200:
        print("✗ Failed to create asset")
        os.remove(test_file)
        return False

    asset_id = response.json()['asset_id']
    print(f"Created asset: {asset_id}")

    # Soft delete
    print(f"\nSoft deleting asset...")
    response = requests.delete(f"{BASE_URL}/assets/{asset_id}")

    print(f"Status: {response.status_code}")

    if response.status_code == 200:
        result = response.json()
        print(f"✓ Asset soft deleted: {result['is_deleted']}")

        # Verify file still exists
        if os.path.exists(test_file):
            print("✓ File still exists on disk")
            os.remove(test_file)
            return True
        else:
            print("✗ File was deleted (should still exist)")
            return False
    else:
        print(f"✗ Failed to soft delete: {response.text}")
        os.remove(test_file)
        return False


def test_storage_stats():
    """Test storage statistics API"""
    print_section("7. Test: Storage Statistics")

    response = requests.get(f"{BASE_URL}/assets/storage/stats")

    print(f"Status: {response.status_code}")

    if response.status_code == 200:
        stats = response.json()
        print(f"✓ Storage stats retrieved:")
        print(f"  Total assets: {stats['total_assets']}")
        print(f"  Total size: {stats['total_size']} bytes")
        print(f"  By type:")
        for asset_type, type_stats in stats['by_type'].items():
            print(f"    - {asset_type}: {type_stats['count']} assets, {type_stats['size']} bytes")
        return True
    else:
        print(f"✗ Failed to get storage stats: {response.text}")
        return False


def main():
    print_section("Step 28 - Asset Management and Storage Test")

    print("\nThis test verifies:")
    print("  1. Asset record creation")
    print("  2. Asset retrieval by ID")
    print("  3. Project assets query")
    print("  4. Job assets query")
    print("  5. Asset filtering by type")
    print("  6. Soft delete functionality")
    print("  7. Storage statistics")

    # Test 1: Create asset
    asset_id = test_create_asset()
    test1_ok = asset_id is not None

    # Test 2: Get asset
    test2_ok = False
    if asset_id:
        test2_ok = test_get_asset(asset_id)

    # Test 3: Get project assets
    test3_ok = test_get_project_assets()

    # Test 4: Get job assets
    test4_ok = test_get_job_assets()

    # Test 5: Filter by type
    test5_ok = test_filter_by_type()

    # Test 6: Soft delete
    test6_ok = test_soft_delete()

    # Test 7: Storage stats
    test7_ok = test_storage_stats()

    print_section("Step 28 Test Summary")

    if test1_ok:
        print("✓ Asset creation works")
    else:
        print("✗ Asset creation failed")

    if test2_ok:
        print("✓ Asset retrieval works")
    else:
        print("✗ Asset retrieval failed")

    if test3_ok:
        print("✓ Project assets query works")
    else:
        print("✗ Project assets query failed")

    if test4_ok:
        print("✓ Job assets query works")
    else:
        print("✗ Job assets query failed")

    if test5_ok:
        print("✓ Asset type filtering works")
    else:
        print("✗ Asset type filtering failed")

    if test6_ok:
        print("✓ Soft delete works")
    else:
        print("✗ Soft delete failed")

    if test7_ok:
        print("✓ Storage statistics works")
    else:
        print("✗ Storage statistics failed")

    print("\nNew Features:")
    print("  • Asset model - tracks all generated files")
    print("  • AssetService - manages asset lifecycle")
    print("  • Asset APIs - CRUD operations for assets")
    print("  • File cleanup service - manages old files")
    print("  • Storage statistics - monitor disk usage")
    print("  • Soft delete - mark files as deleted without removing")

    print("\nBenefits:")
    print("  • File tracking - know what files exist and where")
    print("  • Storage management - monitor and control disk usage")
    print("  • Cleanup automation - remove old/failed job files")
    print("  • Audit trail - track file creation and deletion")
    print("  • Resource optimization - identify storage bottlenecks")

    if all([test1_ok, test2_ok, test3_ok, test4_ok, test5_ok, test6_ok, test7_ok]):
        print("\n✅ All tests passed! Asset management complete.")
    else:
        print("\n⚠ Some tests failed. Check the output above.")


if __name__ == "__main__":
    main()
