# EMBRACEPLUS Avro Data Parser

A Python-based data parsing tool for processing **EMBRACEPLUS wearable device recordings**. This script automatically searches participant/session folders for `.avro` files, extracts physiological and motion sensor data, reconstructs timestamps, combines recordings chronologically, and exports each sensor into an individual `.csv` file.

## 1. Overview

EMBRACEPLUS recordings are stored in Avro format, with multiple recording segments potentially generated during a single experimental session.

This tool is designed to:
- Automatically locate `.avro` files across participant and session folders.
- Extract raw physiological and motion sensor measurements.
- Reconstruct sample timestamps using each sensor's starting timestamp and sampling frequency.
- Apply the recorded timezone offset to timestamps.
- Combine multiple Avro recordings into continuous, chronologically ordered datasets.
- Export each sensor into a separate CSV file.
- Skip sessions that have already been parsed.
- Handle missing sessions and empty sensor recordings.

## 2. Folder Structure

### Input

The script assumes the following directory structure:

```text
SPE Experiments New/
├── P1/
│   ├── S1/
│   │   ├── 2000-00-00/
│   │   │   └── [Recording Folder]/
│   │   │       └── raw data/
│   │   │           └── v6/
│   │   │               ├── recording_001.avro
│   │   │               ├── recording_002.avro
│   │   │               └── ...
│   │   ├── S2/
│   │   └── S3/
├── P2/
│   ├── S1/
│   ├── S2/
│   └── S3/
└── ...
```

The script recursively searches each session directory for folders named `v6` and processes all `.avro` files found inside them.

### Output

Parsed CSV files are saved directly into the corresponding session folder:

```text
SPE Experiments New/
├── P1/
│   ├── S1/
│   │   ├── accelerometer.csv
│   │   ├── gyroscope.csv
│   │   ├── eda.csv
│   │   ├── temperature.csv
│   │   ├── bvp.csv
│   │   ├── steps.csv
│   │   ├── ambientLight.csv
│   │   └── systolicPeaks.csv
│   ├── S2/
│   └── S3/
└── ...
```

## 3. Extracted Measurements

The script extracts the following eight data types:

| Measurement | CSV Filename | Description |
|---|---|---|
| Accelerometer | `accelerometer.csv` | Three-axis acceleration (X, Y, Z) |
| Gyroscope | `gyroscope.csv` | Three-axis angular velocity (X, Y, Z) |
| EDA | `eda.csv` | Electrodermal activity |
| Temperature | `temperature.csv` | Skin/device temperature measurement |
| BVP | `bvp.csv` | Blood volume pulse |
| Steps | `steps.csv` | Step-related measurements |
| Ambient Light | `ambientLight.csv` | Ambient light measurements |
| Systolic Peaks | `systolicPeaks.csv` | Detected systolic peak timestamps |

Each CSV contains a timestamp column. Three-axis measurements contain separate X, Y, and Z columns, while single-channel measurements contain their corresponding signal column.

A `sourceFile` column is also included to identify the original Avro recording segment for each sample.

## 4. Requirements

Python 3.9 or later is recommended.

Required packages:

```bash
pip install avro pandas numpy
```

## 5. Configuration

Before running the script, modify the base directory and participant range:

```python
base_path = "/path/to/SPE Experiments New"

subjects = [f'P{i}' for i in range(16, 40)]
sessions = ['S1', 'S2', 'S3']
```

Adjust the participant range and session names according to the dataset.

## 6. Running the Script

Run the Python script:

```bash
python avro_parser.py
```

The script will automatically:

1. Iterate through all specified participants.
2. Check for available sessions (S1, S2, S3).
3. Search recursively for `v6` directories.
4. Locate and chronologically sort Avro files.
5. Extract sensor measurements and timestamps.
6. Combine recordings belonging to the same sensor.
7. Sort the combined measurements by timestamp.
8. Export individual CSV files into the corresponding session directory.

## 7. Timestamp Reconstruction

Each sensor contains its own:
- `timestampStart`
- `samplingFrequency`
- Measurement values

Sample timestamps are reconstructed using:

\[
t_i = t_0 + \frac{i}{f_s}
\]

where:

- \(t_i\): Timestamp of sample \(i\)
- \(t_0\): Starting timestamp
- \(f_s\): Sampling frequency
- \(i\): Sample index

The original timestamps are represented in microseconds for most continuous sensor measurements. The recorded timezone offset is applied to convert timestamps to the corresponding local clock time.

Systolic peak timestamps are stored in nanoseconds and converted separately.

## 8. Data Handling

### Missing Sessions
Sessions that do not exist are automatically skipped.

### Empty Sensors
If a sensor contains no measurements, no CSV file is generated for that sensor.

### Existing Parsed Data
The script checks whether the expected CSV files already exist. If all expected files are present, the session is skipped.

If only some outputs are missing, the script processes the missing outputs without regenerating existing CSV files.

### Chronological Ordering
Measurements from different Avro segments are concatenated and sorted according to their reconstructed timestamps.

### Duplicate Records
Exact duplicate rows are removed after concatenation.

## 9. MATLAB Compatibility

The exported CSV files can be directly imported into MATLAB using `readtable`.

Example:

```matlab
% Load EDA
eda = readtable('eda.csv');

% Plot EDA
figure;
plot(eda.time, eda.eda);
xlabel('Time');
ylabel('EDA');
title('Electrodermal Activity');
grid on;
```

Example for accelerometer data:

```matlab
acc = readtable('accelerometer.csv');

figure;
plot(acc.time, acc.x);
hold on;
plot(acc.time, acc.y);
plot(acc.time, acc.z);

xlabel('Time');
ylabel('Acceleration');
legend('X', 'Y', 'Z');
title('Accelerometer');
grid on;
```

## 10. Notes and Limitations

- Each participant's session is processed independently.
- The script assumes all Avro files found within a session belong to that session.
- Timestamp reconstruction assumes the sampling frequency is valid and constant within each recording segment.
- Chronological sorting does not guarantee uninterrupted sampling. Gaps and overlaps between recording segments should be checked during downstream quality control.
- Existing CSV files are not automatically updated if the original Avro files change. Delete the relevant CSV outputs before rerunning to regenerate them.
- Empty sensors are skipped rather than exported as empty CSV files.

---

**Purpose:** Convert EMBRACEPLUS wearable Avro recordings into organized, timestamped, MATLAB-compatible CSV datasets for physiological signal processing and research analysis.
