"""Inspect saved project artifacts with the Python standard library only."""

import collections
import csv
import hashlib
import json
import re
import zipfile
from pathlib import Path


def inspect(root):
    with (root / "features/meta_mlp.csv").open(encoding="utf-8") as f:
        metadata = list(csv.DictReader(f))
    split_report = {}
    for paradigm in ("heuristic", "supervised"):
        field = "split_" + paradigm
        routes = {
            split: {row["route"] for row in metadata if row[field] == split}
            for split in ("train", "val", "test")
        }
        split_report[paradigm] = {
            "window_counts": dict(collections.Counter(row[field] for row in metadata)),
            "shared_train_test_recordings": len(routes["train"] & routes["test"]),
        }

    parent_splits = collections.Counter(
        metadata[int(float(row["orig_idx"]))]["split_supervised"]
        for row in metadata if row["source"] == "artificial_aug"
    )
    with (root / "features/map_predictions.csv").open(encoding="utf-8") as f:
        predictions = collections.Counter(row["pred_label"] for row in csv.DictReader(f))

    models = {}
    for path in sorted((root / "models").rglob("*.keras")):
        with zipfile.ZipFile(path) as archive:
            config = json.loads(archive.read("config.json"))
        layers = config.get("config", {}).get("layers", [])
        inputs = [layer["config"].get("batch_shape") for layer in layers if layer["class_name"] == "InputLayer"]
        models[path.relative_to(root).as_posix()] = {"input_shapes": inputs, "bytes": path.stat().st_size}

    tflite = (root / "models/cnn/cnn_supervisada_esp32_int8.tflite").read_bytes()
    header = (root / "firmware/cyclingSafety/modelo_esp32.h").read_text(encoding="utf-8")
    embedded = bytes(int(value, 16) for value in re.findall(r"0x([0-9a-fA-F]{2})", header))
    sketch = (root / "firmware/cyclingSafety/cyclingSafety.ino").read_text(encoding="utf-8")
    window = int(re.search(r"const int WINDOW_SIZE\s*=\s*(\d+)", sketch).group(1))
    return {
        "metadata_rows": len(metadata),
        "sources": dict(collections.Counter(row["source"] for row in metadata)),
        "splits": split_report,
        "augmented_parent_splits": dict(parent_splits),
        "mapped_predictions": dict(predictions),
        "keras_models": models,
        "embedded_model": {
            "tflite_bytes": len(tflite),
            "sha256": hashlib.sha256(tflite).hexdigest(),
            "header_matches_tflite": embedded == tflite,
            "firmware_window_samples": window,
        },
    }


if __name__ == "__main__":
    print(json.dumps(inspect(Path(__file__).resolve().parents[1]), indent=2))
