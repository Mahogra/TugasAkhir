import asyncio
import websockets
import json
import subprocess
from encrypt import dekripsi, enkripsi

data = []

async def client_handler():
    uri = "ws://10.250.25.253:8765"  # Ganti dengan alamat server jika diperlukan

    async with websockets.connect(uri) as websocket:
        # Kirim data autentikasi
        auth_data = {
            "name": "Sean",
            "password": "bayar10rb"
        }
        first_message = json.dumps(auth_data)
        print(f"Sending to server: {first_message}")
        await websocket.send(first_message)

        response = await websocket.recv()
        print(f"Received from server: {response}")
        data.append(response)

        if "terautentikasi" in response:
            while True:
                try:
                    # Jalankan motor_control.py untuk membaca posisi sudut dari encoder
                    process = subprocess.run(
                        ["python", "motor_control.py", "read"],
                        capture_output=True,
                        text=True
                    )

                    # Ambil nilai sudut dari output motor_control.py
                    feedback_angle = float(process.stdout.strip())
                    print(f"Feedback angle: {feedback_angle:.2f}°")

                    # Kirim feedback ke server
                    encrypted_feedback = str(enkripsi(str(feedback_angle)))
                    await websocket.send(encrypted_feedback)

                    # Terima PWM dari server
                    received_message = await websocket.recv()
                    decrypted_message = dekripsi(eval(received_message))
                    pwm_value = float(decrypted_message)

                    # Jalankan motor_control.py dengan nilai PWM yang diterima
                    print(f"Running motor_control.py with PWM: {pwm_value:.2f}%")
                    subprocess.run(["python", "motor_control.py", str(pwm_value)], check=True)

                except websockets.exceptions.ConnectionClosed:
                    print("Connection closed by server")
                    break
                except ValueError:
                    print("Invalid response received from server")

        # Simpan data ke dalam file JSON setelah koneksi ditutup
        with open('client_data.json', 'w') as f:
            json.dump(data, f)

        print("Data saved to client_data.json")

asyncio.run(client_handler())
