from seleniumwire import webdriver
from selenium.webdriver.common.by import By
from pynput.keyboard import Key, Controller 
import time
import discum
import json
import requests
from pymongo import MongoClient

#aşağıda yer alan 2 def fonksiyonu kullanıcı id değerlerini almak için --> https://stackoverflow.com/questions/72457579/not-able-to-scrap-an-entire-servers-user-ids-on-discord-using-discum
def close_after_fetching(resp, guild_id):
    if bot.gateway.finishedMemberFetching(guild_id):
        lenmembersfetched = len(bot.gateway.session.guild(guild_id).members)
        print(str(lenmembersfetched) + ' members fetched')
        bot.gateway.removeCommand({'function': close_after_fetching, 'params': {'guild_id': guild_id}})
        bot.gateway.close()

def get_members(guild_id, channel_id):
    bot.gateway.fetchMembers(guild_id, channel_id, keep='all', wait=1)
    bot.gateway.command({'function': close_after_fetching, 'params': {'guild_id': guild_id}})
    bot.gateway.run()
    bot.gateway.resetSession()
    return bot.gateway.session.guild(guild_id).members


c = open("chanelid.txt", "a")    #chanelid.txt dosyasını açıyoruz
r = open("rsp.json", "a+")       #rsp.json dosyasını açıyoruz
u = open("users.txt", "a")       #users.txt dosyasını açıyoruz

#web driver eklentisini kullanarak chrome driverı açıyoruz.[kullanılacak tarayıcıya göre değişmeli]
driver = webdriver.Chrome(
    r"chromedriver.exe"
)

#klavye kontrolü için 
keyboard = Controller()
# 40 saniye boyunca işlem gerçekleşmez ise kapatması için
driver.set_page_load_timeout(40)
#açılan pencereyi büyütüyoruz 
driver.maximize_window()

#login işlemi için gerekli sayfaya gidiyoruz
driver.get('https://discord.com/login')
time.sleep(2)

#mail ve şifre bilgilerini giriyoruz
driver.find_element(By.NAME,'email').send_keys('mail')
time.sleep(1)
driver.find_element(By.NAME,'password').send_keys("password")
time.sleep(2)
#giriş yap butonuna tıklıyoruz
driver.find_element(By.CLASS_NAME,'sizeLarge-3mScP9').click()
print("3****************************OoO****************************")
time.sleep(25)

#cookie ve token için anasayfaya gidiyoruz
driver.get('https://discord.com/channels/@me')
time.sleep(5)

#Token ve Cookie bilgilerini kullanıcıdan alıyoruz
#Token -> https://stackoverflow.com/questions/67348339/any-way-to-get-my-discord-token-from-browser-dev-console

token=""
token = driver.execute_script("return (webpackChunkdiscord_app.push([[''],{},e=>{m=[];for(let c in e.c)m.push(e.c[c])}]),m).find(m=>m?.exports?.default?.getToken!==void 0).exports.default.getToken()")

#request için cooke değeri lazım
cj= open("cookies.json", "w")
cookies = driver.get_cookies()
j=json.dumps(cookies)
cookie=""
for e in range(len(cookies)):
    cookie += cookies[e]['name'] + "=" + cookies[e]['value'] + "; "

#kullanıcı id değerlerini çekebilmek için token değerlerini eşitliyoruz
bot = discum.Client(token=token)

#guildlist değerini path olarak alıyoruz
guild_list = driver.find_elements(By.XPATH, '//*[@id="app-mount"]/div[2]/div/div[1]/div/div[2]/div/div[1]/nav/ul/div[2]/div[3]/div')

