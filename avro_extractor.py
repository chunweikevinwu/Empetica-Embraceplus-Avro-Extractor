#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import numpy as np
import pandas as pd
from avro.datafile import DataFileReader
from avro.io import DatumReader

# ======================================================
# USER SETTINGS
# ======================================================

base_path = ""



# ======================================================
# Helper functions
# ======================================================

def make_time(timestamp_start, fs, n, timezone_offset):
    """
    timestamp_start : microseconds since epoch
    fs              : sampling frequency
    n               : number of samples
    timezone_offset : seconds
    """
    return pd.to_datetime(
        timestamp_start
        + np.arange(n) * 1e6 / fs
        + timezone_offset * 1e6,
        unit='us'
    )


def find_avro_files(session_path):
    """
    Recursively search for .avro files inside folders named 'v6'
    """
    avro_files = []

    for root, dirs, files in os.walk(session_path):

        if os.path.basename(root).lower() == 'v6':

            for file in files:
                if file.lower().endswith('.avro'):
                    avro_files.append(os.path.join(root, file))

    return sorted(avro_files)


# ======================================================
# Main loop
# ======================================================

for subject in subjects:

    for session in sessions:

        session_path = os.path.join(base_path, subject, session)

        if not os.path.exists(session_path):
            print(f"⏭ Missing session: {subject} {session}")
            continue

        sensor_files = {
            "accelerometer": "accelerometer.csv",
            "eda": "eda.csv",
            "temperature": "temperature.csv",
            "bvp": "bvp.csv",
            "steps": "steps.csv",
            "systolicPeaks": "systolicPeaks.csv"
        }

        missing_sensors = [
            sensor for sensor, fname in sensor_files.items()
            if not os.path.exists(os.path.join(session_path, fname))
            
        ]

        if len(missing_sensors) == 0:
            print(f"⏭ Already parsed: {subject} {session}")
            continue

        print("\n" + "=" * 60)
        print(f"Processing {subject} {session}")
        print("Missing:", missing_sensors)
        print("=" * 60)

        avro_files = find_avro_files(session_path)

        if len(avro_files) == 0:
            print("⚠ No avro files found.")
            continue

        print(f"Found {len(avro_files)} avro files")

        containers = {sensor: [] for sensor in missing_sensors}

        # ==================================================
        # Read avro files
        # ==================================================

        for file in avro_files:

            print("  Reading:", os.path.basename(file))

            try:
                with DataFileReader(open(file, "rb"), DatumReader()) as reader:
                    record = next(reader)

            except Exception as e:
                print("    Failed:", e)
                continue

            raw = record["rawData"]
            tz = record["timezone"]
            source_file = os.path.basename(file)

            # Accelerometer
            if "accelerometer" in missing_sensors:

                acc = raw["accelerometer"]

                if len(acc["x"]) > 0:

                    n = len(acc["x"])

                    containers["accelerometer"].append(
                        pd.DataFrame({
                            "time": make_time(
                                acc["timestampStart"],
                                acc["samplingFrequency"],
                                n,
                                tz
                            ),
                            "x": acc["x"],
                            "y": acc["y"],
                            "z": acc["z"]
                        })
                    )
            '''
            # Gyroscope
            if "gyroscope" in missing_sensors:

                gyro = raw["gyroscope"]

                if len(gyro["x"]) > 0:

                    n = len(gyro["x"])

                    containers["gyroscope"].append(
                        pd.DataFrame({
                            "time": make_time(
                                gyro["timestampStart"],
                                gyro["samplingFrequency"],
                                n,
                                tz
                            ),
                            "x": gyro["x"],
                            "y": gyro["y"],
                            "z": gyro["z"],
                            "sourceFile": source_file
                        })
                    )
                    '''

            # EDA
            if "eda" in missing_sensors:

                eda = raw["eda"]

                if len(eda["values"]) > 0:

                    n = len(eda["values"])

                    containers["eda"].append(
                        pd.DataFrame({
                            "time": make_time(
                                eda["timestampStart"],
                                eda["samplingFrequency"],
                                n,
                                tz
                            ),
                            "eda": eda["values"]
                        })
                    )

            # Temperature
            if "temperature" in missing_sensors:

                temp = raw["temperature"]

                if len(temp["values"]) > 0:

                    n = len(temp["values"])

                    containers["temperature"].append(
                        pd.DataFrame({
                            "time": make_time(
                                temp["timestampStart"],
                                temp["samplingFrequency"],
                                n,
                                tz
                            ),
                            "temperature": temp["values"]
                        })
                    )

            # BVP
            if "bvp" in missing_sensors:

                bvp = raw["bvp"]

                if len(bvp["values"]) > 0:

                    n = len(bvp["values"])

                    containers["bvp"].append(
                        pd.DataFrame({
                            "time": make_time(
                                bvp["timestampStart"],
                                bvp["samplingFrequency"],
                                n,
                                tz
                            ),
                            "bvp": bvp["values"]
                           
                        })
                    )

            # Steps
            if "steps" in missing_sensors:

                steps = raw["steps"]

                if len(steps["values"]) > 0:

                    n = len(steps["values"])

                    containers["steps"].append(
                        pd.DataFrame({
                            "time": make_time(
                                steps["timestampStart"],
                                steps["samplingFrequency"],
                                n,
                                tz
                            ),
                            "steps": steps["values"]
                            
                        })
                    )

            # Ambient Light
            '''
            if "ambientLight" in missing_sensors:

                ambient = raw["ambientLight"]

                if len(ambient["values"]) > 0:

                    n = len(ambient["values"])

                    containers["ambientLight"].append(
                        pd.DataFrame({
                            "time": make_time(
                                ambient["timestampStart"],
                                ambient["samplingFrequency"],
                                n,
                                tz
                            ),
                            "ambientLight": ambient["values"],
                            "sourceFile": source_file
                        })
                    )
                    '''

            # Systolic Peaks
            if "systolicPeaks" in missing_sensors:

                peaks = raw["systolicPeaks"]["peaksTimeNanos"]

                if len(peaks) > 0:

                    containers["systolicPeaks"].append(
                        pd.DataFrame({
                            "time": pd.to_datetime(
                                np.array(peaks) + tz * 1e9,
                                unit='ns'
                            )
                        })
                    )

        # ==================================================
        # Save outputs
        # ==================================================

        for sensor, data_list in containers.items():

            if len(data_list) == 0:
                print(f"  No data for {sensor}")
                continue

            df = pd.concat(data_list, ignore_index=True)

            df = df.sort_values("time")

            df = df.drop_duplicates()

            save_path = os.path.join(
                session_path,
                sensor_files[sensor]
            )

            df.to_csv(save_path, index=False)

            print(f"  Saved {sensor_files[sensor]} ({len(df):,} rows)")

print("\nFinished.")
