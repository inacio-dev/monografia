# Sistema de Teleoperação com Force Feedback para Veículo RC

Repositório público do código-fonte do Trabalho de Conclusão de Curso (TCC) em
Engenharia da Computação — Universidade Federal do Ceará (UFC), 2026.

- **Autor:** Inácio Rodrigues de Matos Galvão
- **Licença:** [MIT](LICENSE)
- **Monografia:** descreve o projeto, os experimentos e os resultados em detalhe

## Escopo deste repositório

Para permitir a replicação dos experimentos, este repositório disponibiliza
apenas o código-fonte das três partes que compõem o sistema:

- [`raspberry/`](raspberry/) — software embarcado executado no Raspberry Pi 4
  (veículo)
- [`client/`](client/) — aplicação cliente executada no PC do operador
- [`pro_micro/`](pro_micro/) — firmware do Arduino Pro Micro responsável pelo
  monitoramento de energia

### O que NÃO está versionado

Por questão de tamanho, os seguintes materiais ficaram fora do repositório e
estão **disponíveis sob solicitação ao autor**:

- _datasets_ brutos das sessões (arquivos Pickle gravados pelo _auto-save_ do
  veículo)
- _datasheets_ dos componentes
- artigos lidos e notas de projeto
- monografia em LaTeX (fontes e PDF)

As rotinas que processam os arquivos Pickle e geram os gráficos do Capítulo 4
acompanham os módulos de cada subprojeto (ver `utils/` em cada pasta).

## Sobre o projeto

Sistema completo de teleoperação de veículo RC estilo Fórmula 1 com interface
háptica (_force feedback_), comunicação UDP de baixa latência e telemetria em
tempo real. Integra:

- **Veículo RC** controlado por Raspberry Pi 4 com câmera e IMU
- **Simulador** com volante Logitech G923 (900°, pedais progressivos,
  _force feedback_ nativo via `evdev`)
- **Aplicação cliente** em Python para vídeo, telemetria e controle
- **Monitoramento de energia** via Arduino Pro Micro (tensão + correntes) e
  INA219

### Principais resultados

| Métrica                  | Obtido    | Benchmark           |
| ------------------------ | --------- | ------------------- |
| Latência UDP             | 1,94 ms   | < 5 ms              |
| FPS do vídeo             | 29,9      | 10 (literatura)     |
| Resolução                | 640×480   | 320×240 (literatura)|
| Precisão _force feedback_| 97,2 %    | —                   |
| Custo total              | R$ 1.300  | R$ 50.000+ (comercial) |

## Arquitetura do sistema

```
┌─────────────────┐     UDP      ┌─────────────────┐     USB      ┌─────────────────┐
│  Raspberry Pi 4 │◄────────────►│   Cliente PC    │◄────────────►│  Logitech G923  │
│                 │   9999/9998  │                 │    evdev     │                 │
│  - Câmera       │              │  - Interface    │              │  - Volante 900° │
│  - BMI160 IMU   │              │  - Vídeo        │              │  - Pedais       │
│  - Motor DC 775 │              │  - Telemetria   │              │  - Paddle shift │
│  - 3x Servos    │              │  - Controle     │              │  - Force FB     │
│  - Pro Micro    │              │  - G923 Manager │              │                 │
└─────────────────┘              └─────────────────┘              └─────────────────┘
```

## Estrutura do repositório

```
tcc-public/
├── raspberry/                # Software embarcado (Raspberry Pi 4)
│   ├── main.py               # Orquestrador principal
│   ├── managers/             # camera, bmi160, motor, steering, brake,
│   │                         # network, power_monitor, temperature, logger,
│   │                         # rpi_system
│   ├── utils/                # Utilitários e rotinas de análise
│   ├── test/                 # Scripts de teste
│   ├── requirements.txt
│   └── MODULOS.md            # Especificações dos módulos de hardware
│
├── client/                   # Aplicação cliente (PC do operador)
│   ├── main.py               # Aplicação principal
│   ├── managers/             # g923, network, video, sensor, keyboard,
│   │                         # slider, image_filters, client_system_monitor,
│   │                         # simple_logger
│   ├── console/              # Interface gráfica (Tkinter)
│   ├── tests/
│   ├── g923_calibration.json # Calibração do volante
│   └── requirements.txt
│
├── pro_micro/                # Firmware Arduino Pro Micro
│   └── pro_micro.ino         # ADC: bateria + 2x ACS758 → USB Serial
│
├── LICENSE                   # MIT
├── mypy.ini
└── README.md
```

O detalhamento de cada diretório está descrito na Tabela 41 do Apêndice B da
monografia.

## Hardware utilizado

### Veículo RC

- Raspberry Pi 4 Model B (4 GB+ RAM)
- Câmera OV5647 (5 MP, interface CSI)
- IMU BMI160 (I²C)
- Motor DC RC 775 + ponte H BTS7960
- 3× servo MG996R (direção + freios)
- Driver PWM PCA9685

