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
