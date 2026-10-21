import streamlit as st
import pandas as pd
import random
from datetime import datetime, timedelta
from pymongo import MongoClient, ASCENDING, DESCENDING
from pymongo.errors import PyMongoError

st.set_page_config(page_title="IoT Telemetry | NoSQL Lab", page_icon="📡", layout="wide")
MONGO_URI = st.sidebar.text_input("MongoDB URI", "mongodb://localhost:27017/")
DB_NAME = "iot_telemetry_lab"

@st.cache_resource
def get_client(uri):
    return MongoClient(uri, serverSelectionTimeoutMS=2500)

st.markdown("""
<style>
.block-container {padding-top: 1.5rem; padding-bottom: 2rem;}
[data-testid="stMetric"] {background: #f4f7fb; border: 1px solid #e1e8f0; padding: 16px 18px; border-radius: 12px;}
[data-testid="stSidebar"] {border-right: 1px solid #e5eaf1;}
div[data-testid="stDataFrame"] {border: 1px solid #e5eaf1; border-radius: 10px;}
</style>
""", unsafe_allow_html=True)

st.title("📡 IoT Telemetry Monitoring")
st.caption("NoSQL lab · MongoDB · sensor analytics · aggregation pipelines · query performance")

try:
    client = get_client(MONGO_URI)
    client.admin.command("ping")
    db = client[DB_NAME]
    events = db["telemetry_events"]
    devices = db["devices"]
    st.sidebar.success("MongoDB connected")
except Exception as exc:
    st.sidebar.error("MongoDB not connected")
    st.error("Cannot connect to MongoDB. Start MongoDB Server, then refresh this page.")
    st.code(f"Connection detail: {exc}")
    st.stop()

pages = ["Overview", "Telemetry Explorer", "Aggregation Lab", "Performance & Sharding"]
page = st.sidebar.radio("NAVIGATION", pages)
st.sidebar.divider()
st.sidebar.caption("Database")
st.sidebar.code(DB_NAME)
st.sidebar.caption("Collection: telemetry_events")

def flatten(doc):
    d = dict(doc)
    d.pop("_id", None)
    loc = d.pop("location", {}) or {}
    readings = d.pop("readings", {}) or {}
    d["building"] = loc.get("building")
    d["floor"] = loc.get("floor")
    for k, v in readings.items():
        if not isinstance(v, (dict, list)):
            d[k] = v
    d["event_time"] = d.get("event_time")
    d["alert_count"] = len(d.get("alerts", []) or [])
    return d

def load_events(query=None, limit=500):
    docs = list(events.find(query or {}, {"_id": 0}).sort("event_time", DESCENDING).limit(limit))
    return pd.DataFrame([flatten(x) for x in docs])

def seed_sample_data(n=1000):
    buildings = ["Block A", "Block B", "Library", "Lab Block"]
    types = ["temperature", "air_quality", "energy", "vibration", "occupancy"]
    start = datetime.utcnow() - timedelta(days=7)
    docs, device_docs = [], {}
    batch = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    for i in range(n):
        typ = random.choice(types)
        device_id = f"{typ[:3].upper()}-{random.randint(1,80):03d}"
        doc = {
            "event_id": f"SEED-{batch}-{i:05d}", "device_id": device_id,
            "tenant_id": random.choice(["CAMPUS-A", "CAMPUS-B"]), "device_type": typ,
            "event_time": start + timedelta(seconds=random.randint(0,604800)),
            "location": {"building": random.choice(buildings), "floor": random.randint(0,4)},
            "metadata": {"firmware": random.choice(["v1.0","v1.1","v2.0"]), "schema_version": random.choice([1,2])},
            "alerts": [], "recent_events": []
        }
        if typ == "temperature":
            temp = round(random.uniform(18,42),1)
            doc["readings"] = {"temperature": temp, "humidity": round(random.uniform(25,90),1)}
            if temp >= 35:
                doc["alerts"].append({"code":"HIGH_TEMP","severity":"warning" if temp < 39 else "critical","acknowledged":random.choice([True,False])})
        elif typ == "air_quality":
            doc["readings"] = {"co2":random.randint(350,1800),"pm25":round(random.uniform(2,90),1),
                               "pollutants":[{"name":"CO2","value":random.randint(350,1800)},{"name":"PM2.5","value":round(random.uniform(2,90),1)}]}
        elif typ == "energy":
            doc["readings"] = {"voltage":round(random.uniform(210,245),1),"current":round(random.uniform(1,30),2),
                               "power_w":round(random.uniform(200,5000),1),
                               "phases":[{"phase":"L1","voltage":round(random.uniform(210,245),1)},{"phase":"L2","voltage":round(random.uniform(210,245),1)}]}
        elif typ == "vibration":
            doc["readings"] = {"axes":[{"axis":"x","rms":round(random.uniform(.1,8),2)},{"axis":"y","rms":round(random.uniform(.1,8),2)},{"axis":"z","rms":round(random.uniform(.1,8),2)}],
                               "frequency_bands":[{"hz":50,"amplitude":round(random.random()*5,2)},{"hz":100,"amplitude":round(random.random()*5,2)}]}
        else:
            doc["readings"] = {"occupied_count":random.randint(0,60),"confidence":round(random.uniform(.6,1),2),
                               "zones":[{"zone":"north","count":random.randint(0,30)},{"zone":"south","count":random.randint(0,30)}]}
        docs.append(doc)
        device_docs[device_id] = {"device_id":device_id,"device_type":typ,"location":doc["location"],"last_seen":doc["event_time"],"capabilities":list(doc["readings"].keys())}
    if docs:
        events.insert_many(docs, ordered=False)
        from pymongo import ReplaceOne
        devices.bulk_write([ReplaceOne({"device_id":d["device_id"]}, d, upsert=True) for d in device_docs.values()])
    return len(docs)

