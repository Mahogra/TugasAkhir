import time
import numpy as np
import sys
from labjack_unified.devices import LabJackT7

# Inisialisasi LabJack T7
lj = LabJackT7()

# Periksa jika ada argumen (PWM input atau mode baca sudut)
if len(sys.argv) > 1:
    arg = sys.argv[1]
    if arg.lower() == "read":
        # Baca posisi sudut
        ppr = 8 * 310
        initial_encoder_count = lj.get_counter()
        encoder_count = lj.get_counter() - initial_encoder_count
        angle_deg = (360 / ppr) * encoder_count
        print(angle_deg)  # Kirim hasil untuk diambil oleh subprocess
    else:
        # Kontrol motor menggunakan PWM dari argumen
        pwm_value = float(arg)
        direction = 1 if pwm_value > 0 else -1
        lj.set_dutycycle(value1=abs(pwm_value) * direction)
        time.sleep(0.5)
        lj.set_dutycycle(value1=0)  # Matikan motor setelah menjalankan

def get_current_angle():
    # Baca sudut dari encoder dan konversi ke derajat
    encoder_count = lj.get_counter() - initial_encoder_count
    return (360 / ppr) * encoder_count

def set_motor_pwm(pwm_value):
    direction = 1 if pwm_value > 0 else -1
    lj.set_dutycycle(value1=abs(pwm_value) * direction)
