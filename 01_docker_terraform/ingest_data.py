#!/usr/bin/env python
# coding: utf-8

import pandas as pd
from sqlalchemy import create_engine
import click

@click.command()
@click.option('--pg-user', default='root', help='PostgreSQL user')
@click.option('--pg-pass', default='root', help='PostgreSQL password')
@click.option('--pg-host', default='localhost', help='PostgreSQL host')
@click.option('--pg-port', default=5432, type=int, help='PostgreSQL port')
@click.option('--pg-db', default='ny_taxi', help='PostgreSQL database name')
def run(pg_user, pg_pass, pg_host, pg_port, pg_db):
    # --- HARD-CODED CONFIGURATION ---
    TAXI_FILE = 'green_tripdata_2025-11.parquet'
    ZONE_FILE = 'taxi_zone_lookup.csv'
    
    TAXI_TABLE = 'green_taxi_data'
    ZONE_TABLE = 'zones'
    # --------------------------------

    engine = create_engine(f'postgresql://{pg_user}:{pg_pass}@{pg_host}:{pg_port}/{pg_db}')
    click.echo(f"Processing hard-coded zone lookup: {ZONE_FILE}...")
    try:
        df_zones = pd.read_csv(ZONE_FILE)
        df_zones.to_sql(name=ZONE_TABLE, con=engine, if_exists='replace', index=False)
        click.echo(f"Successfully inserted {len(df_zones)} zones into table '{ZONE_TABLE}'.")
    except Exception as e:
        click.echo(f"Error processing zones: {e}")

    # --- PART 2: GREEN TAXI DATA (PARQUET) ---
    click.echo(f"Processing hard-coded taxi data: {TAXI_FILE}...")
    try:
        df_taxi = pd.read_parquet(TAXI_FILE)
        
        # Create table structure
        df_taxi.head(0).to_sql(name=TAXI_TABLE, con=engine, if_exists='replace', index=False)
        
        # Insert in chunks
        chunk_size = 100_000
        total_rows = len(df_taxi)
        
        for i in range(0, total_rows, chunk_size):
            df_chunk = df_taxi.iloc[i : i + chunk_size]
            df_chunk.to_sql(name=TAXI_TABLE, con=engine, if_exists='append', index=False)
            click.echo(f"Inserted rows {i} to {min(i + chunk_size, total_rows)} into '{TAXI_TABLE}'")
            
        click.echo("Finished taxi data ingestion.")
    except Exception as e:
        click.echo(f"Error processing taxi data: {e}")

if __name__ == '__main__':
    run()
