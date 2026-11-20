# Technical review of the independent portfolio copy

This review inspected the source, stored notebook outputs, CSV metadata, NumPy array headers, Keras configuration files and TFLite schema. Models were not retrained. No numerical model inference or physical ESP32 validation was performed.

## Findings that affect interpretation

### Evaluation is window-based, not held out by ride

The notebook creates 128-sample windows with a stride of 64 and then applies stratified `train_test_split` to individual window indices. In the stored metadata, 36 natural recording IDs appear in both heuristic training and test, and all 11 controlled recording IDs appear in both supervised training and test.

The split masks do not overlap at the row-index level. However, temporal neighbors and overlapping signal windows from a recording can cross partitions. The route-level wording in some stored output titles is therefore inaccurate. Recorded accuracy and macro-F1 remain exploratory.

### Augmented samples cross the intended evaluation boundary

The saved metadata includes 2,004 augmented windows assigned to training. Their parent-window assignments are:

| Parent partition | Augmented copies in training |
|---|---:|
| Train | 1,401 |
| Validation | 300 |
| Test | 303 |

The recommended next experiment is to split recording IDs before windowing, generate augmentation only from training recordings, tune with validation and evaluate on unseen test recordings. This copy preserves the historic artifacts instead of silently changing their split or inventing replacement metrics.

### The embedded window length did not match the model

The included INT8 TFLite file has an input tensor of **[1, 128, 6]**, with type INT8, input scale approximately 0.129156 and zero point 3. Its output has shape [1, 4], scale 1/256 and zero point -128. The C header contains exactly the same 232,656 model bytes.

The original sketch collected only 120 samples before inference. The fork changes its window to 128 and adds runtime input/output checks, so the full expected input buffer is populated. It also resets the collection index on inference failure and converts the output INT8 score to a probability before publishing the `confidence` field.

The firmware is now located in `firmware/cyclingSafety/` with the embedded model header alongside it. This fixes file organization and a verified shape mismatch, but does not establish on-device performance. Tensor-arena capacity, library/API compatibility, sensor calibration and timing still need board testing.

### Host timing is not ESP32 timing

The notebook's reported 0.03 ms TFLite timing was obtained with a host interpreter using an XNNPACK CPU delegate. It is not an ESP32 latency measurement. The exact reduction percentage in the old comparison also refers to the model file chosen in that notebook cell, not automatically every Keras file currently stored under `models/`.

### Maps show predictions, not verified incident frequency

The map CSV contains 32,218 predictions. Predicted event counts and severity scores describe these model outputs; they are not ground-truth crash statistics or a validated ranking of road danger.

The firmware also retains an upstream behavior that substitutes fixed coordinates when GPS has no fix. Such records must not be treated as valid measured positions in a field study. This behavior is documented, rather than silently presented as validated geolocation.

## Reproducibility adjustments

- Added `keras-tuner` to the training requirements because the main notebook imports it.
- Added separate Paho MQTT and python-dotenv requirements for the transport simulator.
- Added an environment template and clear missing-token handling before the simulator connects.
- Replaced the notebook's fixed Kaggle username with environment configuration or a prompt, in both notebook and Python export.
- Added a standard-library artifact inspector that does not load pickle files or execute model code.
- Preserved the model weights, features, predictions, saved metrics and original license.

The simulator sends synthetic telemetry to ThingsBoard; it does not load a trained classifier. Its default transport follows the original non-TLS port 1883. The hardware uses the same transport and needs deployment-specific network hardening and offline handling for field use.

## Validation performed

The artifact inspector confirms the metadata counts, parent-split counts, Keras input shapes, firmware window and matching TFLite/header bytes. The TFLite input/output metadata was independently inspected using its FlatBuffers schema. Python syntax, command-line behavior, image files and local documentation links were checked during packaging. Full retraining requires the separate raw recordings and regeneration of `X_all_windows.npy`, which is not tracked in the repository.
