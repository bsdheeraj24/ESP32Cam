"""
Test Client for AI Overtaking Safety System
Useful for testing the Python server without ESP32-CAM hardware
"""

import requests
import cv2
import numpy as np
import sys
import time
from pathlib import Path

class SafetySystemTestClient:
    def __init__(self, server_url="http://localhost:5000"):
        self.server_url = server_url
        self.session = requests.Session()
        
    def test_health_check(self):
        """Test server health endpoint"""
        print("\n[TEST 1] Server Health Check")
        print("-" * 50)
        try:
            response = self.session.get(f"{self.server_url}/health", timeout=5)
            if response.status_code == 200:
                print("✓ Server is running")
                data = response.json()
                print(f"  Method: {data.get('method', 'Unknown')}")
                print(f"  Total frames: {data.get('stats', {}).get('total_frames', 0)}")
                return True
            else:
                print(f"✗ Server returned status {response.status_code}")
                return False
        except Exception as e:
            print(f"✗ Connection failed: {e}")
            return False
    
    def test_home_endpoint(self):
        """Test home endpoint"""
        print("\n[TEST 2] Home Endpoint")
        print("-" * 50)
        try:
            response = self.session.get(f"{self.server_url}/", timeout=5)
            if response.status_code == 200:
                data = response.json()
                print("✓ Server API available")
                print(f"  Name: {data.get('name', 'Unknown')}")
                print(f"  Version: {data.get('version', 'Unknown')}")
                print(f"  Detection: {data.get('detection_method', 'Unknown')}")
                return True
            else:
                print(f"✗ Server returned status {response.status_code}")
                return False
        except Exception as e:
            print(f"✗ Connection failed: {e}")
            return False
    
    def create_test_image(self, scenario="empty"):
        """Create synthetic test images"""
        if scenario == "empty":
            # Empty road - SAFE
            img = np.ones((240, 320, 3), dtype=np.uint8) * 150
            cv2.putText(img, "SAFE ROAD", (80, 120), cv2.FONT_HERSHEY_SIMPLEX, 
                       1, (0, 255, 0), 2)
            return img
        
        elif scenario == "one_vehicle":
            # One vehicle - SAFE
            img = np.ones((240, 320, 3), dtype=np.uint8) * 100
            cv2.rectangle(img, (100, 80), (220, 160), (0, 0, 255), -1)
            cv2.putText(img, "1 Vehicle: SAFE", (50, 200), cv2.FONT_HERSHEY_SIMPLEX, 
                       0.7, (0, 255, 0), 2)
            return img
        
        elif scenario == "multiple_vehicles":
            # Multiple vehicles - NOT_SAFE
            img = np.ones((240, 320, 3), dtype=np.uint8) * 100
            # Vehicle 1
            cv2.rectangle(img, (40, 60), (130, 140), (0, 0, 255), -1)
            # Vehicle 2
            cv2.rectangle(img, (190, 80), (300, 160), (0, 0, 255), -1)
            cv2.putText(img, "Multiple: NOT SAFE", (40, 200), cv2.FONT_HERSHEY_SIMPLEX, 
                       0.7, (0, 0, 255), 2)
            return img
        
        elif scenario == "crowded":
            # Very crowded - NOT_SAFE
            img = np.ones((240, 320, 3), dtype=np.uint8) * 80
            vehicles = [(30, 50, 100, 120), (110, 60, 180, 130), 
                       (200, 70, 270, 140), (60, 150, 140, 200),
                       (160, 140, 250, 190)]
            for x1, y1, x2, y2 in vehicles:
                cv2.rectangle(img, (x1, y1), (x2, y2), (0, 0, 255), -1)
            cv2.putText(img, "Crowded: NOT SAFE", (50, 230), cv2.FONT_HERSHEY_SIMPLEX, 
                       0.6, (0, 0, 255), 2)
            return img
        
        else:
            return None
    
    def test_image_analysis(self, scenario="empty"):
        """Send test image to server"""
        print(f"\n[TEST 3] Image Analysis - Scenario: {scenario.upper()}")
        print("-" * 50)
        
        # Create test image
        img = self.create_test_image(scenario)
        if img is None:
            print(f"✗ Unknown scenario: {scenario}")
            return False
        
        # Encode as JPEG
        _, buffer = cv2.imencode('.jpg', img)
        
        try:
            # Send POST request
            response = self.session.post(
                f"{self.server_url}/analyze",
                data=buffer.tobytes(),
                timeout=15
            )
            
            if response.status_code == 200:
                data = response.json()
                status = data.get('status', 'UNKNOWN')
                print(f"✓ Analysis received")
                print(f"  Status: {status}")
                print(f"  Timestamp: {data.get('timestamp', 'N/A')}")
                print(f"  Vehicles: {data.get('vehicle_count', 0)}")
                
                # Show LED status
                if status == "SAFE":
                    print("  LED: ON  (overtaking allowed)")
                elif status == "NOT_SAFE":
                    print("  LED: OFF (do not overtake)")
                
                return True
            else:
                print(f"✗ Server returned status {response.status_code}")
                print(f"  Response: {response.text}")
                return False
                
        except requests.Timeout:
            print("✗ Request timed out (server may be processing)")
            return False
        except Exception as e:
            print(f"✗ Analysis failed: {e}")
            return False
    
    def test_statistics(self):
        """Test statistics endpoint"""
        print("\n[TEST 4] System Statistics")
        print("-" * 50)
        try:
            response = self.session.get(f"{self.server_url}/stats", timeout=5)
            if response.status_code == 200:
                data = response.json()
                print("✓ Statistics retrieved")
                print(f"  Total frames: {data.get('total_frames', 0)}")
                print(f"  Safe frames: {data.get('safe_count', 0)}")
                print(f"  Unsafe frames: {data.get('unsafe_count', 0)}")
                print(f"  Safe percentage: {data.get('safe_percentage', 0):.1f}%")
                print(f"  Detection method: {data.get('detection_method', 'Unknown')}")
                return True
            else:
                print(f"✗ Server returned status {response.status_code}")
                return False
        except Exception as e:
            print(f"✗ Failed to get statistics: {e}")
            return False
    
    def run_all_tests(self):
        """Run all tests"""
        print("\n" + "=" * 50)
        print("AI OVERTAKING SAFETY SYSTEM - TEST SUITE")
        print("=" * 50)
        
        results = []
        
        # Test 1: Health check
        results.append(("Server Health", self.test_health_check()))
        
        # Test 2: Home endpoint
        results.append(("Home Endpoint", self.test_home_endpoint()))
        
        # Test 3: Image analysis with different scenarios
        scenarios = ["empty", "one_vehicle", "multiple_vehicles", "crowded"]
        for scenario in scenarios:
            name = f"Image Analysis ({scenario})"
            success = self.test_image_analysis(scenario)
            results.append((name, success))
            time.sleep(1)  # Small delay between tests
        
        # Test 4: Statistics
        results.append(("Statistics", self.test_statistics()))
        
        # Summary
        print("\n" + "=" * 50)
        print("TEST SUMMARY")
        print("=" * 50)
        
        passed = sum(1 for _, success in results if success)
        total = len(results)
        
        for test_name, success in results:
            status = "✓ PASS" if success else "✗ FAIL"
            print(f"{status} - {test_name}")
        
        print("-" * 50)
        print(f"Result: {passed}/{total} tests passed")
        print("=" * 50 + "\n")
        
        return passed == total


def main():
    # Get server URL from command line or use default
    server_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:5000"
    
    print(f"\nTesting server at: {server_url}")
    
    client = SafetySystemTestClient(server_url)
    success = client.run_all_tests()
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
