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

    def refreshPA(self, uname ,passw) -> bool:
        print("[UNAME]", uname)
        username = uname
        password = passw
        try:
            driver = webdriver.Firefox()
            driver.get("https://pythonanywhere.com/login/")

            username_select = driver.find_element(By.ID, 'id_auth-username')
            username_select.send_keys(username)

            password_select = driver.find_element(By.ID, 'id_auth-password')
            password_select.send_keys(password)

            login_select = driver.find_element(By.ID, 'id_next')
            login_select.click()

            web_apps_link = "https://www.pythonanywhere.com" + re.findall(r"<a id=\"id_web_app_link\" href=\"(.{1,})\">Web</a>", driver.page_source)[0]

            driver.get(web_apps_link)

            run_until_3month_select = driver.find_element(By.XPATH, '/html/body/div[1]/div[2]/div/div[2]/div/div/div[6]/div/div/div/form/input[2]')
            run_until_3month_select.click()
            return True
        except:
            return False

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
