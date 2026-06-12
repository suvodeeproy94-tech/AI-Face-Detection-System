# Reports Folder

This folder is used for generated evaluation reports.

Run the accuracy evaluation script from the project root:

```bash
python scripts/evaluate_accuracy.py --annotations datasets/sample_annotations.csv
```

The script creates:

```text
reports/accuracy_report.json
```

Generated report files are local evidence files. Review them before adding them
to GitHub.

## Current Reviewed Result

The current reviewed reports show that the best measured result is:

```text
91.15% detection accuracy on the webcam-style WIDER FACE sample.
```

So the project should be described as completed, but it should not claim 95%
accuracy.
