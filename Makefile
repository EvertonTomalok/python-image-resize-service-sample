.PHONY: setup
setup:
	apt-get update && apt-get install --yes build-essential pkg-config libffi-dev python-dev libcurl4-openssl-dev libssl-dev libmagic1 npm
#	npm install -g pm2
	#curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python -
	pip install poetry==1.1.6
	poetry config virtualenvs.create false
	poetry install --no-interaction --no-dev

.PHONY: setup-dev
setup-dev: setup
	poetry install

.PHONY: autoflake
autoflake:
	poetry run autoflake -r $(AUTOFLAKE_OPTIONS) --exclude */snapshots --remove-unused-variables --remove-all-unused-imports  **/ | tee autoflake.log
	echo "$(AUTOFLAKE_OPTIONS)" | grep -q -- '--in-place' || ! [ -s autoflake.log ]

.PHONY: isort
isort:
	poetry run isort ./imageservice/**  ./scripts --multi-line 3 --trailing-comma --line-width 88 --skip */snapshots $(ISORT_OPTIONS)

.PHONY: black
black:
	poetry run black ./imageservice ./scripts

.PHONY: lint
lint: ISORT_OPTIONS := --check-only
lint: BLACK_OPTIONS := --check
lint: autoflake isort black
	poetry run mypy ./imageservice/**/*.py ./scripts --ignore-missing-imports
	poetry run flake8 ./imageservice ./scripts

.PHONY: format
format: AUTOFLAKE_OPTIONS := --in-place
format: autoflake isort black

image-consumer:
	poetry run python -m imageservice.ports.workers.image_resizing_consumer -w $(workers)

pm2-image-consumer:
	pm2 start "export QUEUE_URL=https://sqs.us-east-2.amazonaws.com/328097268885/ImageQueue.fifo && export LEVEL=INFO && poetry run python -m imageservice.ports.workers.image_resizing_consumer -w 1" --name 'image-consumer'

pm2-delete-image-consumer:
	pm2 delete image-consumer

pm2-restart-image-consumer:
	pm2 delete image-consumer && make pm2-image-consumer

pm2-logs:
	pm2 logs

sanitize-channels-db-prod:
	export DB_ENVIRONMENT=PRODUCTION && poetry run python -m scripts.sanitize_channels

resize-images-from-channel:
	export DB_ENVIRONMENT=PRODUCTION && poetry run python -m scripts.resize_images_from_channel_collection

resize-images-from-episodes:
	export DB_ENVIRONMENT=PRODUCTION && poetry run python -m scripts.resize_images_from_episodes_collection

postback-server:
	poetry run uvicorn imageservice.ports.server.postback:app

pm2-script-resize-images-from-channel:
	pm2 start "export DB_ENVIRONMENT=PRODUCTION && poetry run python -m scripts.resize_images_from_channel_collection" --no-autorestart --cron '0 1 * * *' --name 'resize-image-from-channel'

pm2-delete-script-resize-images-from-channel:
	pm2 delete resize-image-from-channel

pm2-script-resize-images-from-episodes:
	pm2 start "export DB_ENVIRONMENT=PRODUCTION && poetry run python -m scripts.resize_images_from_episodes_collection" --no-autorestart --cron '0 2 * * *' --name 'resize-image-from-episodes'

pm2-delete-script-resize-images-from-episodes:
	pm2 delete resize-image-from-episodes
