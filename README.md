# IoT Telemetry Monitoring Using NoSQL (MongoDB)

A NoSQL-based IoT telemetry monitoring dashboard for storing, managing, querying, and analyzing simulated sensor data using MongoDB. The project demonstrates how document-oriented databases can support flexible IoT data storage, aggregation, indexing, and query performance analysis.

## 📌 Project Overview

Internet of Things (IoT) devices continuously generate telemetry data such as temperature, humidity, air quality, battery levels, and other sensor readings. Managing this data efficiently requires a database that supports flexible data structures and effective querying.

This project implements an **IoT Telemetry Monitoring System using MongoDB**, a document-oriented NoSQL database. It provides a dashboard for working with sensor records and demonstrates fundamental NoSQL operations, aggregation pipelines, indexing, and query optimization.

The project uses simulated sensor data for demonstration and academic purposes.

## 🎯 Objectives

- Store and manage IoT telemetry data using MongoDB.
- Demonstrate CRUD operations: Create, Read, Update, and Delete.
- Generate and analyze sample sensor readings.
- Perform data analysis using MongoDB aggregation pipelines.
- Create indexes to improve query performance.
- Examine query execution plans using MongoDB's `explain()` functionality.
- Understand NoSQL database architecture and its suitability for IoT applications.
- Explore the concepts of scalability and sharding.

## ✨ Key Features

- **Telemetry Management:** Work with simulated IoT sensor records.
- **MongoDB Integration:** Store and retrieve structured documents.
- **CRUD Operations:** Insert, view, update, and delete telemetry records.
- **Sample Data Generation:** Generate sensor readings for testing.
- **Aggregation Pipeline:** Summarize and analyze telemetry data.
- **Indexing:** Create indexes to support frequently used queries.
- **Query Performance Analysis:** Inspect query execution plans.
- **Interactive Dashboard:** Use the application's interface to explore telemetry records and database operations.
- **Sharding Concepts:** Understand how MongoDB can distribute data across multiple shards.

## 🛠️ Technology Stack

| Technology | Purpose |
|---|---|
| Python | Application logic |
| MongoDB | NoSQL document database |
| PyMongo | Python interface for MongoDB |
| Streamlit | Interactive dashboard, if using the Streamlit version |
| Git and GitHub | Version control and project hosting |
| VS Code | Development environment |

## 🏗️ System Architecture

```text
+-----------------------------+
|     Simulated IoT Devices   |
+--------------+--------------+
               |
               v
+-----------------------------+
|      Telemetry Data         |
| Temperature, Humidity, etc. |
+--------------+--------------+
               |
               v
+-----------------------------+
|       Python Application    |
|   Dashboard and Operations  |
+--------------+--------------+
               |
               v
+-----------------------------+
|          PyMongo            |
+--------------+--------------+
               |
               v
+-----------------------------+
|       MongoDB Database      |
|   iot_telemetry_lab         |
|                             |
|   telemetry_events          |
|   devices (if configured)   |
+--------------+--------------+
               |
               v
+-----------------------------+
| CRUD, Aggregation, Indexing  |
| and Query Analysis           |
+-----------------------------+
```

## 🗄️ Database Design

**Database name:** `iot_telemetry_lab`

The project uses a MongoDB database to store telemetry records as BSON documents.

### Collections

- **`telemetry_events`** — stores sensor readings and telemetry events.
- **`devices`** — can store device metadata if this collection is implemented in the configured project version.

### Example Telemetry Document

```json
{
  "device_id": "TEMP001",
  "sensor_type": "Temperature",
  "location": "Block A",
  "temperature": 24.5,
  "humidity": 45,
  "battery": 95
}
```

*Note: This is an illustrative document. Field names and data types should match the actual schema used by the application.*

## 📂 Project Structure

A typical project structure is shown below. Your actual filenames may differ depending on the version of the project.

```text
iot_telemetry_nosql_dashboard/
│
├── app.py
├── requirements.txt
├── README.md
└── .gitignore
```

## ⚙️ Installation and Setup

### Prerequisites

Install or configure the following:

- Python 3.10 or a compatible version
- MongoDB Community Server or another accessible MongoDB deployment
- MongoDB Shell (`mongosh`) for database inspection
- Visual Studio Code (recommended)
- Git (optional, for version control)

### Step 1: Clone the Repository

Replace the placeholder with your actual GitHub repository URL.

```bash
git clone https://github.com/YOUR_USERNAME/YOUR_REPOSITORY.git
```

Navigate to the project folder:

```bash
cd YOUR_REPOSITORY
```

### Step 2: Create a Virtual Environment

On Windows using Git Bash:

