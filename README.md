# QStab: A Light-weight Video Stabilization Algorithm

This repository contains the official Python implementation for the upcoming article:

**"QStab: A Light-weight Video Stabilization Algorithm Robust to High-Frequency Perturbations"**

QStab provides a simple yet effective approach for stabilizing videos affected by jitter and high-frequency shakiness. The implementation processes an input video, generates a stabilized version, and delivers a quantitative evaluation report comparing the two.

A complete collection of side-by-side video comparisons demonstrating the algorithm's performance is available in this [Google Drive folder](https://drive.google.com/drive/folders/1btjW8XyeSq4-BwPI1L6Jg7tOk9yDETzk?usp=drive_link).

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

## Requirements

- Python 3.8+
- OpenCV
- NumPy

---

## Data Download

For reproducibility and evaluation, benchmark video datasets can be downloaded from the following sources:

- **SBMnet Dataset**: [http://pione.dinf.usherbrooke.ca/dataset](http://pione.dinf.usherbrooke.ca/dataset)  
- **NUS Dataset**: [http://liushuaicheng.org/SIGGRAPH2013/database.html](http://liushuaicheng.org/SIGGRAPH2013/database.html)

These datasets can be used to test and compare the performance of the QStab algorithm under different motion scenarios.

---

## Citation

Our article describing QStab is currently under review.  
If you use this code or find it helpful in your research, please cite it as follows:

```bibtex
@article{qstab2025,
title = {QStab: A lightweight video stabilization algorithm robust to high-frequency perturbations},
journal = {Knowledge-Based Systems},
volume = {339},
pages = {115549},
year = {2026},
issn = {0950-7051},
doi = {https://doi.org/10.1016/j.knosys.2026.115549},
url = {https://www.sciencedirect.com/science/article/pii/S0950705126002911},
author = {Ibrahim Furkan Ince and Husnu Baris Baydargil and Mustafa Eren Yıldırım and Faruk Bulut}
}
