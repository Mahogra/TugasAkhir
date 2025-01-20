import asyncio
import websockets
import json
import numpy as np
from encrypt import enkripsi, dekripsi

# Dictionary to store authentication status for each client
authenticated_clients = {}

# PID Parameters
Kp = 1.7
Ki = 0.03
Kd = 0.17

# Control Variables
integral = 0
prev_error = 0
setpoint_angle = 0  # Default setpoint (to be updated from client)

async def server_handler(websocket, path):
    global integral, prev_error, setpoint_angle
    
    print("Client connected")
    client_id = str(websocket.remote_address)

    try:
        # Authentication phase
        async for message in websocket:
            if client_id not in authenticated_clients:
                try:
                    auth_data = json.loads(message)
                except json.JSONDecodeError:
                    print(f"Invalid authentication data from {client_id}")
                    await websocket.close()
                    return

                # Check authentication credentials
                if auth_data.get("name") == "Sean" and auth_data.get("password") == "bayar10rb":
                    authenticated_clients[client_id] = True
                    print(f"Client {client_id} authenticated.")
                    await websocket.send("terautentikasi")
                    break
                else:
                    print(f"Authentication failed for {client_id}")
                    await websocket.close()
                    return

        # Communication loop after authentication
        while client_id in authenticated_clients:
            try:
                # Receive data (feedback angle) from client
                received_data = await websocket.recv()
                decrypted_data = dekripsi(eval(received_data))
                
                try:
                    current_angle = float(decrypted_data)
                    print(f"Received feedback angle: {current_angle:.2f}°")
                    
                    # PID Control Calculation
                    error = np.radians(setpoint_angle) - np.radians(current_angle)
                    integral += error
                    derivative = error - prev_error
                    pid_output = (Kp * error) + (Ki * integral) + (Kd * derivative)
                    prev_error = error
                    
                    # Calculate PWM output
                    pwm_output = max(10, min(100, abs(pid_output * 100)))
                    direction = 1 if pid_output > 0 else -1
                    control_signal = pwm_output * direction

                    # Send PWM value to client
                    encrypted_response = str(enkripsi(str(control_signal)))
                    await websocket.send(encrypted_response)
                    print(f"Sent PWM value: {control_signal:.2f}%")
                    
                except ValueError:
                    print("Invalid feedback data received")
                
                await asyncio.sleep(1)

            except websockets.exceptions.ConnectionClosed:
                print(f"Client {client_id} disconnected.")
                break

    except websockets.exceptions.ConnectionClosed as e:
        print(f"Connection Closed: {e}")
    finally:
        authenticated_clients.pop(client_id, None)
        print(f"Client {client_id} disconnected")

async def start_server():
    server = await websockets.serve(server_handler, "0.0.0.0", 8765)
    print("WebSocket server is running...")
    await server.wait_closed()

asyncio.run(start_server())
