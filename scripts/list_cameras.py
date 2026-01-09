"""Utility script to list all available cameras."""

import cv2

def list_cameras(max_test=10):
    """
    Test camera indices from 0 to max_test and list available cameras.

    Args:
        max_test: Maximum camera index to test
    """
    available_cameras = []

    print("Searching for cameras...")
    print("-" * 50)

    for i in range(max_test):
        cap = cv2.VideoCapture(i)
        if cap.isOpened():
            # Try to read a frame to confirm it's working
            ret, frame = cap.read()
            if ret:
                # Get camera properties
                width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                fps = int(cap.get(cv2.CAP_PROP_FPS))

                available_cameras.append(i)
                print(f"✓ Camera {i}: AVAILABLE")
                print(f"  Resolution: {width}x{height}")
                print(f"  FPS: {fps}")
                print()
            cap.release()

    print("-" * 50)
    if available_cameras:
        print(f"Found {len(available_cameras)} camera(s): {available_cameras}")
        print(f"\nTo use a camera, set 'device_index' in config/config.yaml")
        print(f"Example: device_index: {available_cameras[0]}")
    else:
        print("No cameras found!")
        print("Possible issues:")
        print("  - Camera is being used by another application")
        print("  - Camera permissions not granted")
        print("  - No camera connected")

if __name__ == "__main__":
    list_cameras()
