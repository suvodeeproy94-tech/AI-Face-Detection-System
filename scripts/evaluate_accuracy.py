"""
This script evaluates face detection accuracy on labeled images.

It reads a CSV file with real face boxes, runs the backend face detector on
each image, matches predicted boxes with real boxes, and creates a report.
"""

import argparse
import csv
import json
import sys
from collections import defaultdict
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
BACKEND_DIR = PROJECT_ROOT / "backend"
DEFAULT_ANNOTATION_FILE = PROJECT_ROOT / "datasets" / "sample_annotations.csv"
DEFAULT_REPORT_FILE = PROJECT_ROOT / "reports" / "accuracy_report.json"

sys.path.insert(0, str(BACKEND_DIR))

from services.face_detector import FaceDetector  # noqa: E402


def parse_arguments() -> argparse.Namespace:
    """Read command line options in a beginner-friendly way."""

    parser = argparse.ArgumentParser(
        description="Evaluate face detection accuracy using labeled face boxes."
    )
    parser.add_argument(
        "--annotations",
        default=str(DEFAULT_ANNOTATION_FILE),
        help="CSV file with image_path,x,y,width,height columns.",
    )
    parser.add_argument(
        "--output",
        default=str(DEFAULT_REPORT_FILE),
        help="JSON report file path.",
    )
    parser.add_argument(
        "--iou-threshold",
        default=0.5,
        type=float,
        help="Minimum IoU needed to count a detection as correct.",
    )
    return parser.parse_args()


def load_annotations(annotation_file: Path) -> dict[str, list[dict]]:
    """Load real face boxes from the annotation CSV file."""

    grouped_annotations: dict[str, list[dict]] = defaultdict(list)

    with annotation_file.open("r", encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file)

        for row in reader:
            image_path = row["image_path"].strip()
            grouped_annotations[image_path].append(
                {
                    "x": int(float(row["x"])),
                    "y": int(float(row["y"])),
                    "width": int(float(row["width"])),
                    "height": int(float(row["height"])),
                }
            )

    return dict(grouped_annotations)


def calculate_iou(first_box: dict, second_box: dict) -> float:
    """Calculate overlap between two face boxes."""

    first_right = first_box["x"] + first_box["width"]
    first_bottom = first_box["y"] + first_box["height"]
    second_right = second_box["x"] + second_box["width"]
    second_bottom = second_box["y"] + second_box["height"]

    overlap_left = max(first_box["x"], second_box["x"])
    overlap_top = max(first_box["y"], second_box["y"])
    overlap_right = min(first_right, second_right)
    overlap_bottom = min(first_bottom, second_bottom)

    overlap_width = max(0, overlap_right - overlap_left)
    overlap_height = max(0, overlap_bottom - overlap_top)
    overlap_area = overlap_width * overlap_height

    first_area = first_box["width"] * first_box["height"]
    second_area = second_box["width"] * second_box["height"]
    union_area = first_area + second_area - overlap_area

    if union_area == 0:
        return 0

    return overlap_area / union_area


def match_predictions(
    real_boxes: list[dict],
    predicted_boxes: list[dict],
    iou_threshold: float,
) -> tuple[int, int, int]:
    """Match predicted boxes with real boxes one time only."""

    matched_real_indexes: set[int] = set()
    correct_detections = 0

    for predicted_box in predicted_boxes:
        best_iou = 0
        best_real_index = None

        for real_index, real_box in enumerate(real_boxes):
            if real_index in matched_real_indexes:
                continue

            iou_score = calculate_iou(real_box, predicted_box)

            if iou_score > best_iou:
                best_iou = iou_score
                best_real_index = real_index

        if best_real_index is not None and best_iou >= iou_threshold:
            matched_real_indexes.add(best_real_index)
            correct_detections += 1

    missed_faces = len(real_boxes) - correct_detections
    wrong_detections = len(predicted_boxes) - correct_detections

    return correct_detections, missed_faces, wrong_detections


