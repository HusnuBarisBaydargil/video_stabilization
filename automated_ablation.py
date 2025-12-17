import cv2
import numpy as np
import os
import csv
import glob
from collections import deque
import math

try:
    from stab2 import compute_instability
    from distortion import calculate_normalized_distortion, calculate_cropping_ratio_between_videos
except ImportError:
    print("ERROR: Could not import 'stab2.py' or 'distortion.py'. Make sure they are in the same folder.")
    exit()

NUS_PATH = "your/path/to/NUS_dataset"
SBM_PATH = "your/path/to/SBMNet_dataset"
OUTPUT_CSV = "your/path/to/results/ablation_benchmark_results.csv"
TEMP_OUTPUT_DIR = "your/path/to/temp_processing"

# Constants for QStab
IMG_WIDTH = 640
IMG_HEIGHT = 480
RESIZE_SCALE = 0.05
FREQUENCY = 0.05  # 1/N

def get_mse(image_a, image_b):
    if image_a.shape != image_b.shape:
        image_b = cv2.resize(image_b, (image_a.shape[1], image_a.shape[0]))
    err = np.sum((image_a.astype("float") - image_b.astype("float")) ** 2)
    err /= float(image_a.shape[0] * image_a.shape[1] * 3)
    return err

class QStabProcessor:
    def __init__(self, adaptive_mode=True):
        self.adaptive_mode = adaptive_mode
        self.resized_queue = deque()
        self.frame_queue = deque()
        self.max_queue_size = int(1.0 / FREQUENCY)
        self.counter = 0
        self.ref_frame = None

    def process_video(self, input_path, output_path):
        cap = cv2.VideoCapture(input_path)
        if not cap.isOpened(): return False
        
        fps = cap.get(cv2.CAP_PROP_FPS)
        out = cv2.VideoWriter(output_path, cv2.VideoWriter_fourcc(*'mp4v'), fps, (IMG_WIDTH, IMG_HEIGHT))
        
        while True:
            ret, frame = cap.read()
            if not ret: break
            
            # Standardize Input
            frame = cv2.resize(frame, (IMG_WIDTH, IMG_HEIGHT))
            
            # QStab Logic
            self.counter += 1
            resized = cv2.resize(frame, (int(IMG_WIDTH * RESIZE_SCALE), int(IMG_HEIGHT * RESIZE_SCALE)))
            
            if self.counter == 1:
                self.ref_frame = resized
            
            self.resized_queue.append(resized)
            self.frame_queue.append(frame)
            
            if len(self.resized_queue) > self.max_queue_size:
                self.resized_queue.popleft()
                self.frame_queue.popleft()
            
            output_frame = frame # Default
            
            if self.counter > 1:
                min_mse = float('inf')
                best_index = 0
                min_counter_threshold = 0
                
                for i, resized_item in enumerate(self.resized_queue):
                    err = get_mse(resized_item, self.ref_frame)
                    if err < min_mse:
                        min_counter_threshold += 1
                        if min_counter_threshold > len(self.resized_queue) / 1.5:
                            min_mse = err
                            best_index = i
                
                output_frame = self.frame_queue[best_index]
                
                if self.adaptive_mode:
                    self.ref_frame = self.resized_queue[best_index]
                else:
                    pass 
            
            out.write(output_frame)
            
        cap.release()
        out.release()
        return True

# ==========================================
# 2. METRIC CALCULATION WRAPPER
# ==========================================
def calculate_metrics(original_path, stabilized_path):
    # 1. Instability / ITF
    try:
        instab_orig = compute_instability(original_path)
        instab_stab = compute_instability(stabilized_path)
        
        # Avoid div by zero
        if instab_stab == 0: instab_stab = 0.0001
        
        # ITF Formula: 10 * log10(Orig / Stab)
        itf = 10 * math.log10(instab_orig / instab_stab)
    except Exception as e:
        print(f"  Error calc stability: {e}")
        itf = 0

    # 2. Distortion
    try:
        distortion = calculate_normalized_distortion(original_path, stabilized_path)
    except:
        distortion = 0

    # 3. Cropping Ratio
    try:
        cropping = calculate_cropping_ratio_between_videos(original_path, stabilized_path)
    except:
        cropping = 0
        
    return round(itf, 4), round(distortion, 4), round(cropping, 4)

# ==========================================
# 3. AUTOMATION LOOP
# ==========================================
def process_dataset(root_path, dataset_name, csv_writer):
    # Recursively find all video files
    video_extensions = ['*.mp4', '*.mov', '*.avi']
    files = []
    for ext in video_extensions:
        files.extend(glob.glob(os.path.join(root_path, '**', ext), recursive=True))
    
    print(f"Found {len(files)} videos in {dataset_name}...")
    
    for idx, video_path in enumerate(files):
        # Determine category from folder name
        folder_name = os.path.basename(os.path.dirname(video_path))
        file_name = os.path.basename(video_path)
        
        print(f"[{idx+1}/{len(files)}] Processing {folder_name}/{file_name}...")
        
        temp_adaptive = os.path.join(TEMP_OUTPUT_DIR, "temp_adaptive.mp4")
        temp_fixed = os.path.join(TEMP_OUTPUT_DIR, "temp_fixed.mp4")
        
        processor_adaptive = QStabProcessor(adaptive_mode=True)
        processor_adaptive.process_video(video_path, temp_adaptive)
        itf_a, dist_a, crop_a = calculate_metrics(video_path, temp_adaptive)
        
        processor_fixed = QStabProcessor(adaptive_mode=False)
        processor_fixed.process_video(video_path, temp_fixed)
        itf_f, dist_f, crop_f = calculate_metrics(video_path, temp_fixed)
        
        csv_writer.writerow([
            dataset_name, folder_name, file_name,
            itf_a, itf_f,        # ITF Comparison
            dist_a, dist_f,      # Distortion Comparison
            crop_a, crop_f       # Cropping Comparison
        ])
        
        # Force flush to save progress
        print(f"   > Adaptive ITF: {itf_a} | Fixed ITF: {itf_f}")

def main():
    if not os.path.exists(TEMP_OUTPUT_DIR):
        os.makedirs(TEMP_OUTPUT_DIR)
        
    # Open CSV for writing
    with open(OUTPUT_CSV, 'w', newline='') as f:
        writer = csv.writer(f)
        # Header
        writer.writerow([
            "Dataset", "Category", "Filename", 
            "ITF_Adaptive (dB)", "ITF_Fixed (dB)", 
            "Distortion_Adaptive", "Distortion_Fixed",
            "Cropping_Adaptive", "Cropping_Fixed"
        ])
        
        # Process NUS
        if os.path.exists(NUS_PATH):
            process_dataset(NUS_PATH, "NUS", writer)
        else:
            print(f"Warning: NUS Path not found: {NUS_PATH}")
            
        # Process SBMnet
        if os.path.exists(SBM_PATH):
            process_dataset(SBM_PATH, "SBMnet", writer)
        else:
            print(f"Warning: SBM Path not found: {SBM_PATH}")

    print("\n---------------------------------------------------")
    print(f"Benchmarking Complete! Results saved to {OUTPUT_CSV}")
    print("---------------------------------------------------")

if __name__ == "__main__":
    main()