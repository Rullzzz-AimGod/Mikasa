# ============================================================
# MIKASA - Makefile
# ============================================================

PYTHON = python3
RUN = run.py
MAIN = Mikasa.py
REQ = requirements.txt

# Warna
GREEN  = \033[1;32m
YELLOW = \033[1;33m
CYAN   = \033[1;36m
RED    = \033[1;31m
RESET  = \033[0m

# ============================================================
# TARGETS
# ============================================================

all: help

install:
	@echo "$(YELLOW)[+] Installing dependencies...$(RESET)"
	@pip install -r $(REQ) || pip3 install -r $(REQ)
	@echo "$(GREEN)[✓] Dependencies installed!$(RESET)"

run:
	@clear
	@echo "$(CYAN)[+] Running MIKASA...$(RESET)"
	@$(PYTHON) $(RUN)

sudo-run:
	@clear
	@echo "$(CYAN)[+] Running MIKASA with sudo...$(RESET)"
	@sudo $(PYTHON) $(RUN)

setup:
	@echo "$(YELLOW)[+] Creating folder structure...$(RESET)"
	@mkdir -p modules lib config data/wordlists data/logs
	@touch modules/__init__.py lib/__init__.py
	@echo "$(GREEN)[✓] Folder structure created!$(RESET)"

clean:
	@echo "$(YELLOW)[+] Cleaning cache...$(RESET)"
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@find . -type f -name "*.pyo" -delete 2>/dev/null || true
	@echo "$(GREEN)[✓] Cache cleaned!$(RESET)"

purge: clean
	@echo "$(YELLOW)[+] Purging all temp files...$(RESET)"
	@rm -f license.lic 2>/dev/null || true
	@rm -f *.log 2>/dev/null || true
	@rm -rf __pycache__ 2>/dev/null || true
	@echo "$(GREEN)[✓] Purge complete!$(RESET)"

check:
	@echo "$(YELLOW)[+] Checking installed dependencies...$(RESET)"
	@pip list 2>/dev/null || pip3 list
	@echo "$(GREEN)[✓] Done!$(RESET)"

help:
	@echo ""
	@echo "$(CYAN)─────────────────────────────────────────────────────────────$(RESET)"
	@echo "$(CYAN)  $(YELLOW)MIKASA - HELP$(RESET)"
	@echo "$(CYAN)─────────────────────────────────────────────────────────────$(RESET)"
	@echo "$(CYAN)  $(GREEN)make install  $(RESET) Install dependencies"
	@echo "$(CYAN)  $(GREEN)make run      $(RESET) Run MIKASA"
	@echo "$(CYAN)  $(GREEN)make sudo-run $(RESET) Run with sudo (if needed)"
	@echo "$(CYAN)  $(GREEN)make setup    $(RESET) Create folder structure"
	@echo "$(CYAN)  $(GREEN)make clean    $(RESET) Clean cache files"
	@echo "$(CYAN)  $(GREEN)make purge    $(RESET) Remove all temp files"
	@echo "$(CYAN)  $(GREEN)make check    $(RESET) Check installed dependencies"
	@echo "$(CYAN)  $(GREEN)make help     $(RESET) Show this help"
	@echo "$(CYAN)─────────────────────────────────────────────────────────────$(RESET)"
	@echo ""

# ============================================================
# PHONY
# ============================================================
.PHONY: all install run sudo-run setup clean purge check help

