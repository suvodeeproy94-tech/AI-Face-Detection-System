"""
Prepare a small WIDER FACE validation sample for accuracy testing.

This script reads the official WIDER FACE validation annotation file, copies a
limited number of validation images into this project, and creates a CSV file
that can be used by scripts/evaluate_accuracy.py.
"""

import argparse
import csv
import shutil
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_IMAGE_DIR = (
    PROJECT_ROOT / "datasets" / "WIDER_FACE" / "images" / "WIDER_val_sample"
)
DEFAULT_OUTPUT_ANNOTATION_FILE = (
    PROJECT_ROOT
    / "datasets"
    / "WIDER_FACE"
    / "annotations"
    / "wider_val_sample_annotations.csv"
)


def parse_arguments() -> argparse.Namespace:
    """Read command options in a simple way."""

    parser = argparse.ArgumentParser(
        description="Create a small WIDER FACE CSV sample for accuracy testing."
    )
    parser.add_argument(
        "--source",
        required=True,
        help="Path of the downloaded WIDER FACE folder.",
    )
    parser.add_argument(
        "--limit-images",
        default=100,
        type=int,
        help="Maximum number of validation images to copy.",
    )
    parser.add_argument(
        "--minimum-face-size",
        default=40,
        type=int,
        help="Skip very small faces because webcam detection focuses on visible faces.",
    )
    parser.add_argument(
        "--output-images",
        default=str(DEFAULT_OUTPUT_IMAGE_DIR),
        help="Folder where the selected images will be copied.",
    )
    parser.add_argument(
        "--output-annotations",
        default=str(DEFAULT_OUTPUT_ANNOTATION_FILE),
        help="CSV file that will be created for accuracy evaluation.",
    )
    return parser.parse_args()


def make_project_path(path_value: str) -> Path:
    """Convert relative output paths into project paths."""

    selected_path = Path(path_value)

    if selected_path.is_absolute():
        return selected_path

    return PROJECT_ROOT / selected_path


def find_validation_annotation_file(source_folder: Path) -> Path:
    """Find the official WIDER FACE validation annotation file."""

    annotation_files = list(source_folder.rglob("wider_face_val_bbx_gt.txt"))

    if not annotation_files:
        raise FileNotFoundError(
            "Could not find wider_face_val_bbx_gt.txt inside the source folder."
        )

    return annotation_files[0]


def find_validation_images_folder(source_folder: Path, first_image_name: str) -> Path:
    """Find the folder that contains WIDER FACE validation images."""

    for images_folder in source_folder.rglob("images"):
        first_image_path = images_folder / first_image_name

        if first_image_path.exists():
            return images_folder

    raise FileNotFoundError(
        "Could not find the WIDER_val images folder inside the source folder."
    )


def read_wider_validation_boxes(
    annotation_file: Path,
    minimum_face_size: int,
    limit_images: int,
) -> list[dict]:
    """Read WIDER FACE boxes and keep a small easy-to-test validation sample."""

    selected_images = []

    with annotation_file.open("r", encoding="utf-8") as file:
        lines = [line.strip() for line in file if line.strip()]

    line_index = 0

    while line_index < len(lines) and len(selected_images) < limit_images:
        image_name = lines[line_index]
        line_index += 1

        face_count = int(lines[line_index])
        line_index += 1

        face_boxes = []

        for _ in range(face_count):
            box_values = lines[line_index].split()
            line_index += 1

            x_position = int(float(box_values[0]))
            y_position = int(float(box_values[1]))
            box_width = int(float(box_values[2]))
            box_height = int(float(box_values[3]))
            is_invalid_face = int(box_values[7]) == 1

            if is_invalid_face:
                continue

            if box_width < minimum_face_size or box_height < minimum_face_size:
                continue

            face_boxes.append(
                {
                    "x": x_position,
                    "y": y_position,
                    "width": box_width,
                    "height": box_height,
                }
            )

        if face_boxes:
            selected_images.append(
                {
                    "image_name": image_name,
                    "face_boxes": face_boxes,
                }
            )

    return selected_images


def copy_sample_images(
    selected_images: list[dict],
    source_images_folder: Path,
    output_images_folder: Path,
) -> list[dict]:
    """Copy selected images into the project and return their new paths."""

    copied_images = []

    for selected_image in selected_images:
        source_image_path = source_images_folder / selected_image["image_name"]
        destination_image_path = output_images_folder / selected_image["image_name"]

        destination_image_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source_image_path, destination_image_path)

        copied_images.append(
            {
                "image_path": destination_image_path,
                "face_boxes": selected_image["face_boxes"],
            }
        )

    return copied_images


def write_annotation_csv(copied_images: list[dict], output_file: Path) -> None:
    """Write annotation rows in the format used by evaluate_accuracy.py."""

    output_file.parent.mkdir(parents=True, exist_ok=True)

    with output_file.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=["image_path", "x", "y", "width", "height"],
        )
        writer.writeheader()

        for copied_image in copied_images:
            relative_image_path = copied_image["image_path"].relative_to(PROJECT_ROOT)

            for face_box in copied_image["face_boxes"]:
                writer.writerow(
                    {
                        "image_path": relative_image_path.as_posix(),
                        "x": face_box["x"],
                        "y": face_box["y"],
                        "width": face_box["width"],
                        "height": face_box["height"],
                    }
                )


def print_summary(
    copied_images: list[dict],
    output_images_folder: Path,
    output_annotation_file: Path,
) -> None:
    """Show the final result in the terminal."""

    total_faces = sum(len(image["face_boxes"]) for image in copied_images)

    print("WIDER FACE sample prepared successfully")
    print(f"Images copied: {len(copied_images)}")
    print(f"Face boxes saved: {total_faces}")
    print(f"Images folder: {output_images_folder}")
    print(f"Annotation CSV: {output_annotation_file}")
    print("")
    print("Next command:")
    print(
        "python scripts\\evaluate_accuracy.py "
        f"--annotations {output_annotation_file.relative_to(PROJECT_ROOT)}"
    )


def main() -> None:
    """Run the full sample preparation workflow."""

    arguments = parse_arguments()
    source_folder = Path(arguments.source)
    output_images_folder = make_project_path(arguments.output_images)
    output_annotation_file = make_project_path(arguments.output_annotations)

    if not source_folder.exists():
        print(f"Source folder not found: {source_folder}")
        sys.exit(1)

    annotation_file = find_validation_annotation_file(source_folder)

    selected_images = read_wider_validation_boxes(
        annotation_file=annotation_file,
        minimum_face_size=arguments.minimum_face_size,
        limit_images=arguments.limit_images,
    )

    if not selected_images:
        print("No valid validation images found for the selected settings.")
        sys.exit(1)

    source_images_folder = find_validation_images_folder(
        source_folder=source_folder,
        first_image_name=selected_images[0]["image_name"],
    )

    copied_images = copy_sample_images(
        selected_images=selected_images,
        source_images_folder=source_images_folder,
        output_images_folder=output_images_folder,
    )

    write_annotation_csv(
        copied_images=copied_images,
        output_file=output_annotation_file,
    )

    print_summary(
        copied_images=copied_images,
        output_images_folder=output_images_folder,
        output_annotation_file=output_annotation_file,
    )


if __name__ == "__main__":
    main()
