# VARIABLES
SRC_DIR := Collimundo
VENV_DIR := Collimundo
DOTENV_DIR := Collimundo
TEST_PORT := 8000
SERVER_PORT := 3034


# ============================================================================
#								USER COMMANDS
# ============================================================================

# Help functin to view all commands
help:
	@echo =====================================================================
	@echo 						HELP
	@echo =====================================================================
	@echo make help: Show all commands
	@echo .
	@echo .
	@echo - DJANGO FUNCTIONS -
	@echo .
	@echo make migrate: Migrate changes to database
	@echo make run: Run webapplication locally
	@echo make run-insecure: Run webapplication locally with insecure
	@echo .
	@echo .
	@echo - PRE-COMMIT -
	@echo .
	@echo make pre-commit-install-git: Install pre-commit outside of running environment
	@echo make pre-commit: Run pre-commit test
	@echo make pre-commit-all: Run pre-commit test on all files
	@echo .
	@echo .
	@echo - DOT ENVIRONMENT -
	@echo .
	@echo make gen-dotenv: Create new dotenv file with new key
	@echo .
	@echo .
	@echo - EXTRA FUNCTIONS -
	@echo .
	@echo make clean: Delete all temporary files
	@echo make venv_windows: Create virtual environment on windows
	@echo make venv_linux: Create virtual environment on linux
	@echo .
	@echo .
	@echo - TEST FUNCTIONS (written for linux) -
	@echo .
	@echo make test-linux-pre: Run pre test
	@echo make test-linux-searchengine: Run searchengine test
	@echo make test-linux-embedding: Run embedding test
	@echo make test-linux-datasource: Run datasource test
	@echo make end-to-end-tests-linux: Run end-to-end tests
	@echo make end-to-end-tests-selenium: Run end-to-end tests with selenium
	@echo make test-linux-post: Run post test
	@echo .
	@echo .
	@echo - SERVER FUNCTIONS used for deployment (written for linux) -
	@echo .
	@echo make run-s: Run webapplication on server
	@echo make deploy-s: Deploy webapplication on server
	@echo make gen-dotenv-s: Create new dotenv file with new key on server
	@echo make migrate-s: Migrate changes to database on server
	@echo =====================================================================

# Run webapplication locally
run: venv_windows
	.\$(VENV_DIR)\.venv\Scripts\activate \
	&& python $(SRC_DIR)/manage.py runserver $(TEST_PORT)

# Run web application locally and prepare for Selenium testing
run-selenium: venv_unix
	. $(VENV_DIR)/.venv/Scripts/activate && python $(SRC_DIR)/manage.py runserver $(SERVER_PORT)

# Run webapplication locally
run-insecure: venv_windows
	.\$(VENV_DIR)\.venv\Scripts\activate \
	&& python $(SRC_DIR)/manage.py runserver --insecure $(TEST_PORT)


# Install pre-commit outside of running environment
pre-commit-install-git:
	pip install pre-commit==3.6.2 \
	&& pre-commit install

# Run pre-commit test
pre-commit: pre-commit-install
	.\$(VENV_DIR)\.venv\Scripts\activate \
	&& pre-commit run

# Run pre-commit test on all files
pre-commit-all: pre-commit-install
	.\$(VENV_DIR)\.venv\Scripts\activate \
	&& pre-commit run --all-files

# Create new dotenv file with new key
gen-dotenv: venv_windows
	.\$(VENV_DIR)\.venv\Scripts\activate \
	&& python $(DOTENV_DIR)/.dotenv/create_dotenv.py

# Migrate changes to database
migrate: venv_windows
	.\$(VENV_DIR)\.venv\Scripts\activate \
	&& python $(SRC_DIR)/manage.py makemigrations \
	&& python $(SRC_DIR)/manage.py migrate

# Delete all temporary files
clean:
	rmdir /s /Q .\$(VENV_DIR)\.venv && ( echo deleted ) || ( break )
	rmdir /s /Q .\$(SRC_DIR)\Collimundo\__pycache__ && ( echo deleted ) || ( break )
	rmdir /s /Q .\$(SRC_DIR)\companies\__pycache__ && ( echo deleted ) || ( break )
	rmdir /s /Q .\$(SRC_DIR)\dashboard\__pycache__ && ( echo deleted ) || ( break )
	rmdir /s /Q .\$(SRC_DIR)\login\__pycache__ && ( echo deleted ) || ( break )
	rmdir /s /Q .\$(SRC_DIR)\search_engine\__pycache__ && ( echo deleted ) || ( break )
	rmdir /s /Q .\$(SRC_DIR)\widgets\__pycache__ && ( echo deleted ) || ( break )


