make sure to kill the port you want to use 1st : 
lsof -ti :8001 | xargs kill -9


this is how you run the fastapi : 

export PYTHONPATH=$PWD
python -m uvicorn src.main:app --reload --port 8001



