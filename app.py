from flask import Flask, render_template, request
import requests, json, time

app = Flask(__name__)
app.config.update(
    DEBUG = True
)

CLIENT_LOGIN_KEY = "5ac749fbeec93607fc28d666be85e73a"#"some string"! your strign tas "key" shold be here :D

class AlwaysUpMainClass:
    def __init__(self) -> None:
        database = {
            "userdata":{
                "ALWAYSUP":{
                    "password":"",
                    "last_update":0,# when some uname added to db, first step is update site until 3 monthes and thired is add time.time() for this argument
                    "updates":0,
                    "logs":{}# {"TIME":"TEXT"}
                }
            },
            "client_login_key":CLIENT_LOGIN_KEY}
        dbname = "database.json"
        try:
            self.database = eval(open(dbname, "r", encoding="utf-8").read())
        except:
            self.database = database
            open(dbname, "w", encoding="utf-8").write(json.dumps(self.database, indent=4))

    def updatedb(self):
        open("database.json", "w", encoding="utf-8").write(json.dumps(self.database, indent=4))

    def add_to_db(self, uname, data):
        if uname not in self.database["userdata"]:
            self.database["userdata"][uname] = data
        else:
            self.database["userdata"][uname].update(data)

    def refreshPA(self, uname ,passw) -> bool: #https://github.com/smartm13/AutoExtend_pythonanywhere/blob/master/pythonAnywhere_AutoRefresh.py
        print("[UNAME]", uname)
        req = requests.Session()
        response = req.get('https://www.pythonanywhere.com/login/', params={'next':'/user/{}/webapps/'.format(uname)}.items())
        csrft=response.text[response.text.find("value='",response.text.find("csrfmiddlewaretoken"))+7:response.text.find("'",response.text.find("value='",response.text.find("csrfmiddlewaretoken"))+7)]
        cookies = response.cookies.get_dict()
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Referer': 'https://www.pythonanywhere.com/login/?next=/user/{}/webapps/'.format(uname),
        }
        params={'next':'/user/{}/webapps/'.format(uname)}.items()
        data = {
          'csrfmiddlewaretoken': csrft,
          'auth-username': '{}'.format(uname),
          'auth-password': '{}'.format(passw),
          'login_view-current_step': 'auth'
        }
        response2 = req.post('https://www.pythonanywhere.com/login/', headers=headers, params=params, cookies=cookies, data=data, allow_redirects = 1)
        csrft=response2.text[response2.text.find("value='",response2.text.find("csrfmiddlewaretoken"))+7:response2.text.find("'",response2.text.find("value='",response2.text.find("csrfmiddlewaretoken"))+7)]
        cookies=response2.cookies.get_dict()
        #cookies['web_app_tab_type']='%23tab_id_{}_pythonanywhere_com'.format(uname)
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Referer': 'https://www.pythonanywhere.com/user/{}/webapps/'.format(uname),
        }
        data = {'csrfmiddlewaretoken': csrft}
        #u = req.get("https://www.pythonanywhere.com/user/insprjprc/")
        #print(u.is_redirect, u.url, u.content)
        response3 = req.post('https://www.pythonanywhere.com/user/{0}/webapps/{0}.pythonanywhere.com/extend'.format(uname), headers=headers, cookies=cookies, data=data)
        success=response3.request.url.count(uname)
        #print(bool(success))
        return bool(success)

    def register(self, username, password):
        now = int(time.time())
        self.refreshPA(username, password)
        self.add_to_db(username, {
                "password":password,
                "last_update":now,# when some uname added to db, first step is update site until 3 monthes and thired is add time.time() for this argument
                "updates":1,
                "logs":{"_"+str(now):"START"}# {"TIME":"TEXT"}
            })
        self.database["userdata"][username]["logs"][now] = "True|UPDATE DONE SUCCESSFULL: the username and password are correct and site updated"
        self.updatedb()
        return True
        try:
            self.refreshPA(username, password)
            self.add_to_db(username, {
                    "password":password,
                    "last_update":now,# when some uname added to db, first step is update site until 3 monthes and thired is add time.time() for this argument
                    "updates":1,
                    "logs":{"_"+str(now):"START"}# {"TIME":"TEXT"}
                })
            self.database["userdata"][username]["logs"][now] = "True|UPDATE DONE SUCCESSFULL: the username and password are correct and site updated"
            self.updatedb()
            return True
        except Exception as e:
            print(e)
            return False

    def get_data(self):
        out = []
        for uname in self.database["userdata"]:
            print(uname, "aaa")
            out.append({
                "uname" : uname,
                "updates" : self.database["userdata"][uname]["updates"],
                "link" : f"{uname}.pythonanywhere.com"
            })
        return out

    def checker(self):
        while True:
            now = int(time.time())
            for uname in self.database["userdata"]:
                pwd = self.database["userdata"][uname]["password"]
                last_update = self.database["userdata"][uname]["last_update"]
                if now >= last_update + 1*60*60*24*30: # equals: monthly auto update
                    try:
                        self.refreshPA(uname, pwd)
                        self.database["userdata"][uname]["last_update"] = now
                        self.database["userdata"][uname]["updates"] = self.database["userdata"][uname]["updates"] + 1
                        self.database["userdata"][uname]["logs"][now] = "True|UPDATE DONE SUCCESSFULL: the username and password are correct and site updated"
                    except Exception as ERROR:
                        self.database["userdata"][uname]["logs"][now] = f"True|UPDATE FAILD: there is an error in up-to-date-ing site, maybe username and password are not correct. error:[{ERROR}]"
                    self.updatedb()
            time.sleep(60)

UP = AlwaysUpMainClass()

@app.route('/')
def index():
    return render_template('index.html', applications=UP.get_data())

@app.route('/add/')
def add_websites():
    print(request.args)
    KEY = request.args.get("key")
    print(KEY)
    if KEY == CLIENT_LOGIN_KEY or 1==1:
        uname = request.args.get("uname")
        password = request.args.get("pass")
        print(uname, password)
        return str(UP.register(uname, password))
    return "Key is not correct :D"


if __name__ == '__main__':
    app.run()
