import asyncio, aiohttp, random, base64, json, aiofiles

class generator:
    def __init__(self, usrname="xoloking", password="xoloking123", proxy_file="proxies.txt", proxy_type="http", threads=1, capbypassKey=None, account_file="accounts.txt"):
        if not capbypassKey:
            raise Exception("need to buy a capbypass key to make it work")
        self.capbypassKey = capbypassKey
        self.username, self.password = usrname, password
        self.solver = "https://capbypass.com/api/createTask"
        with open(proxy_file, 'r') as file:
            self.proxies = [line.strip() for line in file.readlines()]
            self.proxy_type = proxy_type
        self.threads = threads
        self.publicKey = "A2A14B1D-1AF3-C791-9BBC-EE33CC7A0A6F"
        self.account_file = account_file
        
    def generate_account_name(self, username=None):
        if not username: 
            username = self.username
            
        return username + "".join((str(random.randint(0, 9))) for i in range(5))
    
    async def generate_xtoken(self, session=None, proxy=None):
        try:
          reset_con = not bool(session)
          if not session:
              session = aiohttp.ClientSession()
          x_token  =  (await session.post("https://catalog.roblox.com/v1/catalog/items/details", proxy=proxy, timeout=5)).headers.get("x-csrf-token")
          if reset_con:
              await session.close()
          return x_token
        except:
            return None
    
    async def get_captcha_token(self, session, proxy):
     try:
        x_token = await self.generate_xtoken(session=session, proxy=proxy)
        if not x_token: return
        response = await session.post("https://auth.roblox.com/v2/signup", proxy=proxy, headers={"x-csrf-token": x_token, "User-Agent":"Mozilla/5.0 (Windows; U; Windows CE) AppleWebKit/534.47.7 (KHTML, like Gecko) Version/4.1 Safari/534.47.7"}, json={"username":self.generate_account_name(self.username), "password": self.password, "birthday": "1962-04-08T23:00:00.000Z", "gender": 2, "isTosAgreementBoxChecked": True, "agreementIds": ["848d8d8f-0e33-4176-bcd9-aa4e22ae7905", "54d8a8f0-d9c8-4cf3-bd26-0cbf8af0bba3"]})
        if response.status == 403:
            return json.loads(base64.b64decode(response.headers.get("rblx-challenge-metadata")))
     except:
         return
    
    async def create_account(self, session, proxy, username, Rblx_Chllange_Id, Rblx_Challenge_Metadata):
     try:
        x_token = await self.generate_xtoken(session=session, proxy=proxy)
        if not x_token: return
        response = await session.post("https://auth.roblox.com/v2/signup", proxy=proxy, headers={"Origin": "https://www.roblox.com", "referrer": "https://www.roblox.com/login", "x-csrf-token": x_token, "User-Agent":"Mozilla/5.0 (Windows; U; Windows CE) AppleWebKit/534.47.7 (KHTML, like Gecko) Version/4.1 Safari/534.47.7", "Rblx-Challenge-Id": Rblx_Chllange_Id, "Rblx-Challenge-Metadata": Rblx_Challenge_Metadata, "Rblx-Challenge-Type": "captcha",}, json={"username":username, "password": self.password, "birthday": "1962-04-08T23:00:00.000Z", "gender": 2, "isTosAgreementBoxChecked": True, "agreementIds": ["848d8d8f-0e33-4176-bcd9-aa4e22ae7905", "54d8a8f0-d9c8-4cf3-bd26-0cbf8af0bba3"]})
        if response.status == 200:
            resp = await response.json()
            print(f"generated {resp['userId']}")
            async with aiofiles.open(self.account_file, mode='a') as file:
                await file.write(f"{username}:{self.password}:{response.cookies.get('.ROBLOSECURITY')}\n")
            return await response.json()
        return await response.json()
     except Exception as e:
         return e
        
    async def solve_captcha(self, session, proxy, blob):
        response = await session.post(self.solver, json={"clientKey": self.capbypassKey, "task": {"type":"FunCaptchaTask","websiteURL":"https://www.roblox.com/","websitePublicKey":self.publicKey,"websiteSubdomain":"roblox-api.arkoselabs.com","data[blob]": blob,"proxy": str(proxy)}})
        if response.status == 403:
            raise Exception(response)
        jsonify = (await response.json())
        if not jsonify.get("solution"): return "" 
        return jsonify.get("solution", {}).get("token")
    
    async def generate_account(self):
        while True:
            async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(limit=None)) as session:
                proxy = random.choice(self.proxies)
                if len(proxy.split(":")) == 2:
                    proxy = random.choice(self.proxies).split(":")
                    proxy = f"{self.proxy_type}://" + proxy[0] + ":" + proxy[1]
                elif len(proxy.split(":")) == 4:
                    proxy = random.choice(self.proxies).split(":")
                    proxy = f"{self.proxy_type}://" + proxy[2] + ":" + proxy[3] + "@" + proxy[0] + proxy[1]
                else:
                    print(f"{proxy} invalid")
                    self.proxies.remove(proxy)
                    continue
            
                blob_data = await self.get_captcha_token(session, None) 
                if not blob_data: continue
                solved = await self.solve_captcha(session, None, blob_data["dataExchangeBlob"])
                data = {"unifiedCaptchaId": blob_data["unifiedCaptchaId"], "captchaToken": solved, "actionType": "Signup"}
                print(data)
                print(await self.create_account(session, None, self.generate_account_name(self.username), blob_data["unifiedCaptchaId"], base64.b64encode(json.dumps(data).encode("utf-8")).decode("utf-8")))
                
    
    async def start(self):
        while True:
            tasks = [self.generate_account() for i in range(self.threads)]
            await asyncio.gather(*tasks)

asyncio.run(generator(capbypassKey="0a22aa10507090fe76380eda21f05f36cfe65cd6").start())