if page == "Overview":
    total = events.count_documents({})
    device_count = devices.count_documents({})
    alert_count = events.count_documents({"alerts.0": {"$exists": True}})
    since = datetime.utcnow() - timedelta(hours=24)
    recent_count = events.count_documents({"event_time": {"$gte": since}})
    a,b,c,d = st.columns(4)
    a.metric("Telemetry events", f"{total:,}")
    b.metric("Registered devices", f"{device_count:,}")
    c.metric("Events with alerts", f"{alert_count:,}")
    d.metric("Last 24 hours", f"{recent_count:,}")
    st.subheader("Telemetry at a glance")
    left,right = st.columns([1.15,1])
    with left:
        type_rows = list(events.aggregate([{"$group":{"_id":"$device_type","events":{"$sum":1}}},{"$sort":{"events":-1}}]))
        if type_rows:
            type_df = pd.DataFrame([{"Device type":r["_id"],"Events":r["events"]} for r in type_rows])
            st.markdown("**Events by device type**")
            st.bar_chart(type_df.set_index("Device type"))
        else: st.info("No events yet. Use the sample-data button below.")
    with right:
        temp_rows = list(events.aggregate([
            {"$match":{"readings.temperature":{"$exists":True}}},
            {"$group":{"_id":"$location.building","Average °C":{"$avg":"$readings.temperature"},"Max °C":{"$max":"$readings.temperature"},"Samples":{"$sum":1}}},
            {"$sort":{"Average °C":-1}}
        ]))
        st.markdown("**Temperature by building**")
        if temp_rows:
            temp_df = pd.DataFrame([{"Building":r["_id"],"Average °C":round(r["Average °C"],2),"Max °C":round(r["Max °C"],2),"Samples":r["Samples"]} for r in temp_rows])
            st.dataframe(temp_df, use_container_width=True, hide_index=True)
        else: st.info("No temperature readings available.")
    st.subheader("Latest telemetry events")
    latest = load_events(limit=12)
    if not latest.empty:
        cols = [c for c in ["event_time","event_id","device_id","device_type","building","floor","temperature","humidity","co2","pm25","power_w","alert_count"] if c in latest.columns]
        st.dataframe(latest[cols], use_container_width=True, hide_index=True)
    else: st.info("The telemetry collection is empty.")
    st.divider()
    x,y = st.columns([2,1])
    with x:
        st.markdown("**Demo data**")
        st.caption("Add synthetic readings across temperature, air quality, energy, vibration, and occupancy sensors.")
    with y:
        if st.button("＋ Generate 1,000 sample events", type="primary", use_container_width=True):
            try:
                n = seed_sample_data()
                st.success(f"Inserted {n:,} sample telemetry events.")
                st.rerun()
            except PyMongoError as e: st.error(str(e))