```bash
python -m venv .venv
source .venv/Scripts/activate
```

On Windows using PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### Step 3: Install Dependencies

If the project contains a `requirements.txt` file:

```bash
python -m pip install -r requirements.txt
```

If Streamlit is required but is not listed in the requirements:

```bash
python -m pip install streamlit
```

Install PyMongo if it is not already included:

```bash
python -m pip install pymongo
```

### Step 4: Start MongoDB

Make sure your MongoDB server is running and accessible.

The local MongoDB connection string used by this project is:

```text
mongodb://localhost:27017/
```

If your application uses a different connection string, configure it accordingly.

### Step 5: Run the Application

For the Streamlit dashboard:

```bash
python -m streamlit run app.py
```

For a standard Python application, if the project uses a Tkinter interface instead:

```bash
python app.py
```

Use the command appropriate to the actual application version. For Streamlit, the terminal will display the local address where the dashboard can be opened in a browser.

## 🔍 MongoDB Operations

Connect to MongoDB using the MongoDB Shell:

```bash
mongosh
```

Select the project database:

```javascript
use iot_telemetry_lab
```

Display the available collections:

```javascript
show collections
```

Count the telemetry records:

```javascript
db.telemetry_events.countDocuments()
```

Display sample records:

```javascript
db.telemetry_events.find().limit(5)
```

## 📊 Aggregation Examples

MongoDB aggregation pipelines allow data to be filtered, grouped, summarized, and analyzed.

### 1. Count Records by Sensor Type

```javascript
db.telemetry_events.aggregate([
  {
    $group: {
      _id: "$sensor_type",
      total_records: { $sum: 1 }
    }
  }
])
```

### 2. Calculate Average Temperature by Location

```javascript
db.telemetry_events.aggregate([
  {
    $group: {
      _id: "$location",
      average_temperature: { $avg: "$temperature" }
    }
  }
])
```

### 3. Find High-Temperature Records

```javascript
db.telemetry_events.find({
  temperature: { $gt: 30 }
})
```

These examples assume that the documents contain the corresponding fields. Adjust the field names to match the actual schema.

## ⚡ Indexing and Query Optimization

Indexes help MongoDB locate matching documents without necessarily scanning the entire collection.

Example: create an index on the sensor type.

```javascript
db.telemetry_events.createIndex({
  sensor_type: 1
})
```

Example: create a compound index on location and sensor type.

```javascript
db.telemetry_events.createIndex({
  location: 1,
  sensor_type: 1
})
```

Inspect a query execution plan:

```javascript
db.telemetry_events.find({
  sensor_type: "Temperature"
}).explain("executionStats")
```

The execution statistics can help evaluate the query plan, documents examined, and documents returned.

**Note:** Indexes consume storage and add overhead to write operations. Their effectiveness depends on the query pattern and the data distribution.

## 🌐 NoSQL and Scalability

MongoDB stores data in flexible documents, making it suitable for applications where telemetry records may have different attributes across sensor types.

The project demonstrates NoSQL concepts such as:

- Document-oriented storage
- Flexible document structures
- Aggregation-based data processing
- Indexing and query optimization
- Horizontal scaling concepts

### Sharding

Sharding distributes data across multiple servers to support larger datasets and workloads.

The project introduces the concept of sharding. A local MongoDB instance does **not** automatically provide a sharded cluster. Actual sharding requires a properly configured MongoDB sharded deployment.

## 🧪 Testing and Expected Results

The project can be tested by performing the following operations:

1. Connect the application to MongoDB.
2. Insert or generate sample telemetry records.
3. Verify the records in the `telemetry_events` collection.
4. Read, update, and delete records through the available operations.
5. Run aggregation queries to summarize sensor readings.
6. Create indexes and inspect query execution statistics.
7. Review the dashboard output and database results.

Expected results include successful telemetry record management, aggregation summaries, and query execution information. Actual results depend on the dataset and database configuration.

## 🔐 Limitations

- The current demonstration uses simulated telemetry data rather than a live IoT sensor network.
- Query performance depends on the dataset size, indexes, and execution environment.
- A local MongoDB instance does not demonstrate real distributed sharding by itself.
- Dashboard functionality depends on the application version and its implemented features.

## 🚀 Future Enhancements

- Integrate real IoT devices and streaming sensor data.
- Add real-time telemetry visualization and historical trend charts.
- Introduce threshold-based alerts for abnormal readings.
- Add device authentication and access control.
- Store timestamps for time-based analysis.
- Deploy MongoDB as a properly configured sharded cluster.
- Add data retention policies and automated cleanup.
- Deploy the dashboard to a cloud platform.




