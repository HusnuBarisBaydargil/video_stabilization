# QStab: A Light-weight Video Stabilization Algorithm

This repository contains the official Python implementation for the upcoming article:

**"QStab: A Light-weight Video Stabilization Algorithm Robust to High-Frequency Perturbations"**

QStab provides a simple yet effective approach for stabilizing videos affected by jitter and high-frequency shakiness. The implementation processes an input video, generates a stabilized version, and delivers a quantitative evaluation report comparing the two.

---

## Features

- Queue-based video stabilization algorithm (`QStab`)
- Real-time, side-by-side visualization of original and stabilized video
- Automatic generation of:
  - `original_video.mp4`
  - `stabilized_video.mp4`
- Automated post-processing pipeline that calculates key evaluation metrics:
  - **Normalized Stability Score (NSS)** — Measures reduction in shakiness
  - **Normalized Distortion Score** — Assesses content distortion during stabilization
  - **Cropping Ratio** — Indicates amount of cropping applied

---

## ⚙️ Requirements

- Python 3.8+
- OpenCV
- NumPy

## 📖 Citation

Our article describing QStab has been submitted to journals and is currently under review.  
If you use this code or find it helpful in your research, please cite it as follows:

```bibtex
@unpublished{qstab2025,
  author    = {Ince, Ibrahim Furkan and Baydargil, Husnu Baris and Yıldırım, Mustafa Eren and Bulut, Faruk},
  title     = {QStab: A Light-weight Video Stabilization Algorithm Robust to High-Frequency Perturbations},
  note      = {Manuscript submitted for publication},
  year      = {2025}
}