elif page == "Telemetry Explorer":
    st.subheader("Telemetry Explorer")
    st.caption("Filter, inspect, and add readings in the MongoDB collection.")
    f1,f2,f3 = st.columns(3)
    device_filter = f1.text_input("Device ID contains")
    type_options = ["All"] + sorted(events.distinct("device_type"))
    type_filter = f2.selectbox("Device type", type_options)
    building_options = ["All"] + sorted([x for x in events.distinct("location.building") if x])
    building_filter = f3.selectbox("Building", building_options)
    query = {}
    if device_filter: query["device_id"] = {"$regex": device_filter, "$options":"i"}
    if type_filter != "All": query["device_type"] = type_filter
    if building_filter != "All": query["location.building"] = building_filter
    limit = st.select_slider("Maximum rows", options=[50,100,250,500,1000], value=250)
    df = load_events(query, limit)
    st.caption(f"Showing {len(df):,} matching records (maximum {limit:,}).")
    if not df.empty:
        display_cols = [c for c in ["event_time","event_id","device_id","device_type","building","floor","temperature","humidity","co2","pm25","power_w","occupied_count","alert_count","tenant_id"] if c in df.columns]
        st.dataframe(df[display_cols], use_container_width=True, hide_index=True)
        st.download_button("Download visible rows as CSV", df[display_cols].to_csv(index=False).encode("utf-8"), "telemetry_export.csv", "text/csv")
    else: st.info("No matching readings found.")
    st.divider()
    with st.expander("＋ Insert a sensor reading"):
        with st.form("insert_reading"):
            c1,c2,c3 = st.columns(3)
            device_id = c1.text_input("Device ID", "TEMP-101")
            device_type = c2.selectbox("Device type", ["temperature","air_quality","energy","vibration","occupancy"])
            building = c3.selectbox("Building", ["Block A","Block B","Library","Lab Block"])
            floor = c1.number_input("Floor", 0, 100, 1)
            temperature = c2.number_input("Temperature (°C)", -20.0, 100.0, 29.5, .1)
            humidity = c3.number_input("Humidity (%)", 0.0, 100.0, 65.0, .5)
            submitted = st.form_submit_button("Insert reading", type="primary")
            if submitted:
                doc = {"event_id":f"EVT-{datetime.utcnow().strftime('%Y%m%d%H%M%S%f')}",
                       "device_id":device_id.strip(),"tenant_id":"CAMPUS-A","device_type":device_type,
                       "event_time":datetime.utcnow(),"location":{"building":building,"floor":int(floor)},
                       "readings":{"temperature":temperature,"humidity":humidity},"metadata":{"source":"Streamlit form","schema_version":1},
                       "alerts":[{"code":"HIGH_TEMP","severity":"warning","acknowledged":False}] if temperature >= 35 else []}
                if not device_id.strip(): st.error("Device ID is required.")
                else:
                    try:
                        events.insert_one(doc)
                        devices.update_one({"device_id":device_id.strip()},{"$set":{"device_type":device_type,"location":doc["location"],"last_seen":doc["event_time"]}},upsert=True)
                        st.success("Reading inserted successfully.")
                        st.rerun()
                    except PyMongoError as e: st.error(str(e))
    with st.expander("Update a registered device location"):
        with st.form("update_device"):
            udid = st.text_input("Exact device ID")
            ub = st.selectbox("New building", ["Block A","Block B","Library","Lab Block"], key="ub")
            uf = st.number_input("New floor", 0, 100, 1, key="uf")
            upd = st.form_submit_button("Update device")
            if upd:
                r = devices.update_one({"device_id":udid.strip()},{"$set":{"location.building":ub,"location.floor":int(uf)}})
                st.info(f"Matched {r.matched_count}; modified {r.modified_count} device record(s).")
    with st.expander("Delete a telemetry event"):
        with st.form("delete_event"):
            eid = st.text_input("Exact event_id")
            confirm = st.checkbox("I confirm this deletion")
            dele = st.form_submit_button("Delete event")
            if dele:
                if not confirm: st.warning("Tick the confirmation box first.")
                else:
                    r = events.delete_one({"event_id":eid.strip()})
                    st.info(f"Deleted {r.deleted_count} event(s).")

