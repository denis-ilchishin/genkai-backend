install:
	cp -n .env.example .env
	cp -n compose/backend/local/.env.example compose/backend/local/.env
	cp -n compose/backend/prod/.env.example compose/backend/prod/.env
	cp -n compose/postgres/.env.example compose/postgres/.env
	cp -n src/config/settings/local.py.example src/config/settings/local.py