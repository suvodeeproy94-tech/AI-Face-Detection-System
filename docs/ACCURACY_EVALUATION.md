# Accuracy Evaluation Guide

This document explains how to prove face detection accuracy properly.

## Why Accuracy Testing Is Needed

The live dashboard shows confidence scores from the model. That is useful, but
it is not the same as final project accuracy.

To prove accuracy, the system must be tested on images where the correct face
locations are already known.

## Required Annotation Format

Create a CSV file with this format:

```csv
image_path,x,y,width,height
datasets/sample_images/person_01.jpg,120,80,90,110
datasets/sample_images/group_01.jpg,40,65,70,80
datasets/sample_images/group_01.jpg,180,60,75,85
```

Each row means:

| Column | Meaning |
|---|---|
| `image_path` | Image path from the project root |
| `x` | Left position of the real face box |
| `y` | Top position of the real face box |
| `width` | Width of the real face box |
| `height` | Height of the real face box |

If one image has three faces, write three rows for that image.

## How Accuracy Is Calculated

The script uses IoU, which means Intersection over Union.

Simple meaning:

```text
IoU checks how much the predicted face box overlaps the real face box.
```

A prediction is counted as correct when:

```text
IoU >= 0.5
```

Accuracy formula:

```text
Accuracy = Correct Detections / Total Real Faces * 100
```

Precision formula:

```text
Precision = Correct Detections / Total Predicted Faces * 100
```

## Run Evaluation

From the project root:

```bash
python scripts/evaluate_accuracy.py --annotations datasets/sample_annotations.csv
```

Custom annotation file:

```bash
python scripts/evaluate_accuracy.py --annotations datasets/my_test_annotations.csv
```

Custom IoU threshold:

```bash
python scripts/evaluate_accuracy.py --annotations datasets/my_test_annotations.csv --iou-threshold 0.5
```

## Output Report

The script creates:

```text
reports/accuracy_report.json
```

The report includes:

- Total images tested
- Total real faces
- Correct detections
- Missed faces
- Wrong detections
- Detection accuracy
- Precision
- Whether 95% target was achieved

## Current Project Result

The current project has measured accuracy reports. The best measured result is:

```text
91.15% detection accuracy on the webcam-style WIDER FACE sample.
```

So the correct project statement is:

```text
This project is complete as a working real-time face detection system,
but it does not claim 95% accuracy.
```

## Important Rule For 95%

Do not write that the project has 95% accuracy until the generated report shows:

```text
"target_met": true
```

This keeps the project honest, professional, and examiner-safe.