elif page == "Aggregation Lab":
    st.subheader("Complex Aggregation Lab")
    st.caption("Run server-side MongoDB aggregation pipelines and inspect each result as a readable table.")
    query_names = [
        "Average temperature by building", "Alerts by severity and code",
        "Hourly temperature trend", "Dynamic readings fields by device type",
        "Energy phase voltage analysis", "Top devices by average temperature",
        "Join events with registered device details", "Facet dashboard summary"
    ]
    selected = st.selectbox("Choose aggregation query", query_names)
    pipelines = {
      "Average temperature by building":[{"$match":{"readings.temperature":{"$exists":True}}},{"$group":{"_id":"$location.building","avg_temp":{"$avg":"$readings.temperature"},"max_temp":{"$max":"$readings.temperature"},"count":{"$sum":1}}},{"$sort":{"avg_temp":-1}}],
      "Alerts by severity and code":[{"$unwind":{"path":"$alerts","preserveNullAndEmptyArrays":False}},{"$group":{"_id":{"severity":"$alerts.severity","code":"$alerts.code"},"count":{"$sum":1},"unacknowledged":{"$sum":{"$cond":[{"$eq":["$alerts.acknowledged",False]},1,0]}}}},{"$sort":{"count":-1}}],
      "Hourly temperature trend":[{"$match":{"readings.temperature":{"$exists":True}}},{"$group":{"_id":{"$dateTrunc":{"date":"$event_time","unit":"hour"}},"avg_temp":{"$avg":"$readings.temperature"},"min_temp":{"$min":"$readings.temperature"},"max_temp":{"$max":"$readings.temperature"},"count":{"$sum":1}}},{"$sort":{"_id":1}}],
      "Dynamic readings fields by device type":[{"$match":{"readings":{"$type":"object"}}},{"$project":{"device_type":1,"fields":{"$objectToArray":"$readings"}}},{"$unwind":"$fields"},{"$group":{"_id":{"type":"$device_type","field":"$fields.k"},"count":{"$sum":1}}},{"$sort":{"_id.type":1,"count":-1}}],
      "Energy phase voltage analysis":[{"$match":{"device_type":"energy","readings.phases":{"$exists":True}}},{"$unwind":"$readings.phases"},{"$group":{"_id":"$readings.phases.phase","avg_voltage":{"$avg":"$readings.phases.voltage"},"min_voltage":{"$min":"$readings.phases.voltage"},"max_voltage":{"$max":"$readings.phases.voltage"},"samples":{"$sum":1}}},{"$sort":{"_id":1}}],
      "Top devices by average temperature":[{"$match":{"readings.temperature":{"$exists":True}}},{"$group":{"_id":"$device_id","avg_temp":{"$avg":"$readings.temperature"},"max_temp":{"$max":"$readings.temperature"},"samples":{"$sum":1}}},{"$sort":{"avg_temp":-1}},{"$limit":5}],
      "Join events with registered device details":[{"$lookup":{"from":"devices","localField":"device_id","foreignField":"device_id","as":"device_info"}},{"$unwind":{"path":"$device_info","preserveNullAndEmptyArrays":True}},{"$group":{"_id":"$device_type","events":{"$sum":1},"registered_devices":{"$addToSet":"$device_info.device_id"}}},{"$project":{"events":1,"registered_device_count":{"$size":"$registered_devices"}}},{"$sort":{"events":-1}}],
      "Facet dashboard summary":[{"$facet":{"by_type":[{"$group":{"_id":"$device_type","count":{"$sum":1}}},{"$sort":{"count":-1}}],"temperature_by_building":[{"$match":{"readings.temperature":{"$exists":True}}},{"$group":{"_id":"$location.building","avg":{"$avg":"$readings.temperature"}}}],"latest_events":[{"$sort":{"event_time":-1}},{"$limit":5},{"$project":{"_id":0,"event_id":1,"device_id":1,"device_type":1,"event_time":1}}]}}]
    }
    explanations = {
      "Average temperature by building":"$match filters temperature readings → $group calculates average, maximum and sample count → $sort ranks buildings.",
      "Alerts by severity and code":"$unwind expands alert arrays → $group counts alerts by severity/code and counts unacknowledged alerts.",
      "Hourly temperature trend":"$dateTrunc groups timestamps into hourly buckets; $avg, $min and $max summarize each hour.",
      "Dynamic readings fields by device type":"$objectToArray converts variable reading fields to key/value pairs; $unwind and $group count field usage.",
      "Energy phase voltage analysis":"$unwind expands phases (L1/L2) → $group calculates average/minimum/maximum voltage.",
      "Top devices by average temperature":"$group summarizes each device, $sort ranks average temperature, $limit returns the top five.",
      "Join events with registered device details":"$lookup joins telemetry events to the devices collection using device_id.",
      "Facet dashboard summary":"$facet runs multiple summary pipelines in one aggregation: counts by type, temperature by building and latest events."
    }
    st.info(explanations[selected])
    pipeline = pipelines[selected]
    with st.expander("View MongoDB aggregation pipeline"):
        st.json(pipeline)
    if st.button("▶ Run aggregation", type="primary"):
        try:
            results = list(events.aggregate(pipeline, allowDiskUse=True))
            st.success(f"Query completed · {len(results)} result row(s)")
            if selected == "Facet dashboard summary" and results:
                r = results[0]
                c1,c2,c3 = st.columns(3)
                with c1: st.markdown("**Events by type**"); st.dataframe(pd.DataFrame(r.get("by_type",[])), use_container_width=True, hide_index=True)
                with c2: st.markdown("**Temperature by building**"); st.dataframe(pd.DataFrame(r.get("temperature_by_building",[])), use_container_width=True, hide_index=True)
                with c3: st.markdown("**Latest events**"); st.dataframe(pd.DataFrame(r.get("latest_events",[])), use_container_width=True, hide_index=True)
            elif results:
                df = pd.json_normalize(results)
                st.dataframe(df, use_container_width=True, hide_index=True)
                numeric = df.select_dtypes(include="number")
                if not numeric.empty and len(df) > 1:
                    st.markdown("**Visual result**")
                    st.bar_chart(numeric)
                st.download_button("Export results as JSON", pd.Series(results).to_json(orient="values", date_format="iso").encode("utf-8"), "aggregation_results.json", "application/json")
            else: st.warning("No results returned. Generate sample events or insert readings first.")
        except Exception as e: st.error(f"Aggregation failed: {e}")