def evaluate_dataset(
    annotations: dict[str, list[dict]],
    iou_threshold: float,
) -> dict:
    """Run the detector on all labeled images and calculate final metrics."""

    detector = FaceDetector()
    image_results = []

    total_real_faces = 0
    total_correct_detections = 0
    total_missed_faces = 0
    total_wrong_detections = 0

    for relative_image_path, real_boxes in annotations.items():
        image_path = PROJECT_ROOT / relative_image_path

        try:
            detection_result = detector.detect_from_image_file(image_path)
            predicted_boxes = detection_result["faces"]
            error_message = ""
        except ValueError as error:
            predicted_boxes = []
            error_message = str(error)

        correct_detections, missed_faces, wrong_detections = match_predictions(
            real_boxes=real_boxes,
            predicted_boxes=predicted_boxes,
            iou_threshold=iou_threshold,
        )

        total_real_faces += len(real_boxes)
        total_correct_detections += correct_detections
        total_missed_faces += missed_faces
        total_wrong_detections += wrong_detections

        image_results.append(
            {
                "image_path": relative_image_path,
                "real_faces": len(real_boxes),
                "predicted_faces": len(predicted_boxes),
                "correct_detections": correct_detections,
                "missed_faces": missed_faces,
                "wrong_detections": wrong_detections,
                "error": error_message,
            }
        )

    detection_accuracy = calculate_percentage(
        total_correct_detections,
        total_real_faces,
    )
    precision = calculate_percentage(
        total_correct_detections,
        total_correct_detections + total_wrong_detections,
    )

    return {
        "model_status": detector.get_status(),
        "iou_threshold": iou_threshold,
        "total_images": len(annotations),
        "total_real_faces": total_real_faces,
        "correct_detections": total_correct_detections,
        "missed_faces": total_missed_faces,
        "wrong_detections": total_wrong_detections,
        "detection_accuracy_percent": detection_accuracy,
        "precision_percent": precision,
        "target_accuracy_percent": 95,
        "target_met": detection_accuracy >= 95,
        "image_results": image_results,
    }


def calculate_percentage(value: int, total: int) -> float:
    """Calculate a rounded percentage and avoid division by zero."""

    if total == 0:
        return 0

    return round((value / total) * 100, 2)


def save_report(report: dict, output_file: Path) -> None:
    """Save the accuracy report as a JSON file."""

    output_file.parent.mkdir(parents=True, exist_ok=True)

    with output_file.open("w", encoding="utf-8") as file:
        json.dump(report, file, indent=2)


def print_summary(report: dict, output_file: Path) -> None:
    """Print the most important report values in the terminal."""

    print("Accuracy Evaluation Completed")
    print(f"Images Tested: {report['total_images']}")
    print(f"Real Faces: {report['total_real_faces']}")
    print(f"Correct Detections: {report['correct_detections']}")
    print(f"Missed Faces: {report['missed_faces']}")
    print(f"Wrong Detections: {report['wrong_detections']}")
    print(f"Detection Accuracy: {report['detection_accuracy_percent']}%")
    print(f"Precision: {report['precision_percent']}%")
    print(f"Target Met: {report['target_met']}")
    print(f"Report Saved: {output_file}")


def main() -> None:
    """Run the full accuracy evaluation workflow."""

    arguments = parse_arguments()
    annotation_file = Path(arguments.annotations)
    output_file = Path(arguments.output)

    if not annotation_file.exists():
        print(f"Annotation file not found: {annotation_file}")
        print("Create the CSV file first, then run this script again.")
        sys.exit(1)

    annotations = load_annotations(annotation_file)
    report = evaluate_dataset(
        annotations=annotations,
        iou_threshold=arguments.iou_threshold,
    )
    save_report(report, output_file)
    print_summary(report, output_file)


if __name__ == "__main__":
    main()
