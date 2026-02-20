.PHONY: setup generate ingest train run-api dashboard test lint

setup:
	pip install -r requirements.txt
	pre-commit install || true

generate:
	python data/seed/generate.py

ingest:
	python pipelines/ingest/load.py

train:
	python pipelines/train/train_price_model.py
	python pipelines/train/train_conversion_model.py

run-api:
	uvicorn app.main:app --reload

dashboard:
	streamlit run dashboard/app.py

test:
	MODEL_SOURCE=mock pytest tests/ -v --tb=short

lint:
	ruff check .
	black --check .
