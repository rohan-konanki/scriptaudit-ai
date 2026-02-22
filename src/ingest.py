import pandas as pd
import requests
import os
from pathlib import Path
from dotenv import load_dotenv
from cortex import CortexClient, DistanceMetric
import time

current_dir = Path(__file__).resolve().parent
env_path = current_dir.parent / '.env'
csv_path = current_dir.parent / 'data' / 'tmdb_5000_movies.csv'

load_dotenv(dotenv_path=env_path)
api_key = os.getenv("GEMINI_API_KEY")

def ingest_movies():
    print("Loading TMDB dataset...")
    df = pd.read_csv(csv_path)
    df = df.dropna(subset=['overview']).head(200)
    
    with CortexClient("localhost:50051") as db_client:
        print("Recreating 'movies' collection with 3072 dimensions...")
        db_client.recreate_collection(
            name="movies",
            dimension=3072, 
            distance_metric=DistanceMetric.COSINE
        )
            
        for index, row in df.iterrows():
            title = row['title']
            overview = row['overview']
            
            try:
                # 1. Call Gemini via raw REST API
                url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-embedding-001:embedContent?key={api_key}"
                payload = {
                    "model": "models/gemini-embedding-001",
                    "content": {"parts": [{"text": overview}]}
                }
                
                response = requests.post(url, json=payload)
                response_data = response.json()
                
                if 'embedding' not in response_data:
                    print(f"API Error on {title}: {response_data}")
                    time.sleep(1) # Prevent rate limiting
                    continue
                    
                vector = response_data['embedding']['values']
                
                # 2. Push to the Actian Vector Database
                db_client.upsert(
                    "movies", 
                    id=int(index), 
                    vector=vector, 
                    payload={"title": title, "plot": overview}
                )
                print(f"Successfully ingested: {title}")
                
            except Exception as e:
                print(f"Error processing {title}: {e}")

if __name__ == "__main__":
    ingest_movies()