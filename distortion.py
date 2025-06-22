import cv2
import numpy as np
import os

def calculate_cropping_ratio_between_videos(original_video_path, stabilized_video_path):
    """
    Calculate the cropping ratio between an original and a stabilized video.
    """
    original_video = cv2.VideoCapture(original_video_path)
    stabilized_video = cv2.VideoCapture(stabilized_video_path)
    
    if not original_video.isOpened() or not stabilized_video.isOpened():
        raise ValueError("Could not open one of the videos.")
    
    orig_width = int(original_video.get(cv2.CAP_PROP_FRAME_WIDTH))
    orig_height = int(original_video.get(cv2.CAP_PROP_FRAME_HEIGHT))
    orig_area = orig_width * orig_height
    
    stab_width = int(stabilized_video.get(cv2.CAP_PROP_FRAME_WIDTH))
    stab_height = int(stabilized_video.get(cv2.CAP_PROP_FRAME_HEIGHT))
    stab_area = stab_width * stab_height
    
    original_video.release()
    stabilized_video.release()
    
    if orig_area == 0: return 0.0 # Avoid division by zero
    
    cropping_ratio = float(stab_area / orig_area)
    return max(0, min(1, cropping_ratio))

def calculate_normalized_distortion(original_video_path, stabilized_video_path):
    """
    Calculates the normalized distortion score in a memory-efficient way.
    """
    cap_orig = cv2.VideoCapture(original_video_path)
    cap_stab = cv2.VideoCapture(stabilized_video_path)

    if not cap_orig.isOpened() or not cap_stab.isOpened():
        raise ValueError("Could not open one or both video files for distortion calculation.")

    total_pixel_difference = 0
    total_pixels_potential_diff = 0
    
    orig_frame_shape = (
        int(cap_orig.get(cv2.CAP_PROP_FRAME_HEIGHT)),
        int(cap_orig.get(cv2.CAP_PROP_FRAME_WIDTH))
    )

    while True:
        ret_orig, frame_orig = cap_orig.read()
        ret_stab, frame_stab = cap_stab.read()

        # If either video ends, stop processing
        if not ret_orig or not ret_stab:
            break

        # Resize stabilized frame to match original frame's dimensions
        frame_stab_resized = cv2.resize(frame_stab, (orig_frame_shape[1], orig_frame_shape[0]))

        # Calculate absolute pixel difference for the current frames
        diff = cv2.absdiff(frame_orig, frame_stab_resized)
        total_pixel_difference += np.sum(diff)
        
        # The maximum possible difference is 255 (white) for each channel of each pixel
        total_pixels_potential_diff += diff.size * 255

    cap_orig.release()
    cap_stab.release()

    if total_pixels_potential_diff == 0:
        return 1.0  # If no pixels, distortion is zero, so score is 1.

    # Calculate normalized distortion score
    normalized_distortion_score = 1.0 - (total_pixel_difference / total_pixels_potential_diff)
    return normalized_distortion_score

if __name__ == "__main__":
    original_video   = "Created videos/O_MC_2_ref.mov"
    stabilized_video = "Created videos/O_MC_2.mp4"
    
    if os.path.exists(original_video) and os.path.exists(stabilized_video):
        distortion_score = calculate_normalized_distortion(original_video, stabilized_video)
        print(f"Normalized Distortion Score: {distortion_score:.4f}")

        cropping_ratio = calculate_cropping_ratio_between_videos(original_video, stabilized_video)
        print(f"Cropping Ratio: {cropping_ratio:.2f}")
    else:
        print("Example videos not found. Skipping example run.")