# Run the IoT Telemetry dashboard (Windows + VS Code)

## 1. Requirements
- Python 3.10 or newer
- MongoDB Community Server running locally, unless you use a remote MongoDB URI

## 2. Open the project
Extract this ZIP, open the extracted folder in VS Code, and open Terminal → New Terminal.

## 3. Create and activate a virtual environment (Git Bash)
```bash
python -m venv .venv
source .venv/Scripts/activate
python -m pip install -r requirements.txt
```
If `.venv` is already active, do not create/activate it again; just run:
```bash
python -m pip install -r requirements.txt
```

## 4. Start the dashboard
```bash
streamlit run app.py
```
Streamlit will show a local URL, usually http://localhost:8501. Open it in your browser.

## 5. Try it
1. Confirm “MongoDB connected” in the sidebar.
2. Open Overview and click “Generate 1,000 sample events”.
3. Explore Telemetry Explorer, Aggregation Lab, and Performance & Sharding.
4. Run aggregation queries and inspect the displayed pipeline.

## Troubleshooting
- If `streamlit` is not found, run `python -m streamlit run app.py`.
- If MongoDB is not connected, start MongoDB Server from Windows Services (service name often `MongoDB`) and refresh.
- The app uses database `iot_telemetry_lab` and collections `telemetry_events`, `devices`.
- The dashboard checks sharding status but does not magically enable sharding. A real sharded cluster must be configured separately as described in `SHARDING.md`.



