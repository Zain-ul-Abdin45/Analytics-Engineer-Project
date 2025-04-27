# Technical Report

## 1. Problem Statement and Requirements Analysis

This project aims to process and visualize client-supplier and sonar data from client-supplier interactions.  
The system must handle potentially messy JSON-like fields, perform efficient parsing and cleaning, and generate clean metrics and visualizations for insights into parts pricing, supplier reliability, and data quality.

### Requirements:
- Ingest raw data with nested sonar result fields.
- Parse and normalize nested fields into a structured format.
- Perform Exploratory Data Analysis (EDA) to uncover patterns and clean data i,e: Units have the same values with different notations.
- Build clear visualizations to support business decision-making.

---

## 2. Data Architecture Decisions

### Data Sources:
- Primary input: Parquet file export containing client, part, country, sonar results, and metadata.

### Data Processing Pipeline:
- **Extraction:** Raw ingestion of datasets into Pandas DataFrames using DBDUCK to read Parquet files.
- **Transformation:**
  - Convert the date column into a proper, readable format for databases and Python systems.
  - Parse the `sonar_results` field from mixed formats (string, list, malformed JSON).
  - Clean missing and invalid entries (e.g., missing prices, invalid dates).
  - Normalize nested sonar entries into a flat tabular structure.
  - Perform data type conversions for fields like `price` and `date_sonar`.
- **Loading:** Processed DataFrames stored in memory for EDA and visualization.

### Key Tools:
- **DBDUCK** for data reading
- **Pandas** for data cleaning and tabular transformation
- **Matplotlib** and **Seaborn** for exploratory visualizations
- **PSQL** used for data storing and further cleaning, querying, and deep understanding for data, for example: some data contained duplicate values with minor Camel characters or all-small, so handled through queries, built & executed queries for dashboard development.
- **Apache Superset** for dashboard creation and professional BI-grade visualization
- Custom utility functions for robust parsing and chunk processing

---

## 3. Technical Implementation Details

### ETL Techniques:
- **Chunked Processing:** `process_sonar_chunks(df, chunk_size=1000)` avoids memory issues with large datasets.
- **Robust Parsing:** `parse_sonar_results()` handles varied data structures using JSON parsing, `ast.literal_eval`, and regex fallback.
- **Safe Column Selection:** Selective loading of necessary columns for analysis.
- **Type Safety:** Explicit coercion of date and numeric types to handle dirty data.

### Performance Considerations:
- **Chunked DataFrame Iteration:** Reduces memory footprint compared to loading entire sonar results at once.
- **Vectorization Potential:** Future enhancement would involve replacing `iterrows()` with `apply()` or `explode()` for faster processing.
- **Parsing Efficiency:** Multiple fallback layers ensure no sonar result is silently dropped.
- **Lazy Evaluation:** Transformations are deferred until necessary, especially for parsing steps.

---

## 4. Visualization and Dashboard Components

The visualization strategy was divided between Python-based EDA (Seaborn/Matplotlib) and a dynamic, interactive dashboard built in **Apache Superset**.

### Visualization Components:

**Visual Components Using Python's Libraries**
- **Country and Currency Distribution Bar Charts:** Show the concentration of data across geographic regions and currencies, with clear dominance of DEU/USA and EUR/USD respectively.
- **Time Series Bar Chart of Entry Volume:** Displays entry counts over the last 12 months, revealing significant spikes (notably February 2022) and operational patterns.
- **Data Quality Segmentation Chart:** Categorizes entries by quality level (unknown, high, medium, low), highlighting potential data reliability concerns with a substantial "unknown" segment.
- **Verification Status Distribution:** Compares verified vs. unverified entries, providing transparency on data validation coverage.
- **Sonar Results Distribution:** Shows the frequency of entries with specific numbers of sonar results, revealing that most entries have 0 results.
- **Unit Type Analysis:** Visualizes the distribution of measurement units across the dataset, showing standardization patterns with ST and EA as dominant units.

> **Styling Notes:** Clean, minimal styling (`sns.set_style('whitegrid')`) was chosen for professional readability in Python visualizations, while Superset dashboards used cohesive color themes (mainly choose Markt-Pilot color pallets) and interactive elements.

### Dashboard Components in Apache Superset:

1. **Geographic Distribution Dashboard**
   - World map with color intensity representing data density.
   - **Insight:** Identifies regions with high/low market coverage.

2. **Geographic Supplied Parts**
   - The bar chart shows the parts supplied per country.
   - **Insight:** Highlights where data concentration is strongest.

3. **Supplier Contribution Analysis**
   - Color-coded grid showing country-wise supplier contributions.

4. **Total Price Points**
   - KPI area chart displaying the total number of price points (e.g., 90.1k).

5. **Price Points Over Time**
   - Multi-line chart for tracking average delivery, price, and transaction counts over time.

6. **Price Points by Part**
   - Area chart showing how price points are distributed across parts.

7. **Customer Distribution per Country**
   - Pie chart highlighting customer base distribution, with Germany and USA dominating.

8. **Data Quality Absolute**
   - Horizontal bar charts showcasing country-specific data quality metrics.

9. **Contribution by Supplier**
   - Vertical bar chart quantifying major supplier contributions.

10. **Price Points by Supplier**
    - Supplier-specific price point distribution visualization.

11. **Suppliers Comparison Table**
    - Tabular representation of current vs previous supplier counts.

12. **Part Price Volatility Analysis**
    - Scatter plot indicating parts with high price volatility.

### Dashboard Interactivity:

- Time range selectors (e.g., All, 1Yr, 6Mo).
- Metric toggles for selective data viewing.
- Country and supplier selection filters.
- Consistent styling across all visual elements.
- Logarithmic scaling is used where appropriate to accommodate wide data ranges.

---

## 5. Future Enhancements and Scalability

- **Parallelized Parsing:** Integrate multiprocessing for sonar parsing at scale.
- **Real time integration** We can integrate data generators with database with any messaging tool and get our real time analysis.
- **Incremental Data Capture:** Only ingest newly available records to optimize processing, using an incremental approach.
- **Database Integration:** Load normalized data into cloud SQL warehouses (e.g., Redshift, PostgreSQL, Athena) for large-scale analytics.
- **Data Warehouse Development:** Implement a *Medallion Architecture* (bronze, silver, gold layers) for improved data lifecycle management.
- **Advanced Metrics Development:**
  - Supplier performance scoring.
- **Enhanced Visualizations:**
  - Price trend forecasting.
  - Supplier reliability indexes.
  - Competitive side-by-side supplier analysis.
  - Categorical analysis with Status and Unit.
  - Once the data is integrated with any data-storing model, we can proceed with real-time dashboarding and monitoring for dashbaords.
- **Scalability Improvements:**
  - Move from single-node Pandas to distributed frameworks like Spark.
  - Introduce data versioning and validation pipelines.

---

# End of Report
