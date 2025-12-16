import cv2
import numpy as np
import os
import glob
from collections import deque

# Import your evaluation functions
from stab2 import compute_instability
from distortion import calculate_normalized_distortion, calculate_cropping_ratio_between_videos

SRC_TYPE = "video" 
TEST_VIDEO_PATH = "CMU.mov"
IMG_WIDTH = 640
IMG_HEIGHT = 480
FPS = 30
RESIZE_SCALE = 0.05
FREQUENCY = 0.05
SHAKE_THRESHOLD = 10
ORIGINAL_FRAMES_DIR = "original_frames"
STABILIZED_FRAMES_DIR = "stabilized_frames"
ORIGINAL_VIDEO_OUTPUT = "original_video.mp4"
STABILIZED_VIDEO_OUTPUT = "stabilized_video.mp4"

def get_mse(image_a, image_b):
    if len(image_a.shape) == 2: # Convert grayscale image to 3 channels if necessary
        image_a = cv2.cvtColor(image_a, cv2.COLOR_GRAY2BGR)
        image_b = cv2.cvtColor(image_b, cv2.COLOR_GRAY2BGR)
    err = np.sum((image_a.astype("float") - image_b.astype("float")) ** 2)
    err /= float(image_a.shape[0] * image_a.shape[1] * image_a.shape[2]) # Account for channel count
    return err


def vibrate_image(image, shake_amount):
    """Applies an artificial shake to an image using affine transformation."""
    h, w, _ = image.shape
    M = np.float32([[1, 0, shake_amount], [0, 1, shake_amount]])
    vibrated_image = cv2.warpAffine(image, M, (w, h))
    return vibrated_image

def compile_frames_to_video(input_dir, output_path, fps, frame_size):
    """Takes a directory of images and compiles them into a video file."""
    print(f"Compiling video from frames in '{input_dir}'...")
    
    img_files = sorted(glob.glob(os.path.join(input_dir, "*.png")))
    if not img_files:
        print(f"Error: No image files found in {input_dir}")
        return False

    fourcc = cv2.VideoWriter_fourcc(*'mp4v') 
    writer = cv2.VideoWriter(output_path, fourcc, fps, frame_size)
    for filename in img_files:
        img = cv2.imread(filename)
        if img is not None:
            writer.write(img)
    writer.release()
    print(f"Successfully created video: {output_path}")
    return True

def run_evaluation_report(original_video_path, stabilized_video_path):
    """Runs all evaluation metrics and prints a final report."""
    print("\n--- Calculating Evaluation Scores ---")

    # a) Normalized Stability Score (NSS)
    instability_original = compute_instability(original_video_path)
    instability_stabilized = compute_instability(stabilized_video_path)
    if instability_original > 0:
        nss = 1 - (instability_stabilized / instability_original)
    else:
        nss = 0 # Cannot calculate if original instability is zero
    nss = max(0, min(1, nss))

    # b) Normalized Distortion Score
    distortion_score = calculate_normalized_distortion(original_video_path, stabilized_video_path)

    # c) Cropping Ratio
    cropping_ratio = calculate_cropping_ratio_between_videos(original_video_path, stabilized_video_path)

    print("\n=============================================")
    print("   VIDEO STABILIZATION EVALUATION REPORT   ")
    print("=============================================")
    print(f"Normalized Stability Score (NSS): {nss:.4f}")
    print(f"Normalized Distortion Score:      {distortion_score:.4f}")
    print(f"Cropping Ratio:                   {cropping_ratio:.4f}")
    print("=============================================\n")


def main():
    """Main function to run stabilization and evaluation."""
    os.makedirs(ORIGINAL_FRAMES_DIR, exist_ok=True)
    os.makedirs(STABILIZED_FRAMES_DIR, exist_ok=True)

    cap = cv2.VideoCapture(TEST_VIDEO_PATH)
    if not cap.isOpened():
        print(f"Error: Could not open video file at {TEST_VIDEO_PATH}")
        return

    video_fps = cap.get(cv2.CAP_PROP_FPS)

    # Deque and state variable setup
    resized_queue, frame_queue = deque(), deque()
    max_queue_size = int(1.0 / FREQUENCY)
    counter, is_paused, ref_frame, output_frame = 0, False, None, None

    print("Starting stabilization. Press 'q' in the window to quit and see the report.")
    
    while True:
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'): break
        if key == 13: is_paused = not is_paused
        if is_paused: continue

        ret, frame = cap.read()
        if not ret: break

        curr_frame = cv2.resize(frame, (IMG_WIDTH, IMG_HEIGHT))
        
        rnd = np.random.randint(-SHAKE_THRESHOLD, SHAKE_THRESHOLD)
        vibrated_frame = vibrate_image(curr_frame, rnd)
        resized = cv2.resize(vibrated_frame, (int(IMG_WIDTH * RESIZE_SCALE), int(IMG_HEIGHT * RESIZE_SCALE)))
        counter += 1
        if counter == 1:
            ref_frame, output_frame = resized, vibrated_frame
        
        resized_queue.append(resized)
        frame_queue.append(vibrated_frame)
        if len(resized_queue) > max_queue_size:
            resized_queue.popleft()
            frame_queue.popleft()

        if counter > 1:
            min_mse, best_index, min_counter_threshold = float('inf'), 0, 0
            for i, resized_item in enumerate(resized_queue):
                err = get_mse(resized_item, ref_frame)
                if err < min_mse:
                    min_counter_threshold += 1
                    if min_counter_threshold > len(resized_queue) / 1.5:
                        min_mse, best_index = err, i
            output_frame = frame_queue[best_index]
            ref_frame = resized_queue[best_index]
        
        cv2.imwrite(os.path.join(ORIGINAL_FRAMES_DIR, f"{counter:04d}.png"), vibrated_frame)
        cv2.imwrite(os.path.join(STABILIZED_FRAMES_DIR, f"{counter:04d}.png"), output_frame)

        combined_view = np.hstack([vibrated_frame, output_frame])
        cv2.putText(combined_view, "Original", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        cv2.putText(combined_view, "Stabilized", (IMG_WIDTH + 10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        cv2.imshow("Video Stabilization", combined_view)

    cap.release()
    cv2.destroyAllWindows()

    # --- Post-processing and evaluation ---
    frame_size = (IMG_WIDTH, IMG_HEIGHT)
    
    # Compile videos and then run the report
    original_created = compile_frames_to_video(ORIGINAL_FRAMES_DIR, ORIGINAL_VIDEO_OUTPUT, video_fps, frame_size)
    stabilized_created = compile_frames_to_video(STABILIZED_FRAMES_DIR, STABILIZED_VIDEO_OUTPUT, video_fps, frame_size)
    if original_created and stabilized_created:
        run_evaluation_report(ORIGINAL_VIDEO_OUTPUT, STABILIZED_VIDEO_OUTPUT)
    else:
        print("Could not run evaluation because one or both videos failed to compile.")


if __name__ == "__main__":

    main()

