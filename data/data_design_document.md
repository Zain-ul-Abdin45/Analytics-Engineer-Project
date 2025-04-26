# Data Storage Architecture

## Overview
This document outlines the PostgreSQL database schema implemented for storing and analyzing supplier and pricing data collected via the Sonar web scraping tool. The architecture is designed to efficiently handle large volumes of pricing information while maintaining relational integrity between clients, parts, suppliers, and pricing data points.

## Database Schema

### Core Tables

1. **`clients`**
   - Primary table storing client information
   - `client_id` (varchar(50)) as primary key
   - Relationships: One-to-many with client_regions and client_part_collection_sample

2. **`parts`**
   - Master record of all parts in the system
   - `part_id` (varchar(24)) as primary key
   - Contains `unit` information (varchar(20))
   - Tracks `date_added` (timestamp)
   - Relationships: Referenced by sonar_results and client_part_collection_sample

3. **`suppliers`**
   - Repository of all supplier information
   - `supplier_id` (varchar(50)) as primary key
   - Contains `supplier_name` (varchar(100))
   - Stores `supplier_country` (varchar(3))
   - Relationships: Referenced by parsed_sonar_data

4. **`regions`**
   - Reference table for geographic regions
   - `region_id` (varchar(50)) as primary key
   - Contains `region_name` (varchar(100))
   - Relationships: Referenced by client_regions

### Relational Tables

5. **`client_regions`**
   - Maps clients to their applicable regions
   - Contains foreign keys to both `clients` and `regions`
   - Additional attributes include `country`, `currency`, and `data_quality`

6. **`client_part_collection_sample`**
   - Associates clients with their parts portfolio
   - Contains timestamps for when parts were added
   - Includes all client-specific part metadata

### Data Collection Tables

7. **`sonar_results`**
   - Raw storage of web scraping results
   - Contains `result_id` (varchar(50)) as primary key
   - Links to `part_id`, `client_id`, and `supplier_id`
   - Stores scraped price information and metadata

8. **`parsed_sonar_data`**
   - Cleaned and processed version of sonar results
   - Contains structured fields for analysis:
     - `price` (numeric(18,10))
     - `delivery` (bigint)
     - `date_sonar` (timestamp)
     - `currency` (text)
     - `status` (text)

## Data Relationships

The schema implements several one-to-many relationships:
- One client can have multiple regions (client_regions)
- One client can have multiple parts (client_part_collection_sample)
- One part can have multiple sonar results (sonar_results)
- Multiple sonar results can be processed into structured data points (parsed_sonar_data)

## Data Types and Constraints

- IDs are implemented as variable-length character strings (varchar(50))
- Timestamps include timezone information
- Country codes use standard 3-character format
- Prices are stored with high precision (numeric(18,10))
- Delivery times are stored as bigint values (days)

## ETL Process Flow

1. Raw client and part data is loaded into `clients` and `parts`
2. Sonar web scraping results are stored in `sonar_results`
3. ETL processes parse and clean this data into `parsed_sonar_data`
4. Analysis queries primarily work with the parsed data table

This database design supports the visualization dashboard by providing clean, structured data that can be efficiently queried for geographic, supplier, price, and quality analysis.

![markt_pilot](https://github.com/user-attachments/assets/3c6a6dfc-145a-491f-84d0-4c4c98cba7c6)
