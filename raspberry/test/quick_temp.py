#!/usr/bin/env python3
"""
quick_temp_test.py - Teste Rápido do Sensor DS18B20
Teste simples e direto do sensor de temperatura

EXECUÇÃO:
=========
python3 quick_temp_test.py

REQUISITOS:
===========
• DS18B20 conectado no GPIO4 (Pin 7)
• 1-Wire habilitado no raspi-config
• dtoverlay=w1-gpio,gpiopin=4 no /boot/firmware/config.txt
"""

import os
import time
import glob
from datetime import datetime


def check_1wire_setup():
    """Verifica se 1-Wire está configurado"""
    print("🔍 Verificando configuração 1-Wire...")

    w1_dir = "/sys/bus/w1/devices/"
    if not os.path.exists(w1_dir):
        print("❌ 1-Wire não configurado!")
        print("\nPara configurar:")
        print("1. sudo raspi-config → Interface Options → 1-Wire → Enable")
        print("2. Adicionar ao /boot/config.txt: dtoverlay=w1-gpio,gpiopin=25")
        print("3. sudo reboot")
        return False

    # Procura dispositivos DS18B20
    device_folders = glob.glob(w1_dir + "28-*")

    if not device_folders:
        print("❌ Nenhum sensor DS18B20 encontrado!")
        print("\nVerifique:")
        print("• Conexões: VDD→3.3V, GND→GND, DQ→GPIO4 (Pin 7)")
        print("• Resistor pull-up 4.7kΩ entre DQ e 3.3V")
        return False

    print(f"✅ Sensor encontrado: {os.path.basename(device_folders[0])}")
    return device_folders[0]


def read_temperature_raw(device_path):
    """Lê dados brutos do sensor"""
    try:
        with open(device_path + "/w1_slave", "r") as f:
            lines = f.readlines()
        return lines
    except Exception as e:
        print(f"❌ Erro ao ler sensor: {e}")
        return None


def parse_temperature(lines):
    """Converte dados brutos em temperatura"""
    if not lines or len(lines) < 2:
        return None

    # Verifica se leitura é válida
    if lines[0].strip()[-3:] != "YES":
        return None

    # Extrai temperatura
    temp_pos = lines[1].find("t=")
    if temp_pos != -1:
        temp_string = lines[1][temp_pos + 2 :]
        temp_c = float(temp_string) / 1000.0
        return temp_c

    return None


def get_temperature(device_path, max_retries=3):
    """Obtém temperatura com retry"""
    for attempt in range(max_retries):
        lines = read_temperature_raw(device_path)
        if lines:
            temp = parse_temperature(lines)
            if temp is not None:
                return temp

        if attempt < max_retries - 1:
            time.sleep(0.2)  # Aguarda 200ms antes de tentar novamente

    return None


def get_thermal_status(temp_c):
    """Determina status térmico"""
    if temp_c < 40:
        return "NORMAL", "🟢"
    elif temp_c < 60:
        return "WARNING", "🟡"
    elif temp_c < 80:
        return "CRITICAL", "🔴"
    else:
        return "DANGER", "🚨"


def main():
    """Teste principal"""
    print("🌡️  TESTE RÁPIDO DO SENSOR DS18B20")
    print("=" * 40)

    # Verifica configuração
    device_path = check_1wire_setup()
    if not device_path:
        return False

    print(f"📍 Dispositivo: {device_path}")
    print("\n🧪 Iniciando teste de leituras...")
    print("Pressione Ctrl+C para parar\n")

    reading_count = 0
    temperatures = []

    try:
        while True:
            # Lê temperatura
            temp_c = get_temperature(device_path)

            if temp_c is not None:
                reading_count += 1
                temperatures.append(temp_c)

                # Converte para outras unidades
                temp_f = (temp_c * 9 / 5) + 32
                temp_k = temp_c + 273.15

                # Status térmico
                status, emoji = get_thermal_status(temp_c)

                # Timestamp
                timestamp = datetime.now().strftime("%H:%M:%S")

                # Exibe leitura
                print(
                    f"[{timestamp}] #{reading_count:3d} | "
                    f"{temp_c:6.2f}°C | {temp_f:6.1f}°F | {temp_k:6.1f}K | "
                    f"{emoji} {status}"
                )

                # Detecta mudanças bruscas
                if len(temperatures) >= 2:
                    change = temperatures[-1] - temperatures[-2]
                    if abs(change) > 1.0:
                        print(f"    ⚠️  Mudança: {change:+.2f}°C")

                # Estatísticas a cada 10 leituras
                if reading_count % 10 == 0:
                    temp_min = min(temperatures)
                    temp_max = max(temperatures)
                    temp_avg = sum(temperatures) / len(temperatures)
                    print(
                        f"    📊 Min: {temp_min:.1f}°C | "
                        f"Max: {temp_max:.1f}°C | "
                        f"Média: {temp_avg:.1f}°C"
                    )

            else:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] ❌ Falha na leitura")

            # Aguarda 1 segundo
            time.sleep(1.0)

    except KeyboardInterrupt:
        print("\n\n🛑 Teste interrompido pelo usuário")

    except Exception as e:
        print(f"\n❌ Erro durante teste: {e}")

    finally:
        # Estatísticas finais
        if temperatures:
            print("\n📈 ESTATÍSTICAS FINAIS:")
            print(f"   Leituras válidas: {len(temperatures)}")
            print(f"   Temperatura mínima: {min(temperatures):.2f}°C")
            print(f"   Temperatura máxima: {max(temperatures):.2f}°C")
            print(f"   Temperatura média: {sum(temperatures)/len(temperatures):.2f}°C")
            print(f"   Variação total: {max(temperatures)-min(temperatures):.2f}°C")

            if len(temperatures) >= 5:
                print("✅ Sensor funcionando corretamente!")
            else:
                print("⚠️  Poucas leituras válidas - verifique conexões")
        else:
            print("❌ Nenhuma leitura válida obtida")

        print("\n👋 Teste finalizado")


if __name__ == "__main__":
    main()
