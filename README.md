# Telegram News Bot for AppleSPBevent.ru
### <p>First of all we need to update system<br>
sudo apt-get update<br>
### Next we need to install pip (in ubuntu python included)<br>
sudo apt-get install python-pip<br>
### Next we need to change some settings<br>
pip install -r requirements.txt<br>
add file links.txt with link to the last post on site (optional)<br>
add file inst_link.txt with picture on the last post page (optional)<br>
add file cookies.json with cookie of instagram login (optional)<br>
set ADMIN_TG_ID, TG_CHANNEL, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, REGION, INST_USER, INST_PASSWORD in heroku<br>
### Run or push to heroku script using python clock.py
