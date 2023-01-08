import requests
import json
from flask import Flask, jsonify,  make_response
import os
class xUiClient:
    def __init__(self, host, username, password):
        self.tried_to_auth = False
        self.host = host
        self.username = username
        self.password = password
        self.retrieve_session()
    def retrieve_session(self):
        if self.tried_to_auth:
            print("your credentials seems to be wrong, please check them")
            quit()
        response = requests.post(f'http://{self.host}/login', data={'username': self.username, 'password': self.password}, verify=False)
        if response.status_code == 200:
            self.cookies = {
                'session': response.cookies['session'],
            }
            print("SESSION RETRIEVED")
            return True
        else:
            print(response.text)
            print("RESULT CODE NOT 200")
            self.tried_to_auth = True
            return False
    def request(self, path, return_json=True):
        response = requests.post(f'http://{self.host}/{path}', cookies=self.cookies, verify=False)
        if response.status_code == 200:
            if return_json:
                return {"success":True, "data": json.loads(response.text)}
            else:
                return response.text
        elif response.status_code == 404:
            print("session seems to be expired, trying to retrieve session")
            self.retrieve_session()
            return self.request(path, return_json)
        else:
            print("RESULT CODE NOT 200/404", response.status_code, response.text)
            if return_json:
                return {"success": False, "msg": "got !200"}
            else:
                return "error"
    def server_status(self):
        result = self.request("server/status")
        response = []
        if result['success'] == True:
            result = result['data']['obj']
            # parsing server status
            if result['xray']['state'] == "running":
                response.append("xray_running 1.0")
            else:
                response.append("xray_running 0.0")
            response.append("tcp_count " + str(float(result['tcpCount'])))
            response.append("udp_count " + str(float(result['udpCount'])))
            response.append("netio_up " + str(float(result['netIO']['up'])))
            response.append("netio_down " + str(float(result['netIO']['down'])))
            response.append("traffic_sent " + str(float(result['netTraffic']['sent'])))
            response.append("traffic_receive " + str(float(result['netTraffic']['recv'])))
            response.append("cpu " + str(float(result['cpu'])))
            response.append("disk_current " + str(float(result['disk']['current'])))
            response.append("disk_total " + str(float(result['disk']['total'])))
            response.append("mem_current " + str(float(result['mem']['current'])))
            response.append("mem_total " + str(float(result['mem']['total'])))
            response.append("swap_current " + str(float(result['swap']['current'])))
            response.append("swap_total " + str(float(result['swap']['total'])))
        return response
    def generate_results(self):
        res = ""
        res += "\n".join(self.server_status())
        return res

username = os.getenv('x_ui_username')
password = os.getenv('x_ui_password')
host = os.getenv('x_ui_url')
xc = xUiClient(host, username, password) # url is like xui.mydomain.com:54321
app = Flask(__name__)

@app.route("/metrics")
def metrics_endpoint():
    try:
        response = make_response(xc.generate_results(), 200)
        response.mimetype = "text/plain"
        return response
    except Exception as e:
        print("ERROR", e)
        return jsonify(res), 500

if __name__ == "__main__":
   app.run(debug=False, host="0.0.0.0", port=9688)
