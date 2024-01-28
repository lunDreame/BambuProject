import socket
import requests
import json
import binascii
import jwt      # PyJWT==1.7.1
import time

class TCPSocket:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connected = False

    def connect(self):
        self.socket.connect((self.host, self.port))
        self.connected = True

    def send(self, data):
        if not self.connected:
            raise ConnectionError("Socket is not connected.")
        self.socket.sendall(data)

    def receive(self, buffer_size=1024):
        if not self.connected:
            raise ConnectionError("Socket is not connected.")
        return self.socket.recv(buffer_size)

    def receive_json(self, buffer_size=1024):
        data = self.receive(buffer_size)
        byte4_data = binascii.hexlify(data[0 : 4]).decode('utf-8')
        json_data = json.loads(data[4 : len(data) - 2].decode('utf-8'))
        byte2_data = binascii.hexlify(data[len(data) - 2 : len(data)]).decode('utf-8')
        return byte4_data, json_data, byte2_data

    def close(self):
        self.socket.close()
        self.connected = False

def unbind_device():
    try:
        dev_id = input("Enter the device ID to delete (e.g. 01S...): ").strip().upper()
        json_data = {"dev_id": dev_id, "force": False}
        response = requests.delete("https://api.bambulab.com/v1/iot-service/api/user/bind", headers=headers, json=json_data)
        response.raise_for_status()
        print("Response Text: ", response.text)

    except requests.exceptions.RequestException as e:
        if e.response.status_code == 403:
            print("Device not found, please try again")
        else:
            print("An error occurred while requesting:", e)

def send_device_auth(preferred_username: str):
    if client_socket.connected:
        data = {"login": {"sequence_id": 8001, "command": "login", "wifi": "KR", "tutk": "US", "iot": "https://api.bambulab.com/v1", "apix": "https://api.bambulab.com/", "emqx": "ssl://us.mqtt.bambulab.com:8883", "timezone": "UTC+09:00", "e-improved": True, "user_id": preferred_username}}
        start_byte = bytearray([0xa5, 0xa5, 0x06, 0x01])
        json_bytes = bytearray(json.dumps(data), 'utf-8')
        end_byte = bytearray([0xa7, 0xa7])

        final_data = start_byte + json_bytes + end_byte
        client_socket.send(final_data)

    received_byte4, received_json, received_byte2 = client_socket.receive_json()
    print('Login Report:   status: {}, reason: {}'.format(received_json['login']['status'], received_json['login'].get('reason')))
    if received_json['login']['status'] == 'wait_auth':
        send_user_ticket(received_json['login']['ticket'])
    elif received_json['login']['status'] == 'FAILURE':
        reason = json.loads(received_json['login'].get('reason'))
        if reason.get('devmsg') != "LAN-ONLY enabled" and reason.get('err_code') == 83968025:
            user_input = input('Device is already binded. Do you want to unbind? "True/False": ')
            unbind_device() if user_input.strip().lower() == 'true' else print("Device unbind user cancel")
        else:
            print("Unexpected failure reason:", reason)
    else:
        print("Unexpected status:", received_json['login']['status'])
            
def send_user_ticket(login_ticket: str):
    print("Login Ticket:  ", login_ticket)

    try:
        response = requests.get('https://api.bambulab.com/v1/user-service/my/ticket/' + login_ticket, headers=headers)
        response.raise_for_status()
        print("Response Text: ", response.text)
        if len(response.json()) == 2:
            bind_user_ticket(login_ticket)
    except requests.exceptions.RequestException as e:
        print("An error occurred while requesting: ", e)

def bind_user_ticket(login_ticket: str):
    try:
        response = requests.post('https://api.bambulab.com/v1/user-service/my/ticket/' + login_ticket, headers=headers)
        response.raise_for_status()
        print("Response Text: ", response.text or None)
        received_byte4, received_json, received_byte2 = client_socket.receive_json()
        print('Login Report:   status: {}, reason: {}'.format(received_json['login']['status'], received_json['login'].get('reason')))
    except requests.exceptions.RequestException as e:
        print("An error occurred while requesting: ", {e})

def get_login_token(username: str, password: str):
    global headers, decoded_token
    json_data = {"account": username, "password": password, "apiError": ""}
    try:
        response = requests.post('https://bambulab.com/api/sign-in/form', json=json_data)
        response.raise_for_status()
        print("Response Text: ", response.text)

        token = response.cookies.get('token')
        refresh_token = response.cookies.get('refreshToken')

        headers = {'Authorization': f'Bearer {token}', 'Refresh-Token': refresh_token}
        decoded_token = jwt.decode(token, verify=False)

        send_device_auth(decoded_token['preferred_username'])
    except requests.exceptions.RequestException as e:
        print("Maybe the mail or password is wrong. Please try again")
        # print("An error occurred while requesting: ", e)


if __name__ == "__main__":
    global client_socket

    host = input("Printer IP Address: ")
    username = input("Bambu Lab Accout Mail: ")
    password = input("Bambu Lab Accout Password: ")

    if host and username and password:
        client_socket = TCPSocket(host, 3000)
        client_socket.connect()
        time.sleep(1)
        get_login_token(username, password)

