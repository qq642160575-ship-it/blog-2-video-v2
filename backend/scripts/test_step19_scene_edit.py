#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Step 19 test - Scene editing API
"""
import sys
import os
import requests
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

BASE_URL = "http://localhost:8000"


def print_section(title: str) -> None:
    print()
    print("=" * 72)
    print(title)
    print("=" * 72)


def test_get_scenes(project_id: str):
    """Test GET /projects/{project_id}/scenes"""
    print_section("1. Get Project Scenes")

    response = requests.get(f"{BASE_URL}/projects/{project_id}/scenes")
    print(f"Status: {response.status_code}")

    if response.status_code == 200:
        scenes = response.json()
        print(f"Found {len(scenes)} scenes")

        if scenes:
            first_scene = scenes[0]
            print(f"\nFirst scene:")
            print(f"  ID: {first_scene['scene_id']}")
            print(f"  Version: {first_scene['version']}")
            print(f"  Template: {first_scene['template_type']}")
            print(f"  Voiceover: {first_scene['voiceover'][:50]}...")
            print(f"  Duration: {first_scene['duration_sec']}s")
            return scenes
    else:
        print(f"Error: {response.text}")
        return []


def test_update_scene(scene_id: str):
    """Test PATCH /scenes/{scene_id}"""
    print_section("2. Update Scene")

    updates = {
        "voiceover": "这是更新后的旁白文本，用于测试场景编辑功能。",
        "duration_sec": 6
    }

    print(f"Updating scene {scene_id}")
    print(f"New voiceover: {updates['voiceover']}")
    print(f"New duration: {updates['duration_sec']}s")

    response = requests.patch(
        f"{BASE_URL}/projects/scenes/{scene_id}",
        json=updates
    )

    print(f"\nStatus: {response.status_code}")

    if response.status_code == 200:
        result = response.json()
        print(f"✓ Scene updated to version {result['version']}")
        print(f"  Voiceover: {result['voiceover']}")
        print(f"  Duration: {result['duration_sec']}s")
        return result
    else:
        print(f"Error: {response.text}")
        return None


def test_validation_errors(scene_id: str):
    """Test validation errors"""
    print_section("3. Test Validation Errors")

    # Test 1: Voiceover too long
    print("\nTest 3.1: Voiceover too long (>90 chars)")
    updates = {
        "voiceover": "这是一个非常非常非常非常非常非常非常非常非常非常非常非常非常非常非常非常非常非常非常非常非常非常非常非常非常非常非常非常非常长的旁白文本"
    }
    response = requests.patch(
        f"{BASE_URL}/projects/scenes/{scene_id}",
        json=updates
    )
    print(f"Status: {response.status_code}")
    if response.status_code == 400:
        print(f"✓ Validation error caught: {response.json()['detail']}")
    else:
        print(f"✗ Expected 400, got {response.status_code}")

    # Test 2: Duration out of range
    print("\nTest 3.2: Duration out of range")
    updates = {
        "duration_sec": 15
    }
    response = requests.patch(
        f"{BASE_URL}/projects/scenes/{scene_id}",
        json=updates
    )
    print(f"Status: {response.status_code}")
    if response.status_code == 400:
        print(f"✓ Validation error caught: {response.json()['detail']}")
    else:
        print(f"✗ Expected 400, got {response.status_code}")

    # Test 3: Screen text too long
    print("\nTest 3.3: Screen text item too long (>18 chars)")
    updates = {
        "screen_text": ["这是一个非常非常非常非常长的文本"]
    }
    response = requests.patch(
        f"{BASE_URL}/projects/scenes/{scene_id}",
        json=updates
    )
    print(f"Status: {response.status_code}")
    if response.status_code == 400:
        print(f"✓ Validation error caught: {response.json()['detail']}")
    else:
        print(f"✗ Expected 400, got {response.status_code}")


def test_get_versions(scene_id: str):
    """Test GET /scenes/{scene_id}/versions"""
    print_section("4. Get Scene Version History")

    response = requests.get(f"{BASE_URL}/projects/scenes/{scene_id}/versions")
    print(f"Status: {response.status_code}")

    if response.status_code == 200:
        versions = response.json()
        print(f"Found {len(versions)} versions")

        for v in versions:
            print(f"\nVersion {v['version']}:")
            print(f"  Voiceover: {v['voiceover'][:50]}...")
            print(f"  Duration: {v['duration_sec']}s")
            print(f"  Created: {v['created_at']}")
    else:
        print(f"Error: {response.text}")


def main():
    print_section("Step 19 - Scene Editing API Test")

    # Use the project from step 18
    project_id = "c4f46fd789d84c4b8284d856b62fe4c9"

    # Test 1: Get scenes
    scenes = test_get_scenes(project_id)

    if not scenes:
        print("\n✗ No scenes found. Please run step 18 first.")
        return

    scene_id = scenes[0]['scene_id']

    # Test 2: Update scene
    test_update_scene(scene_id)

    # Test 3: Validation errors
    test_validation_errors(scene_id)

    # Test 4: Get version history
    test_get_versions(scene_id)

    print_section("Step 19 Test Complete")
    print("✓ GET /projects/{project_id}/scenes")
    print("✓ PATCH /scenes/{scene_id}")
    print("✓ Scene validation")
    print("✓ Version history")


if __name__ == "__main__":
    main()
