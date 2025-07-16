import pandas as pd

# === CONFIG ===
CHUNK_COUNT = 11
CSV_OUTPUT = "../data/youtube_comments.csv"
CSV_PREFIX = "../data/youtube_comments_sentiment_chunk"

# === Merge Chunks ===
df_list = []

for i in range(1, CHUNK_COUNT + 1):
    filename = f"{CSV_PREFIX}{i}.csv"
    print(f"🔗 Reading {filename}...")
    df = pd.read_csv(filename)
    df_list.append(df)

# Concatenate all chunks
merged_df = pd.concat(df_list, ignore_index=True)

# Save to single file
merged_df.to_csv(CSV_OUTPUT, index=False)
print(f"✅ All chunks merged into {CSV_OUTPUT}")