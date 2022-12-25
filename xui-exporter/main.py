import requests
import json
from flask import Flask, jsonify,  make_response
import os
class xUiClient:
    def __init__(self, host, token):
        self.host = host
        self.token = token
        self.cookies = {
            'session': self.token,
        }
    def request(self, path, return_json=True):
        response = requests.post(f'http://{self.host}/{path}', cookies=self.cookies, verify=False)
        if response.status_code == 200:
            if return_json:
                return {"success":True, "data": json.loads(response.text)}
            else:
                return response.text
        else:
            print("RESULT CODE NOT 200")
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
    def inbound_list(self):
        result = self.request("xui/inbound/list")
    def generate_results(self):
        res = ""
        res += "\n".join(self.server_status())
        return res

# retrieve token from cookies after logging in
token = os.getenv('x_ui_token')
host = os.getenv('x_ui_url')
xc = xUiClient(host, token) # url is like xui.mydomain.com:54321
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
