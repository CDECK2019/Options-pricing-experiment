-- Core tables for options data

-- Underlying Securities
CREATE TABLE underlyings (
    underlying_id SERIAL PRIMARY KEY,
    symbol VARCHAR(10) NOT NULL,
    name VARCHAR(100),
    security_type VARCHAR(20),
    last_price DECIMAL(10,2),
    updated_at TIMESTAMP,
    UNIQUE(symbol)
);

-- Options Contracts
CREATE TABLE options_contracts (
    contract_id SERIAL PRIMARY KEY,
    underlying_id INTEGER REFERENCES underlyings(underlying_id),
    contract_symbol VARCHAR(20) NOT NULL,
    option_type CHAR(1) CHECK (option_type IN ('C', 'P')),
    strike_price DECIMAL(10,2) NOT NULL,
    expiration_date DATE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(contract_symbol)
);

-- Options Pricing (Time Series)
CREATE TABLE options_pricing (
    pricing_id SERIAL PRIMARY KEY,
    contract_id INTEGER REFERENCES options_contracts(contract_id),
    timestamp TIMESTAMP NOT NULL,
    bid DECIMAL(10,2),
    ask DECIMAL(10,2),
    last_price DECIMAL(10,2),
    volume INTEGER,
    open_interest INTEGER,
    implied_volatility DECIMAL(10,4),
    delta DECIMAL(10,4),
    gamma DECIMAL(10,4),
    theta DECIMAL(10,4),
    vega DECIMAL(10,4),
    rho DECIMAL(10,4)
);

-- Historical Volatility Data
CREATE TABLE historical_volatility (
    volatility_id SERIAL PRIMARY KEY,
    underlying_id INTEGER REFERENCES underlyings(underlying_id),
    date DATE NOT NULL,
    hv_10_day DECIMAL(10,4),
    hv_20_day DECIMAL(10,4),
    hv_30_day DECIMAL(10,4),
    hv_60_day DECIMAL(10,4),
    hv_90_day DECIMAL(10,4)
);

-- Saved Screens/Filters
CREATE TABLE saved_screens (
    screen_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    filter_config JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX idx_options_contracts_expiration ON options_contracts(expiration_date);
CREATE INDEX idx_options_pricing_timestamp ON options_pricing(timestamp);
CREATE INDEX idx_options_pricing_contract ON options_pricing(contract_id);
CREATE INDEX idx_historical_volatility_date ON historical_volatility(date);
