# Python Data Engineering Pipeline (ETL)

This project implements an **end-to-end data engineering pipeline** using Python.  
It extracts user data from a public REST API, cleans and validates the data, enriches it with derived features, stores it in a relational database (SQLite), and generates meaningful business insights using SQL.

The project is designed to simulate **real-world data engineering workflows** in a Linux environment.

---

## 🚀 Features

- Extracts data from an external REST API
- Handles unreliable API calls with exception handling
- Cleans and flattens nested JSON data
- Applies strict data validation rules
- Logs pipeline execution and failures
- Stores clean data in CSV and SQLite
- Generates analytical insights using SQL
- Uses Python virtual environments for isolation
- Git version-controlled with clean `.gitignore`

---

## 🧱 Tech Stack

- **Language**: Python 3
- **Libraries**: `requests`, `sqlite3`, `csv`, `logging`
- **Database**: SQLite
- **Environment**: Linux (Chromebook with Linux enabled)
- **Version Control**: Git & GitHub

---

## 📊 Data Source

- API: https://jsonplaceholder.typicode.com/users  
- Data format: Nested JSON containing user, address, geo, and company information

---

## 🔄 Pipeline Flow

## output/insights --
📊 BUSINESS INSIGHTS


Users by City:
('Wisokyburgh', 1)
('South Elvis', 1)
('South Christy', 1)
('Roscoeview', 1)
('McKenziehaven', 1)
('Lebsackbury', 1)
('Howemouth', 1)
('Gwenborough', 1)
('Bartholomebury', 1)
('Aliyaview', 1)

Users by Company:
('Yost and Sons', 1)
('Romaguera-Jacobson', 1)
('Romaguera-Crona', 1)
('Robel-Corkery', 1)
('Keebler LLC', 1)
('Johns Group', 1)
('Hoeger LLC', 1)
('Deckow-Crist', 1)
('Considine-Lockman', 1)
('Abernathy Group', 1)

Users by Continent:
('Australia/Asia', 3)
('South America', 2)
('North America', 2)
('Antarctica', 2)
('Europe/Asia', 1)

Users by Hemisphere:
('Northern', 3)
('Southern', 7)

Parent Company Concentration:
('Romaguera', 2)

Email Domain Usage:
('yesenia.net', 1)
('rosamond.me', 1)
('melissa.tv', 1)
('kory.org', 1)
('karina.biz', 1)
('jasper.info', 1)
('dana.io', 1)
('billy.biz', 1)
('april.biz', 1)
('annie.ca', 1)

Website TLD Usage:
('biz', 1)
('com', 2)
('info', 2)
('io', 1)
('net', 2)
('org', 2)