# ============================================================================



# ============================================================================
#								TEST (Linux)
# ============================================================================
# PRE TEST
test-linux-pre: venv_linux
	. $(SRC_DIR)/.venv/bin/activate \
	&& python3 -m pytest -s ./Collimundo/testing/pre_test.py

# UNIT TESTS
test-linux-searchengine: venv_linux
	. $(SRC_DIR)/.venv/bin/activate \
	&& python3 -m pytest -s ./Collimundo/testing/automatic_searchengine_test.py

test-linux-embedding: venv_linux
	. $(SRC_DIR)/.venv/bin/activate \
	&& python3 -m pytest -s ./Collimundo/testing/automatic_embedding_test.py

test-linux-datasource: venv_linux
	. $(SRC_DIR)/.venv/bin/activate \
	&& python3 -m pytest ./Collimundo/testing/automatic_datasource_test.py


# END-TO-END TESTS
end-to-end-tests-linux: venv_linux
	. $(SRC_DIR)/.venv/bin/activate \
	&& python3 $(SRC_DIR)/manage.py test $(SRC_DIR).urls_test

end-to-end-tests-selenium: venv_linux
	. $(SRC_DIR)/.venv/bin/activate \
	&& python3 -m pytest ./Collimundo/testing/end_to_end_test.py

# POST TESTING
test-linux-post: venv_linux
	. $(SRC_DIR)/.venv/bin/activate \
	&& python3 -m pytest ./Collimundo/testing/post_test.py


# ============================================================================



# ============================================================================
#							SERVER COMMANDS (Linux)
# ============================================================================


run-s: venv_linux
	. $(VENV_DIR)/.venv/bin/activate \
	&& python3 $(SRC_DIR)/manage.py runserver $(SERVER_PORT)

deploy-s:
	sudo service collimundo stop \
	&& sudo git stash \
	&& sudo git checkout main \
	&& sudo git pull \
	&& sudo make gen-dotenv-s \
	&& sudo make migrate-s \
 	&& sudo service collimundo start \

gen-dotenv-s: venv_linux
	. $(SRC_DIR)/.venv/bin/activate \
	&& python3 $(DOTENV_DIR)/.dotenv/create_dotenv.py

migrate-s: venv_linux
	. $(SRC_DIR)/.venv/bin/activate \
	&& python3 $(SRC_DIR)/manage.py makemigrations \
	&& python3 $(SRC_DIR)/manage.py migrate

get-news-s: venv_linux_API
	. API/.venv/bin/activate \
	&& python3 API/NewsArticles/News_articles.py
	sudo mv -f API/NewsArticles/data/AI.json Collimundo/static/data/news/AI.json \
	&& sudo mv -f API/NewsArticles/data/belgium.json Collimundo/static/data/news/belgium.json \
	&& sudo mv -f API/NewsArticles/data/sustainability.json Collimundo/static/data/news/sustainability.json \
	&& sudo mv -f API/NewsArticles/data/vrt.json Collimundo/static/data/news/vrt.json


# ============================================================================



# ============================================================================
#						VIRTUAL ENVIRONMENT & DEPENDENCIES
# ============================================================================

pre-commit-install: venv_windows
	.\$(VENV_DIR)\.venv\Scripts\activate \
	&& pre-commit install

venv_windows:
	python3 -m venv $(VENV_DIR)/.venv \
	&& .\$(VENV_DIR)\.venv\Scripts\activate \
	&& pip install -Ur ./$(VENV_DIR)/requirements.txt

venv_linux:
	python3 -m venv $(VENV_DIR)/.venv \
	&& . $(VENV_DIR)/.venv/bin/activate \
	&& pip install -Ur $(VENV_DIR)/requirements.txt

venv_linux_API:
	python3 -m venv API/.venv \
	&& . API/.venv/bin/activate \
	&& pip install -Ur API/requirements.txt
