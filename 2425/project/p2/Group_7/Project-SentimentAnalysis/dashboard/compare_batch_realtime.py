import os
import glob
import pandas as pd
from datetime import datetime

def get_csv_stats(folder):
    csv_files = glob.glob(os.path.join(folder, '*.csv'))
    if not csv_files:
        return 0, None, None
    timestamps = []
    total_records = 0
    for file in csv_files:
        df = pd.read_csv(file)
        total_records += len(df)
        if 'processed_timestamp' in df.columns:
            timestamps += list(pd.to_datetime(df['processed_timestamp'], errors='coerce').dropna())
    if not timestamps:
        return total_records, None, None
    return total_records, min(timestamps), max(timestamps)

def print_stats(mode, folder):
    total, start, end = get_csv_stats(folder)
    if total == 0 or not start or not end:
        print(f"{mode}: No data found or missing timestamps.")
        return None
    duration = (end - start).total_seconds() / 60  # minutes
    throughput = total / duration if duration > 0 else 0
    print(f"{mode} Processing:")
    print(f"  Total records: {total}")
    print(f"  Start: {start}")
    print(f"  End: {end}")
    print(f"  Duration: {duration:.2f} minutes")
    print(f"  Throughput: {throughput:.2f} records/minute\n")
    return {
        'mode': mode,
        'total': total,
        'start': start,
        'end': end,
        'duration': duration,
        'throughput': throughput
    }

if __name__ == "__main__":
    print("=== Batch vs Real-Time Processing Comparison ===\n")
    batch_folder = os.path.join("..", "batch-realtime_processing", "batch", "output")
    realtime_folder = os.path.join("..", "batch-realtime_processing", "realtime", "output")
    # If using dashboard/sentiment_output for both, adjust as needed
    dashboard_folder = os.path.join("dashboard", "sentiment_output")
    print_stats("Combined (all output)", dashboard_folder)
    print_stats("Batch", batch_folder)
    print_stats("Real-Time", realtime_folder)
