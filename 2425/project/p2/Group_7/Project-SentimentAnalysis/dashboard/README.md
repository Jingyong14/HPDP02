# Dashboard & Visualization

This folder contains:
- `elastic_mappings.json`: Elasticsearch index mappings for sentiment data
- `kibana_visualizations.ndjson`: Exported Kibana dashboard and visualizations
- `sentiment_output/`: Output CSVs from Spark consumer (batch/real-time)
- `quick_sentiment_summary.py`: Script for quick summary of sentiment results

To visualize results:
1. Import the NDJSON file into Kibana
2. Use the data view `reddit_sentiment` with time field `processed_timestamp`
3. Explore and create visualizations in Kibana
