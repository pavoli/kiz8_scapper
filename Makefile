# Makefile для запуска Apache Airflow с Docker Compose

VENV_NAME = airflow_venv
PYTHON = python3.12
ACTIVATE = source $(VENV_NAME)/bin/activate
REQ_FILE = requirements.txt
AIRFLOW_URL = http://localhost:8080

.PHONY: venv activate install af-up af-db-init af-db-upgrade af-create-user af-open-ui start-all down help

help:
	@echo "Makefile targets:"
	@echo "  venv            - Создать виртуальное окружение"
	@echo "  activate        - Активировать виртуальное окружение"
	@echo "  install         - Создать виртуальное окружение и установить зависимости из requirements.txt"
	@echo "  af-up           - Запустить основные сервисы Airflow (webserver, scheduler, worker) в фоне"
	@echo "  af-db-init      - Инициализировать базу данных Airflow"
	@echo "  af-db-upgrade   - Обновить базу данных Airflow"
	@echo "  af-create-user  - Создать пользователя администратора Airflow"
	@echo "  af-open-ui      - Откроет Airflow UI"
	@echo "  start-all       - Запустить все сервисы Airflow в фоне"
	@echo "  down            - Остановить и удалить контейнеры"

venv:
	@echo "Создаем виртуальное окружение $(VENV_NAME)..."
	$(PYTHON) -m venv $(VENV_NAME)

activate:
	@echo "Активируйте виртуальное окружение командой:"
	@echo "source $(VENV_NAME)/bin/activate"

install: venv
	@echo "Устанавливаем зависимости из $(REQ_FILE)..."
	$(ACTIVATE) && pip install -r $(REQ_FILE)

af-up:
	@echo "Запускаем основные сервисы Airflow в фоне..."
	docker-compose up airflow-webserver airflow-scheduler airflow-worker -d

af-db-init:
	@echo "Инициализируем базу данных Airflow..."
	docker-compose run --rm airflow-webserver airflow db init
	
af-db-upgrade:
	@echo "Обновляем базу данных Airflow..."
	docker-compose run --rm airflow-webserver airflow db upgrade

af-create-user:
	@echo "Создаем пользователя администратора Airflow..."
	docker-compose run --rm airflow-webserver airflow users create \
		--username admin \
		--firstname Admin \
		--lastname User \
		--role Admin \
		--email admin@example.com

af-open-ui:
	@echo "Открываем Airflow UI -> $(AIRFLOW_URL)..."
	@# Try gio open (GNOME)
	@if command -v gio >/dev/null 2>&1; then \
		gio open $(AIRFLOW_URL); \
		exit 0; \
	fi
	@# Try open (macOS)
	@if command -v open >/dev/null 2>&1; then \
		open --url $(AIRFLOW_URL); \
		exit 0; \
	fi
	@# Try start (Windows CMD)
	@if command -v cmd.exe >/dev/null 2>&1; then \
		cmd.exe /c start $(AIRFLOW_URL); \
		exit 0; \
	fi

start-all:
	@echo "Запускаем все сервисы в фоне..."
	docker-compose up -d

down:
	@echo "Останавливаем и удаляем контейнеры..."
	docker-compose down