### Monitoramento de energia

- Arduino Pro Micro (ATmega32U4, USB nativo)
- 2× ACS758 (efeito Hall, 50 A + 100 A, _high-side_)
- Divisor de tensão 20 kΩ / 10 kΩ (bateria 3S LiPo)
- INA219 (corrente do Raspberry Pi, I²C)

### Simulador

- Logitech G923 Racing Wheel (USB)
- Volante 900°, pedais progressivos, _paddle shifters_
- _Force feedback_ nativo via Linux `evdev`

## Ambiente operacional

- **Sistema do veículo:** Raspberry Pi OS Bullseye 64-bit
  (_kernel_ `5.15.84-v8+`)
- **Rede _wireless_:** 5 GHz via roteador TP-Link Deco M4 V4 (Wi-Fi 5 AC1200)
- **Resolução de hostname:** mDNS via Avahi (`f1car.local`)

## Instalação

### Raspberry Pi (veículo)

```bash
# Habilitar interfaces (Camera, I2C, SPI)
sudo raspi-config

# Dependências do sistema
sudo apt update
sudo apt install python3-opencv python3-numpy python3-picamera2 python3-libcamera

# Dependências Python
cd raspberry
pip install -r requirements.txt

# Hostname + mDNS
sudo hostnamectl set-hostname f1car
echo "127.0.1.1 f1car" | sudo tee -a /etc/hosts
sudo systemctl restart avahi-daemon
```

### Cliente (PC com Linux)

```bash
cd client
python3 -m venv venv
source venv/bin/activate          # bash
# source venv/bin/activate.fish    # fish
pip install -r requirements.txt

# Acesso ao G923 via evdev
sudo usermod -a -G input $USER     # logout/login depois

# mDNS (exemplo Arch Linux)
sudo pacman -S avahi nss-mdns
sudo systemctl enable --now avahi-daemon
```

### Arduino Pro Micro (firmware)

1. Arduino IDE → _Board_: Arduino Micro
2. _Upload_ de [`pro_micro/pro_micro.ino`](pro_micro/pro_micro.ino)
3. Conectar via USB ao Raspberry Pi (detecção automática)

## Uso

### Inicialização

```bash
# 1. Raspberry Pi (com Pro Micro conectado via USB)
cd raspberry
python3 main.py

# 2. Cliente PC (com G923 conectado via USB)
cd client
source venv/bin/activate
python3 main.py --port 9999
```

O G923 e o Pro Micro são detectados automaticamente. O G923 tem prioridade
sobre o teclado quando conectado.

### Controles

| Entrada           | Ação                              |
| ----------------- | --------------------------------- |
| G923 Volante      | Direção (−100 a +100)             |
| G923 Acelerador   | _Throttle_ (0–100 %)              |
| G923 Freio        | _Brake_ (0–100 %)                 |
| G923 Paddle R / L | Marcha acima / abaixo             |
| W / ↑             | Acelerar (teclado)                |
| S / ↓             | Frear (teclado)                   |
| A / ←             | Virar à esquerda (teclado)        |
| D / →             | Virar à direita (teclado)         |
| M / N             | Marcha acima / abaixo (teclado)   |

## Protocolo de comunicação

### UDP (Raspberry Pi ↔ Cliente)

- **Porta 9999** — dados (vídeo MJPEG + telemetria JSON)
- **Porta 9998** — comandos de controle

### G923 → Cliente (`evdev`)

```
ABS_X         → STEERING (-100 a +100)
ABS_RZ        → THROTTLE (0-100%)
ABS_Z         → BRAKE    (0-100%)
BTN_GEAR_UP   → GEAR_UP
BTN_GEAR_DOWN → GEAR_DOWN
```

### _Force feedback_ (Cliente → G923)

```python
g923_manager.apply_force_feedback(intensity, direction)
# intensity: 0-100 %
# direction: "left" | "right" | "neutral"
# Usa FF_CONSTANT via evdev (efeito contínuo atualizado em tempo real)
```

### Serial (Pro Micro → Raspberry Pi)

```
PWR:<v_bat>,<i_servos>,<i_motor>   # Tensão (V) e correntes (A) a 10 Hz
CAL                                # Solicitar recalibração dos ACS758
```

## Validação experimental

O sistema foi validado em sessão controlada de 15 minutos, gerando:

- 90.000+ pontos de telemetria
- 26.925 _frames_ de vídeo
- análise estatística (ANOVA, teste _t_, correlação de Pearson)

A discussão completa dos resultados está no Capítulo 4 da monografia. Os
arquivos Pickle utilizados na análise podem ser solicitados ao autor.

## Licença

Distribuído sob a licença [MIT](LICENSE).

## Contato

Inácio Rodrigues de Matos Galvão
Engenharia da Computação — UFC, 2026
