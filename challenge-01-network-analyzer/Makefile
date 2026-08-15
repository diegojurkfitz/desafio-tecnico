.PHONY: build run demo test clean help

IMAGE_NAME := traffic-analyzer
DATA_DIR := ./data

help: ## Exibe comandos disponiveis
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

build: ## Build da imagem Docker
	docker build -t $(IMAGE_NAME) .

run: build ## Executa captura real (interface eth0, 100 pacotes, timeout 30s)
	docker run --rm \
		--network host \
		--cap-add NET_ADMIN \
		--cap-add NET_RAW \
		-v $(DATA_DIR):/data \
		$(IMAGE_NAME) \
		--interface eth0 --count 100 --timeout 30

demo: build ## Executa modo demonstracao (sem permissao de captura)
	docker run --rm \
		-v $(DATA_DIR):/data \
		$(IMAGE_NAME) \
		--demo

test: ## Executa testes unitarios localmente
	python -m unittest discover -s tests -v

lint: ## Verifica tipagem com mypy (requer mypy instalado)
	python -m mypy app/ --strict --ignore-missing-imports

clean: ## Remove banco de dados local e cache Python
	rm -rf $(DATA_DIR)/*.db
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
