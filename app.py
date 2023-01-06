#initialize the database connect
import pymongo

client = pymongo.MongoClient("")
db = client.db#db name
print("Connect is success")

#initialize Flask server
from flask import *

app = Flask(
    __name__,
    static_folder = "public",
    static_url_path= "/"
            )
app.secret_key = "any string but secret" #set session's secret key
#set the routing
@app.route("/") 
def index(): 
    return render_template("index.html")

@app.route("/member") 
def member(): 
    if "nickname" in session:
        return render_template("member.html", nickname = session["nickname"])
    else:
        return redirect("/")
# /error?msg = error message
@app.route("/error") 
def error(): 
    message = request.args.get("msg", "error, please contact to our customer service") #default value is "contact to c/s"
    return render_template("error.html", message = message)

@app.route("/signup", methods=["POST"])
def signup():
    #get the data from front-end
    nickname = request.form["nickname"]
    email = request.form["email"]
    password = request.form["password"]
    #based on the received data, interact with database
    collection = db.user
    result = collection.find_one({
        "email":email
    })
    #check the database whether had the same email data or not   
    if result != None:
        return redirect("/error?msg=The email was registered")
    #increase the inputData into the database and finish the registeration
    collection.insert_one({
        "nickname":nickname,
        "email":email,
        "password":password
    })
    return redirect("/")
@app.route("/signin", methods=["POST"])
def signin():
    #get the usersInput from front-end
    email = request.form["email"]
    password = request.form["password"]
    #interact with database
    collection = db.user
    #check whther the email and password are correct
    result = collection.find_one({
        "$and":[
            {"email":email},
            {"password":password}
        ]
    })
    #if cannot find the right data, the login will be failed and direct to the error page
    if result ==None:
        return redirect("/error?msg=email or password error")
    #if login succeed, use Session to save the record and direct to the member page
    session["nickname"] = result["nickname"]
    return redirect("/member")

@app.route("/signout")
def signout():
    #remove the member's formation in Session
    del session["nickname"]
    return redirect("/") 

@app.route("/reset", methods=["POST"])
def edit():
    #reset the password
    email = request.form["email"]
    resetpass1 = request.form["resetpass1"]
    resetpass2 = request.form["resetpass2"]  
    if resetpass1 != resetpass2:
        return redirect("error?msg=password input error")
    collection = db.user
    collection.update_one({
        "email":email
    },{
        "$set":{
            "password":resetpass1
        }
    })
    return render_template("index.html")

@app.route("/delete", methods=["POST"])
def delete():
    email = request.form["email"]
    delpass1 = request.form["delpass1"]
    delpass2 = request.form["delpass2"]
    if delpass1 != delpass2:
        redirect("error?msg=the input of passwords are not the same") 
    collection = db.user
    result = collection.find_one({
        "$and":[
            {"email":email},
            {"password":delpass1}
        ]
    })
    if result ==None:
        return redirect("/error?msg=the email or password is wrong!")
    
    collection.delete_one({
        "email":email
    })
    
    return redirect("/")
app.run(port = 5000)