import cv2
import numpy as np

def compute_instability(video_path):
    cap = cv2.VideoCapture(video_path)
    prev_gray = None
    instability = []

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        if prev_gray is not None:
            # Calculate optical flow
            flow = cv2.calcOpticalFlowFarneback(prev_gray, gray, None, 0.5, 3, 15, 3, 5, 1.2, 0)
            # Magnitude of motion vectors
            magnitude, _ = cv2.cartToPolar(flow[..., 0], flow[..., 1])
            # Mean motion magnitude as instability
            instability.append(np.mean(magnitude))
        prev_gray = gray

    cap.release()
    return np.mean(instability)

# Paths to videos
original_video = "Created videos/badminton_ref.mov"
stabilized_video = "Created videos/badminton_stab.mov"

# Compute instability
instability_original = compute_instability(original_video)
instability_stabilized = compute_instability(stabilized_video)

# Calculate NSS
nss = 1 - (instability_stabilized / instability_original)
nss = max(0, min(1, nss))  # Clamp to [0, 1]

print(f"Normalized Stability Score (NSS): {nss:.4f}")
