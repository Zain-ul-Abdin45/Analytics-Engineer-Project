# MARKT-PILOT Analytics Engineering 
---

## 📌 Problem Statement

The objective of this project was to drive meaningful insights from the provided dataset of parts pricing information.  
The focus was on exploring key patterns across dimensions such as geography, pricing, delivery times, and data completeness.

Key analytical questions included:
- How many customers or shops are active per country?
- How many price points are available per part, per shop, and per country?
- How do pricing and delivery times evolve over time?
- Which shops provide the richest or most complete datasets?
- Are there trends based on supplier or country of origin?

---

## 🛠️ Tools & Technologies Used

- **Python** (pandas, duckdb) – for data extraction, transformation, cleaning, and initial exploration.
- **PostgreSQL** – as a relational database for structured storage and querying of the cleaned dataset.
- **Apache Superset** – for creating dashboards and interactive visualizations based on the PostgreSQL database.

These tools were chosen to mimic a real-world analytics stack and ensure the scalability and reproducibility of the project.

---

## 🧠 My Approach

### 1. Data Extraction, Cleaning, Parsing, and Ingestion (Python)

I started by extracting the raw parts pricing data and preparing it for analysis:
- Used **duckdb** to quickly load and query the large Parquet datasets with a minimal memory footprint.
- Focused on cleaning critical fields like `sonar_results`, which contained nested and messy JSON-like structures.
- Performed normalization of nested columns (e.g., supplier name, prices, delivery times) for easier downstream analysis.
- Standardized missing values and handled inconsistencies across different data sources.

This phase ensured the data was accurate, reliable, and ready for structured storage.

---

### 2. Exploratory Data Analysis (Python)

With the cleaned dataset, I moved into **EDA** to understand major trends and anomalies:
- Used **pandas** and **seaborn/matplotlib** to visualize distributions, missing value patterns, and correlations.
- Focused on identifying variables of interest like `shop_country`, `delivery_time`, and `price_amount`.
- Discovered interesting patterns like skewed price distributions and varying delivery times across countries.

Due to the original dataset's large size, I needed to move into a proper data storage platform, and I used PostgreSQL as data storing, modelling and querying the data.

All EDA work is documented in Jupyter notebooks for easy reference.

---

### 3. Data Storage & Modeling (PostgreSQL)

To enable more efficient querying and dashboarding:
- I set up a **local PostgreSQL database**.
- Designed a schema that mirrored the cleaned data's logical structure.
- Imported the data into PostgreSQL tables, ensuring proper indexing for faster queries.
- Documented the database schema and setup process under `data_architecture/`.

PostgreSQL allowed me to write optimized SQL queries and integrate seamlessly with visualization tools.

---

### 4. Dashboarding and Visualization (Apache Superset)

For the final analytical layer:
- Connected **Apache Superset** to the PostgreSQL database.
- Designed a dashboard featuring multiple interconnected charts to address the key business questions.
- Visualizations included: customer/shop distribution by country, price trends over time, delivery time distributions, and data availability heatmaps.

Despite the Superset version available having some legacy limitations, I made full use of chart types like bar charts, line graphs, pie charts, and maps.

The final dashboard is provided as:
- A **PDF file** (for easy offline viewing)

<img width="1391" alt="image" src="https://github.com/user-attachments/assets/0efd5814-58a5-4bda-9802-3b20761442c4" />


---

## 🔧 Requirements

The project’s Python environment can be replicated using `requirements.txt`.  
Key packages include:
- `pandas`
- `duckdb`
- `sqlalchemy`
- `psycopg2`
- `matplotlib`
- `seaborn`

PostgreSQL installation and Superset setup are assumed to be available locally for full reproduction of the environment.


##Commands to Establish the environment (Mac Version)
Installing Homebrew to install Applications locally through the internet

`/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"`

I already had python 3.13 version running so i only had to work with virtual environment creation

`brew install pyenv`

Then, installinga  compatible version of Apache Superset 
`pyenv install 3.10.7`


Activating Environment and Installing dependable libraries:

`python -m venv venv`
`source venv/bin/activate`
`pip install pandas matplotlib seaborn apache-superset psycopg2 dbduck`


Installing Python 
For the Apache Superset capability you need to have 3.10.7 version of Python so installing command on Mac is

Installing Postgres using Homebrew
`brew install postgresql`
`brew services start postgresql`


Command to create a database

`CREATE DATABASE markt_pilot`

Initializing Superset

`superset db upgrade`

Creating a Username and Password for UI as it asks for your User and password when you launch it for the first time
So,

`export FLASK_APP=superset`
`superset fab create-admin`

It will prompt you to add a username, password, and email.

Command to launch Apache Superset

`superset run -p 8088 --with-threads --reload --debugger`

And it will be available on 
`http://localhost:8088`


---
