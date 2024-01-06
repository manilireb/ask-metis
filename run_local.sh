uvicorn api.main:app --reload --port 8001 &

sleep 2

streamlit run frontend.py --server.port 8002