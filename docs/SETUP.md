# Setup and project structure

## Inspect the saved project without TensorFlow

```bash
git clone https://github.com/Andres-Vallejo/CyclingSafety.git
cd CyclingSafety
python examples/inspect_artifacts.py
```

The inspector uses Python's standard library. It reads metadata, model configuration and model bytes without deserializing pickle files or running training/inference.

## Open the interactive maps

Open one of the HTML files under `outputs/` in a browser. The maps load external JavaScript and tiles and therefore normally need an internet connection. To serve them locally:

```bash
python -m http.server 8000 --bind 127.0.0.1
```

Then visit `http://127.0.0.1:8000/outputs/map_combined.html`. This command serves the repository on your own computer; it does not publish a hosted website.

The README uses a local coordinate plot derived from `features/map_predictions.csv`, so its preview needs no map-tile provider.

## Training and preprocessing

Create a Python environment and install the original training dependencies plus KerasTuner:

```bash
python -m venv .venv
# Windows PowerShell: .venv\Scripts\Activate.ps1
# Linux/macOS: source .venv/bin/activate
python -m pip install -r requirements.txt
```

Raw Sensor Logger recordings are not bundled. The upstream [English](../README_UPSTREAM.md) and [Spanish](../README_UPSTREAM_ES.md) overviews retain the team's dataset/Colab links. Place raw recordings under `data/raw/artificial_events/` and `data/raw/natural_events/`, then run:

```bash
python utils/combine_recordings.py --mode artificial
python utils/combine_recordings.py --mode natural
jupyter notebook notebooks/Cycling_Safety.ipynb
```

The notebook's local path setup assumes its kernel starts in the `notebooks/` directory. In Colab, provide the expected `/content/` input paths. The Kaggle identity is configurable through `KAGGLE_USERNAME` or the interactive prompt; the API token is requested rather than committed.

The tracked feature arrays do not replace the missing full `X_all_windows.npy` tensor. Recreate it from the raw recordings before running the CNN stages. The historic split has known leakage; see [REVIEW.md](REVIEW.md) before reporting new experiment results.

## ThingsBoard telemetry simulator

```bash
python -m pip install -r requirements-iot.txt
```

Copy `.env.example` to `.env` and set your own ThingsBoard device token. The simulator uses python-dotenv. Run from the repository root:

```bash
python utils/simulate_cycling_node.py
```

The simulator generates synthetic IMU/GPS messages. It does not perform neural-network inference. Its defaults follow the original ThingsBoard MQTT transport on port 1883, so this configuration is a demonstration rather than a secure production deployment. Stop with Ctrl+C.

## ESP32 prototype

Open `firmware/cyclingSafety/cyclingSafety.ino` in Arduino IDE. The matching `modelo_esp32.h` is included in the same directory.

The original sketch uses an ESP32 board package, PubSubClient, TinyGPS++, MPU6050_light, SD/SPI/Wire and TensorFlow Lite Micro headers. Its comments refer to a Chirale TensorFlow Lite Micro distribution. Confirm compatibility with that distribution's interpreter API before compilation; no board compilation was performed for this fork.

Connections declared by the sketch include GPS UART RX/TX pins 16/17 and microSD chip-select pin 5. IMU I2C uses `Wire.begin()` and the selected board's default I2C pins. Replace the WiFi and ThingsBoard placeholders locally.

The included model expects 128 samples × 6 standardized IMU channels. The firmware uses fixed normalization constants from the original project. Smartphone and MPU-6050 data differ, so matching tensor dimensions alone does not establish valid field classification. Also review the fixed-coordinate GPS fallback before collecting route data.

## Where files live

| Directory | Contents |
|---|---|
| `notebooks/` | Main experiments and Python export |
| `features/` | Stored features, metadata, split masks and tuner artifacts |
| `models/` | MLP/CNN files and TFLite export |
| `firmware/cyclingSafety/` | Arduino sketch and embedded model header |
| `utils/` | Recording preprocessing and MQTT transport demo |
| `outputs/` | Existing interactive Folium maps |
| `media/` | README figures and local prediction preview |
| `examples/` | Artifact inspector |