#Bu döngü dc nn sol tarafında bulunan server listesine 
#giderek serverlara tıklar ve açılan ilk sohbetin id değerini alır
for X in guild_list:
    guild = X.find_elements(By.CSS_SELECTOR, 'div[data-list-item-id*="guildsnav__"]')
    if len(guild) ==1 :
        guild=guild[0]
        guild_id = guild.get_attribute('data-list-item-id').split('___')[1]
        guild.click()
        channel_ids = driver.find_elements(By.CSS_SELECTOR,'#channels > ul > li.containerDefault-YUSmu3.selected-2TbFuo > div > div > a')
        print(channel_ids)
        rsp = []
        for channel in channel_ids:
            channel_id = channel.get_attribute('data-list-item-id').split('___')[1]
            print(guild_id + "," + channel_id)
            c.write(guild_id + "," + channel_id + "\n")
            if len(guild_id) > 0 and len(channel_id) > 0:
                memberslist = []
                members = get_members(guild_id,channel_id)
                #kullanıcı id değerlerini ve profil bilgilerini istek ataraz alıyoruz
                s=0
                for memberID in members:
                    memberslist.append(memberID)
                    # for element in memberslist:
                    u.write(memberID + "," + guild_id + '\n')
                    query_string = {"with_mutual_guilds": "true", "with_mutual_friends_count": "false", "guild_id": guild_id}
                    url = "https://discord.com/api/v9/users/" + memberID + "/profile"
                    # url = "https://discord.com/api/v9/users/000000000000000000/profile - kendi headerınızı eklemeniz gerek"
                    headers = {
                        "Host" : "discord.com",
                        "Cookie" : cookie,
                        "Sec-Ch-Ua" : '"Not?A_Brand";v="8", "Chromium";v="108", "Microsoft Edge";v="108"', 
                        "X-Super-Properties" : "pbmRvd3MiLCJicm93c2VyIjoiQ2hyb21lIiwiZGV2aWNlIjoiIiwic3lzdGVtX2xvY2FsZSI6InRyIiwiYnJvd3Nlcl91c2VyX2FnZW50IjoiTW96aWxsYS81LjAgKFdpbmRvd3MgTlQgMTAuMDsgV2luNjQ7IHg2NCkgQXBwbGVXZWJLaXQvNTM3LjM2IChLSFRNTCwgbGlrZSBHZWNrbykgQ2hyb21lLzEwOC4wLjAuMCBTYWZhcmkvNTM3LjM2IEVkZy8xMDguMC4xNDYyLjU0IiwiYnJvd3Nlcl92ZXJzaW9uIjoiMTA4LjAuMC4wIiwib3NfdmVyc2lvbiI6IjEwIiwicmVmZXJyZXIiOiIiLCJyZWZlcnJpbmdfZG9tYWluIjoiIiwicmVmZXJyZXJfY3VycmVudCI6IiIsInJlZmVycmluZ19kb21haW5fY3VycmVudCI6IiIsInJlbGVhc2VfY2hhbm5lbCI6InN0YWJsZSIsImNsaWVudF9idWlsZF9udW1iZXIiOjE2NTQ4NSwiY2xpZW50X2V2ZW50X3NvdXJjZSI6bnVsbH0=",
                        "Authorization" : token,
                        "User-Agent" : "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36 Edg/108.0.1462.76",
                        "X-Discord-Locale" : "tr",
                        "Sec-Ch-Ua-Platform" : "Windows",
                        "Accept" : "*/*",
                        "Sec-Fetch-Site" : "same-origin",
                        "Sec-Fetch-Mode" : "cors",
                        "Sec-Fetch-Dest" : "empty",
                        "Referer" : "https://discord.com/channels/"+guild_id+ "/" +channel_id,
                        "Accept-Encoding" : "gzip, deflate",
                        "Accept-Language" : "tr,en;q=0.9,en-GB;q=0.8,en-US;q=0.7"
                    }
                           
                    time.sleep(1)                    
                    response = requests.request("GET", url, headers=headers)
                    #dönen cevabı json formatına çeviriyoruz
                    j = json.loads(response.text)
                    rsp.append(j)     
                    print(s)
                    s+=1    
            #kaydedilen değeri json dosyasına yazdırıyoruz                           
            r.write(json.dumps(rsp))
            
#kullanıcı id değerlerini bulundukları sunucu id lerini ve kanal id , sohbet idlerini dosyalara kaydediyoruz                  
print("DOSYAYA YAZILIYOR")

# Mongodb bağlantısı kuruyoruz ( aşağıda yer alan client web bağlantısı ) aşaması
#alınacak bağlantı adresi kullanılan python versiyonuna göre değişiklik gösterebilir bu yüzden çalıştırılmadan önce alınması gerekli.
client = MongoClient("{mongodb için gerekli bağlantı adresi}")
  
# database ve collection oluşturuyoruz/seçiyoruz
db = client["data"]
Collection = db["data"]
 
# json dosyasını mongodb ye yüklüyoruz.
with open('rsp.json') as file:
    file_data = json.load(file)

if isinstance(file_data, list):
    Collection.insert_many(file_data) 
else:
    Collection.insert_one(file_data)
