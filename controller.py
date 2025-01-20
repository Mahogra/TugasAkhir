import asyncio
import websockets
import json
import sys
from encrypt import dekripsi, enkripsi
from motor_control import get_current_angle, set_motor_pwm

async def client_handler():
    uri = "ws://10.250.25.253:8765"
    
    async with websockets.connect(uri) as websocket:
        auth_data = {
            "name": "Sean",
            "password": "bayar10rb"
        }
        await websocket.send(json.dumps(auth_data))
        response = await websocket.recv()

        if "terautentikasi" in response:
            print("Authentication successful.")

            # Receive setpoint
            encrypted_setpoint = await websocket.recv()
            setpoint = float(dekripsi(eval(encrypted_setpoint)))
            print(f"Received setpoint: {setpoint}")

            while True:
                current_angle = get_current_angle()
                encrypted_angle = str(enkripsi(str(current_angle)))
                await websocket.send(encrypted_angle)

                encrypted_pwm = await websocket.recv()
                control_signal = float(dekripsi(eval(encrypted_pwm)))

                set_motor_pwm(control_signal)
                print(f"Applied PWM: {control_signal}")

asyncio.run(client_handler())
