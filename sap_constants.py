"""Konstanten: Vehikel (wie in der Wurzel der Linie), Regler-Grenzen, Experiment, Farben und Presets."""

# --- Vehikel: sechs Standorte, Kapazität, Zukauf bis 50 % der mittleren Nachfrage (ohne Umlagerung: d = 6 Entscheidungsvariablen) -----------
J = 6
MU_LOW, MU_HIGH = 60, 140
CAP_COST = 1.0
SPOT_JITTER = 0.1
UNMET_MULT = 3.0                # nur für die Kopie der Instanz, die Fehlmenge ist hier eine Nebenbedingung, kein Kostenterm
SPOT_LIMIT = 0.5
TRANSFER_BASE, TRANSFER_SCALE = 0.3, 0.35
RHO = 0.4
SPOT_MULT = 1.9
SCENARIO_SEED_OFFSET = 7_000_003
BUDGET_FREE = 10.0
SCENARIOS = 200                 # Vorgabe von `demand_scenarios`, hier unbenutzt
Z0_BINS = 5                     # nur für die Kopie des Vehikels

# --- „Wahre“ Verteilung zum Prüfen: frische lognormale Szenarien (die Optimierung sieht sie nie) ------------------------------------------------
REF_SCENARIOS = 20_000
REF_SEED = 900_001

# --- Regler --------------------------------------------------------------------------------------------------------------------------------
EPS_CHOICES = (0.02, 0.05, 0.10)
DEFAULT_EPS = 0.05
BETA_CHOICES = (1e-2, 1e-3, 1e-5)
DEFAULT_BETA = 1e-2
N_MIN, N_MAX, N_STEP, DEFAULT_N = 20, 1500, 10, 260
B_MIN, B_MAX, B_STEP, DEFAULT_B = 0, 100, 10, 30
SIGMA_MIN, SIGMA_MAX, SIGMA_STEP, DEFAULT_SIGMA = 0.10, 0.60, 0.05, 0.35
SEED_MAX, DEFAULT_SEED = 999999, 7
DRAW_MAX, DEFAULT_DRAW = 999, 6

# --- Experiment ----------------------------------------------------------------------------------------------------------------------------
REPEATS = 100                   # unabhängige Ziehungen je Szenarienzahl
SMALL_N = (20, 60)              # kleine Szenarienzahlen, die weit unter jeder Schranke liegen

# --- Farben --------------------------------------------------------------------------------------------------------------------------------
COLOR_BINOMIAL = "#2F6B65"
COLOR_SIMPLE = "#B5651D"
COLOR_CC = "#8c6bb1"
COLOR_SMALL = "#4c78a8"
COLOR_GRID = "rgba(150,150,150,0.75)"

PRESETS = {
    "Standardfall (Voreinstellung)": {
        "eps": DEFAULT_EPS, "beta": DEFAULT_BETA, "n": DEFAULT_N, "b": DEFAULT_B, "sigma": DEFAULT_SIGMA,
        "seed": DEFAULT_SEED, "draw": DEFAULT_DRAW,
    },
    "Zu wenige Szenarien": {
        "eps": DEFAULT_EPS, "beta": DEFAULT_BETA, "n": 60, "b": DEFAULT_B, "sigma": DEFAULT_SIGMA,
        "seed": DEFAULT_SEED, "draw": DEFAULT_DRAW,
    },
    "Strenger: ε = 2 %, β = 0,001 %": {
        "eps": 0.02, "beta": 1e-5, "n": 1500, "b": DEFAULT_B, "sigma": DEFAULT_SIGMA,
        "seed": DEFAULT_SEED, "draw": DEFAULT_DRAW,
    },
    "Keine Fehlmenge erlaubt": {
        "eps": DEFAULT_EPS, "beta": DEFAULT_BETA, "n": DEFAULT_N, "b": 0, "sigma": DEFAULT_SIGMA,
        "seed": DEFAULT_SEED, "draw": DEFAULT_DRAW,
    },
}
PRESET_HELP = {
    "Standardfall (Voreinstellung)": "ε = 5 %, Konfidenz 99 %, 260 Szenarien (etwa die exakte Schranke), höchstens 30 Einheiten Fehlmenge insgesamt.",
    "Zu wenige Szenarien": "Nur 60 Szenarien: weit unter der Schranke; die Verletzung der Nebenbedingung ist oft größer als ε.",
    "Strenger: ε = 2 %, β = 0,001 %": "Strengere Garantie: viel mehr Szenarien nötig, der Plan wird teurer.",
    "Keine Fehlmenge erlaubt": "Schwelle b = 0: jede Fehlmenge zählt als Verletzung.",
}
