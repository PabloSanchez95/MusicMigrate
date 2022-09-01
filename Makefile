run:
	@echo "Running migration" 
	@( \
		source venv/bin/activate; \
		python app.py; \
	)

setup: install
	@[ ! -f .env ] && cp .env.mock .env ||:;
	@[ ! -f youtube_music/headers_auth.json ] && cp headers_auth.json.mock youtube_music/headers_auth.json ||:;

install:
	@echo "Installing dependencies locally"
	@( \
		[ ! -d venv ] && python3 -m venv --copies venv ||:; \
		source venv/bin/activate; \
		pip install -qU pip; \
		pip install --no-cache-dir wheel; \
		pip install --no-cache-dir -r requirements.txt; \
	)