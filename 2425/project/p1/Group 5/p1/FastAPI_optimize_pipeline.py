from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pymongo import MongoClient
import pandas as pd
import time
import psutil

app = FastAPI()

# ---------------------------- #
# Asynchronous Data Cleaning Logic
# ---------------------------- #
async def clean_mongo_data():
    client = MongoClient("mongodb://localhost:27017/")
    db = client["mydb"]
    raw_collection = db["raw_pets"]

    raw_data = list(raw_collection.find())
    if not raw_data:
        return 0, 0, 0, {}

    for item in raw_data:
        item.pop('_id', None)

    cleaned_df = pd.DataFrame(raw_data)

    process = psutil.Process()
    start_time = time.time()
    start_cpu_times = process.cpu_times()
    start_memory = process.memory_info().rss / 1024 / 1024

    cleaned_df.replace(["", "N/A", "Not Sure"], pd.NA, inplace=True)
    cleaned_df.dropna(subset=[col for col in cleaned_df.columns if col != 'Pet ID'], how='all', inplace=True)

    str_cols = cleaned_df.select_dtypes(include='object').columns
    cleaned_df[str_cols] = cleaned_df[str_cols].apply(lambda x: x.str.strip())
    cleaned_df.drop_duplicates(inplace=True)

    if 'Profile' in cleaned_df.columns:
        profile_split = cleaned_df['Profile'].str.extract(r'(?P<Gender>[^,]+), (?P<Age>.+)')
        cleaned_df = pd.concat([cleaned_df.drop(columns=['Profile']), profile_split], axis=1)

    if 'Body' in cleaned_df.columns:
        body_split = cleaned_df['Body'].str.extract(r'(?P<Body_Size>[^,]+), (?P<Fur_Length>.+)')
        body_split.rename(columns={'Body_Size': 'Body Size', 'Fur_Length': 'Fur Length'}, inplace=True)
        cleaned_df = pd.concat([cleaned_df.drop(columns=['Body']), body_split], axis=1)

    if 'Posted' in cleaned_df.columns:
        posted_split = cleaned_df['Posted'].str.extract(r'(?P<Original>[^()]+)(?:\(Updated (?P<Updated>[^)]+)\))?')
        posted_split = posted_split.apply(lambda x: x.str.strip())

        def parse_date(date_str):
            for fmt in ('%d %b %Y', '%d-%b-%y'):
                try:
                    return pd.to_datetime(date_str, format=fmt)
                except (ValueError, TypeError):
                    continue
            return pd.NaT

        posted_split['Original Date'] = posted_split['Original'].apply(parse_date)
        posted_split['Updated Date'] = posted_split['Updated'].apply(parse_date)
        posted_split['Updated Date'] = posted_split['Updated Date'].fillna(posted_split['Original Date'])

        cleaned_df = pd.concat([cleaned_df.drop(columns=['Posted']), posted_split[['Original Date', 'Updated Date']]], axis=1)

    bool_cols = ['Vaccinated', 'Dewormed', 'Spayed']
    for col in bool_cols:
        if col in cleaned_df.columns:
            cleaned_df[col] = cleaned_df[col].map({'Yes': 1, 'No': 0}).fillna(0).astype(int)

    if 'Amount' in cleaned_df.columns:
        cleaned_df['Amount'] = (
            cleaned_df['Amount']
            .astype(str)
            .str.extract(r'(\d+)')
            .fillna(1)
            .astype(int)
        )

    if 'Price' in cleaned_df.columns:
        cleaned_df['Price'] = cleaned_df['Price'].astype(str).str.strip().str.upper()
        cleaned_df['Price'] = cleaned_df['Price'].replace('FREE', '0')
        cleaned_df['Price'] = cleaned_df['Price'].str.replace(r'^RM', '', regex=True)
        cleaned_df['Price'] = pd.to_numeric(cleaned_df['Price'], errors='coerce').fillna('Enquire')

    object_cols = cleaned_df.select_dtypes(include='object').columns
    cleaned_df[object_cols] = cleaned_df[object_cols].astype('string')

    end_time = time.time()
    end_cpu_times = process.cpu_times()
    end_memory = process.memory_info().rss / 1024 / 1024

    clean_collection = db["cleaned_pets"]
    clean_collection.delete_many({})
    clean_collection.insert_many(cleaned_df.to_dict(orient="records"))

    cpu_time_used = (end_cpu_times.user - start_cpu_times.user) + (end_cpu_times.system - start_cpu_times.system)
    elapsed_time = end_time - start_time
    cpu_usage_percent = (cpu_time_used / elapsed_time) * 100 / psutil.cpu_count()

    column_types = cleaned_df.dtypes.apply(lambda x: str(x)).to_dict()

    return elapsed_time, cpu_usage_percent, end_memory - start_memory, column_types

# ---------------------------- #
# API Endpoint: /clean-data
# ---------------------------- #
@app.get("/clean-data")
async def clean_data():
    time_taken, cpu_usage, memory_used, column_types = await clean_mongo_data()

    return JSONResponse(
        content={
            "time_taken": time_taken,
            "cpu_usage_percent": cpu_usage,
            "memory_used_MB": memory_used,
            "column_data_types": column_types
        }
    )