else:
    st.subheader("Performance & Sharding")
    st.caption("Inspect indexes, explain query execution, and verify whether this connection is a mongos router.")
    col1,col2 = st.columns(2)
    with col1:
        st.markdown("#### Index management")
        if st.button("Create / verify indexes", use_container_width=True):
            try:
                events.create_index([("event_id",ASCENDING)], unique=True)
                events.create_index([("device_type",ASCENDING),("event_time",DESCENDING)])
                events.create_index([("device_id",ASCENDING),("event_time",DESCENDING)])
                events.create_index([("alerts.code",ASCENDING)])
                st.success("Indexes created or verified.")
            except Exception as e: st.error(str(e))
        try:
            index_info = events.index_information()
            st.dataframe(pd.DataFrame([{"Index":k,"Keys":str(v.get("key")),"Unique":v.get("unique",False)} for k,v in index_info.items()]), use_container_width=True, hide_index=True)
        except Exception as e: st.warning(str(e))
    with col2:
        st.markdown("#### Explain query")
        st.write("Check whether MongoDB uses an index for recent temperature readings.")
        if st.button("Run explain()", type="primary", use_container_width=True):
            try:
                q = {"device_type":"temperature","event_time":{"$gte":datetime.utcnow()-timedelta(days=7)}}
                plan = events.find(q).sort("event_time",DESCENDING).explain()
                stats = plan.get("executionStats",{})
                m1,m2,m3 = st.columns(3)
                m1.metric("Returned", stats.get("nReturned","—"))
                m2.metric("Docs examined", stats.get("totalDocsExamined","—"))
                m3.metric("Keys examined", stats.get("totalKeysExamined","—"))
                st.json({"winningPlan":plan.get("queryPlanner",{}).get("winningPlan"),"executionStats":stats})
            except Exception as e: st.error(str(e))
    st.divider()
    st.markdown("#### Sharding status")
    st.warning("A standalone MongoDB server is not a sharded cluster. Real sharding requires config servers, shard replica sets, and a mongos router.")
    if st.button("Check sharding status"):
        try:
            hello = client.admin.command("hello")
            if hello.get("msg") == "isdbgrid":
                st.success("Connected through mongos.")
                st.json(client.admin.command("listShards"))
                try: st.json(client.admin.command({"shardingStatus":1}))
                except Exception as e: st.info(f"Cluster metadata command: {e}")
            else:
                st.error("This connection is not through mongos; sharding is not active on this connection.")
                st.json({"hello_msg":hello.get("msg"),"setName":hello.get("setName"),"isWritablePrimary":hello.get("isWritablePrimary")})
        except Exception as e: st.error(str(e))
    st.markdown("**Sharding setup guide:** See `SHARDING.md` for the cluster setup and shard-key discussion.")
