import asyncio
import websockets
import json
import numpy as np
from encrypt import enkripsi, dekripsi

# PID Parameters
Kp = 1.7
Ki = 0.03
Kd = 0.17

# Control Variables
integral = 0
prev_error = 0
setpoint_angle = 90  # Setpoint default, bisa diubah sesuai kebutuhan

authenticated_clients = {}

async def server_handler(websocket, path):
    global integral, prev_error, setpoint_angle

    print("Client connected")
    client_id = str(websocket.remote_address)
    
    try:
        # Authentication
        async for message in websocket:
            if client_id not in authenticated_clients:
                auth_data = json.loads(message)
                if auth_data.get("name") == "Sean" and auth_data.get("password") == "bayar10rb":
                    authenticated_clients[client_id] = True
                    print(f"Client {client_id} authenticated.")
                    await websocket.send("terautentikasi")
                    break
                else:
                    await websocket.close()
                    return

        # Send setpoint to client
        encrypted_setpoint = str(enkripsi(str(setpoint_angle)))
        await websocket.send(encrypted_setpoint)
        print(f"Setpoint {setpoint_angle} dikirim ke client")

        # Control loop
        while client_id in authenticated_clients:
            try:
                received_data = await websocket.recv()
                decrypted_data = dekripsi(eval(received_data))
                current_angle = float(decrypted_data)
                print(f"Feedback angle: {current_angle:.2f}")

                # PID Control
                error = np.radians(setpoint_angle) - np.radians(current_angle)
                integral += error
                derivative = error - prev_error
                pid_output = (Kp * error) + (Ki * integral) + (Kd * derivative)
                prev_error = error

                pwm_output = max(0, min(100, abs(pid_output * 100)))
                direction = 1 if pid_output > 0 else -1
                control_signal = pwm_output * direction

                encrypted_response = str(enkripsi(str(control_signal)))
                await websocket.send(encrypted_response)
                print(f"PWM sent to client: {control_signal:.2f}")

            except Exception as e:
                print(f"Error: {e}")
                break

    except websockets.exceptions.ConnectionClosed:
        print(f"Client {client_id} disconnected.")
    finally:
        authenticated_clients.pop(client_id, None)
        print(f"Client {client_id} logged out.")

async def start_server():
    server = await websockets.serve(server_handler, "0.0.0.0", 8765)
    print("WebSocket server is running...")
    await server.wait_closed()

asyncio.run(start_server())
