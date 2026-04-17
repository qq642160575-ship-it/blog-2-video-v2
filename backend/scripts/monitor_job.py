#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import requests
import time
import sys

job_id = sys.argv[1] if len(sys.argv) > 1 else "job_d76860f3"
BASE_URL = "http://localhost:8000"

print(f"Monitoring job {job_id}...")

while True:
    try:
        response = requests.get(f"{BASE_URL}/jobs/{job_id}")
        if response.status_code == 200:
            job = response.json()
            status = job['status']
            progress = job.get('progress', 0)
            stage = job.get('stage', 'unknown')

            print(f"[{time.strftime('%H:%M:%S')}] Status: {status}, Progress: {progress:.2f}, Stage: {stage}")

            if status in ['completed', 'failed']:
                print(f"\nJob finished with status: {status}")
                if status == 'failed':
                    print(f"Error: {job.get('error', 'Unknown error')}")
                else:
                    print(f"Video URL: {job.get('video_url', 'N/A')}")
                break
        else:
            print(f"Error: {response.status_code}")
            break

    except Exception as e:
        print(f"Error: {e}")
        break

    time.sleep(5)
