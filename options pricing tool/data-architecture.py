import pandas as pd
import sqlite3
from datetime import datetime, timedelta
import requests
from typing import List, Dict

class OptionsDataManager:
    def __init__(self, db_path: str, api_key: str):
        self.db_path = db_path
        self.api_key = api_key
        self.initialize_database()
        
    def initialize_database(self):
        """Create necessary database tables if they don't exist"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create tables for different data types
        cursor.executescript("""
            CREATE TABLE IF NOT EXISTS underlying_prices (
                symbol TEXT,
                date DATE,
                price REAL,
                volume INTEGER,
                updated_at TIMESTAMP,
                PRIMARY KEY (symbol, date)
            );
            
            CREATE TABLE IF NOT EXISTS options_data (
                symbol TEXT,
                expiration_date DATE,
                strike_price REAL,
                option_type TEXT,
                bid REAL,
                ask REAL,
                volume INTEGER,
                open_interest INTEGER,
                implied_volatility REAL,
                delta REAL,
                gamma REAL,
                theta REAL,
                vega REAL,
                updated_at TIMESTAMP,
                PRIMARY KEY (symbol, expiration_date, strike_price, option_type)
            );
            
            CREATE TABLE IF NOT EXISTS volatility_history (
                symbol TEXT,
                date DATE,
                historical_volatility REAL,
                implied_volatility_rank REAL,
                updated_at TIMESTAMP,
                PRIMARY KEY (symbol, date)
            );
            
            CREATE TABLE IF NOT EXISTS watchlist (
                symbol TEXT PRIMARY KEY,
                last_updated TIMESTAMP,
                update_frequency INTEGER  -- in hours
            );
        """)
        conn.commit()
        conn.close()
    
    def update_data(self, symbols: List[str] = None):
        """Update data for specified symbols or entire watchlist"""
        if not symbols:
            symbols = self.get_watchlist_symbols()
            
        for symbol in symbols:
            if self.should_update(symbol):
                try:
                    # Fetch new data from API
                    options_data = self.fetch_options_data(symbol)
                    price_data = self.fetch_price_data(symbol)
                    volatility_data = self.fetch_volatility_data(symbol)
                    
                    # Store in database
                    self.store_options_data(symbol, options_data)
                    self.store_price_data(symbol, price_data)
                    self.store_volatility_data(symbol, volatility_data)
                    
                    # Update last_updated timestamp
                    self.update_last_updated(symbol)
                except Exception as e:
                    print(f"Error updating data for {symbol}: {str(e)}")
    
    def should_update(self, symbol: str) -> bool:
        """Check if symbol data needs updating based on frequency"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT last_updated, update_frequency 
            FROM watchlist 
            WHERE symbol = ?
        """, (symbol,))
        
        result = cursor.fetchone()
        conn.close()
        
        if not result:
            return True
            
        last_updated, frequency = result
        last_updated = datetime.strptime(last_updated, '%Y-%m-%d %H:%M:%S')
        return datetime.now() - last_updated > timedelta(hours=frequency)
    
    def get_data_for_analysis(self, symbol: str, lookback_days: int = 30) -> Dict:
        """Retrieve data for analysis"""
        conn = sqlite3.connect(self.db_path)
        
        # Get options data
        options_df = pd.read_sql_query("""
            SELECT * FROM options_data 
            WHERE symbol = ? 
            AND updated_at >= date('now', ?)
        """, conn, params=(symbol, f'-{lookback_days} days'))
        
        # Get price history
        price_df = pd.read_sql_query("""
            SELECT * FROM underlying_prices 
            WHERE symbol = ? 
            AND date >= date('now', ?)
        """, conn, params=(symbol, f'-{lookback_days} days'))
        
        # Get volatility history
        volatility_df = pd.read_sql_query("""
            SELECT * FROM volatility_history 
            WHERE symbol = ? 
            AND date >= date('now', ?)
        """, conn, params=(symbol, f'-{lookback_days} days'))
        
        conn.close()
        
        return {
            'options': options_df,
            'prices': price_df,
            'volatility': volatility_df
        }
    
    def add_to_watchlist(self, symbol: str, update_frequency: int = 24):
        """Add symbol to watchlist with specified update frequency"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO watchlist (symbol, last_updated, update_frequency)
            VALUES (?, datetime('now'), ?)
        """, (symbol, update_frequency))
        
        conn.commit()
        conn.close()
