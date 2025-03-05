# Makefile per gestire i container di API e Dashboard

.PHONY: all api-up dashboard-up up api-down dashboard-down down restart logs logs-api logs-dashboard rm-networks prune clean

# Target predefinito: alza entrambi i servizi
all: up

# Avvia il servizio API (in cartella api)
api-up:
	@echo "Avvio API..."
	@cd api && docker compose up -d --build

# Avvia il servizio Dashboard (in cartella dashboard)
dashboard-up:
	@echo "Avvio Dashboard..."
	@cd dashboard && docker compose up -d --build

# Avvia entrambi i servizi
up: api-up dashboard-up

# Ferma il servizio API
api-down:
	@echo "Arresto API..."
	@cd api && docker compose down

# Ferma il servizio Dashboard
dashboard-down:
	@echo "Arresto Dashboard..."
	@cd dashboard && docker compose down

# Ferma entrambi i servizi
down: api-down dashboard-down

# Riavvia entrambi i servizi
restart: down up

# Visualizza i log dell'API
logs-api:
	@echo "Log API:"
	@cd api && docker compose logs -f

# Visualizza i log della Dashboard
logs-dashboard:
	@echo "Log Dashboard:"
	@cd dashboard && docker compose logs -f

# Visualizza i log di entrambi i servizi (in parallelo, in sessioni separate)
logs: logs-api logs-dashboard

# Rimuove il network esterno (se esiste)
rm-networks:
	@echo "Rimozione del network 'backend-network'..."
	@docker network rm backend-network || echo "Network 'backend-network' non esistente o già rimosso."

# Pulisce container e network inutilizzati
prune:
	@echo "Pulizia dei container e network inutilizzati..."
	@docker container prune -f
	@docker network prune -f

# Target di pulizia totale: ferma i container, pulisce e rimuove il network
clean: down prune rm-networks
	@echo "Pulizia completata."
