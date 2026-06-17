"""
constants.py - Constantes compartilhadas do console
"""

from pathlib import Path

# Limites do console de log
MAX_LOG_LINES = 5000

# Diretório de auto-export (relativo ao diretório do projeto client/)
AUTO_EXPORT_DIR = str(Path(__file__).resolve().parents[3] / "exports" / "auto")

# Intervalos de atualização (ms)
UPDATE_INTERVAL = 100  # Taxa de atualização da GUI
AUTO_SAVE_INTERVAL = 20000  # Auto-save periódico (20 segundos)

# Thresholds de cálculo
ACCEL_THRESHOLD = 0.3  # Threshold para filtrar ruído de aceleração (m/s²)
VELOCITY_DECAY_FACTOR = 0.98  # Fator de decay para simular atrito
MIN_VELOCITY_THRESHOLD = 0.1  # Velocidade mínima antes de zerar (m/s)

# Limites mínimos para auto-save
MIN_LOGS_FOR_SAVE = 100
MIN_SENSORS_FOR_SAVE = 1000
MIN_TELEMETRY_FOR_SAVE = 100  # Pontos mínimos de telemetria para salvar

# Valores padrão de Force Feedback (ajuste base para condução)
# Max Force é o FF_GAIN global do G923: teto que escala TODOS os efeitos no
# hardware. Com tudo a 100%, a força resultante nunca ultrapassa esse limite.
FF_DAMPING_DEFAULT = 35.0  # Amortecimento leve: mata oscilação sem pesar o volante
FF_FRICTION_DEFAULT = 25.0  # Atrito sutil de grip, sem mascarar o puxão de curva
FF_FILTER_DEFAULT = 50.0  # Suaviza o jitter do BMI160 mantendo a resposta da curva
FF_SENSITIVITY_DEFAULT = 75.0  # Preserva faixa dinâmica do puxão sem clipar cedo
FF_MAX_FORCE_DEFAULT = 20.0  # Teto global no motor (% do max do G923; ~25% trava)

# Valores padrão de controle
BRAKE_BALANCE_DEFAULT = 60.0  # 60% dianteiro
