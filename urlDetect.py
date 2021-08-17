from bs4 import BeautifulSoup
import requests
import urllib3
import pyodbc



class UrlDetectModel(object):

    def __init__(self):
        self.action = ""
        self.orig_url = ""
        self.detect_url = ""
        self.status = ""

    

class Database(object):

    def db(self):
        server = "tcp:RTITOADB"
        database = "CCM"
        username = "CCSUser"
        password = "CCSUser!1"
        port = "1433"
        self.cnxn = pyodbc.connect(
                'DRIVER={ODBC Driver 17 for SQL Server};SERVER=' + server + ';DATABASE=' + database + ';UID=' + username + ';PWD=' + password + ';PORT=' + port)
        

    def insert_new(self, url_detect):
        print("exec [dbo].[SP_CCM_Data_Url_Detect] @action = C_DetectResult")
        self.db()
        cursor = self.cnxn.cursor()
        sql = ( "set nocount on;exec [dbo].[SP_CCM_Data_Url_Detect] @action = ?, @orig_url = ?, @detect_url = ?, @status = ?")
        params = (url_detect.action, url_detect.orig_url, url_detect.detect_url, url_detect.status)
        
        cursor.execute(sql, params)
        # cursor.fetchone()
        cursor.commit()
        cursor.close()
        self.cnxn.close()
    
    def send_notice_mail(self):
        self.db()
        cursor = self.cnxn.cursor()
        sql = ( "set nocount on;exec [dbo].[SP_CCM_Data_Url_Detect] @action = ?" )
        params = ("SendNoticeMail")
        cursor.execute(sql, params)
        # cursor.fetchone()
        cursor.commit()
        cursor.close()
        self.cnxn.close()

    def get_orig_url(self):
        l = []
        self.db()
        cursor = self.cnxn.cursor()
        sql = ( "set nocount on;exec [dbo].[SP_CCM_Data_Url_Detect] @action = ?" )
        params = ("GetUrlDetectSource")
        cursor.execute(sql, params)
       # cursor.fetchone()
        for row in cursor:
            l.append(row.wiki_URL)
        cursor.commit()
        cursor.close()
        self.cnxn.close()
        return l

class UrlDetect(object):

    def new(self, rs):
       for url in rs:
            orig_url = url #'https://wikiqa.realtek.com/pages/viewpage.action?pageId=1217471'
            print(orig_url)

            if(orig_url.find("href") > 0):
  
                soup = BeautifulSoup(orig_url,'lxml')

                for a in soup.find_all('a', href=True):  
                        print("a=",a)                  
                    # if(a['href'].find('http') == 0):
                        print("Found the URL:", a['href'])
                        try:
                            detect_url = a['href']                  
                            status= requests.get(a['href']).status_code
                            print(requests.get(a['href']).status_code)

                            self.call_insert_sp(orig_url, detect_url, status)
                        except Exception:
                            pass
                        continue   
                        

            else:
                res = requests.get(orig_url)
                soup = BeautifulSoup(res.text,'lxml')      

                try:
                    rs = res.status_code
                    print(rs)

                    self.call_insert_sp(orig_url, orig_url, rs)
                except Exception:
                    pass 
                
            
                items = soup.select('div#main-content a')
                for b in items:
                    if(b.get('href','').find('http') == 0):  
                        try:
                            detect_url = b.get('href')
                            print(b.get('href'))

                            status= requests.get(b.get('href')).status_code
                            print(requests.get(b.get('href')).status_code)

                            self.call_insert_sp(orig_url, detect_url, status)
                        except Exception:
                            pass
                        continue   
        

    def call_insert_sp(self, orig_url, detect_url, status):
        obj = UrlDetectModel() 
        db = Database()
                         
        obj.action = "C_DetectResult"
        obj.orig_url = orig_url
        obj.detect_url = detect_url
        obj.status = status
        
        print("new : " + obj.detect_url.encode("utf8").decode("cp950", "ignore"))              
        db.insert_new(obj)

    
    def send_notice_mail(self):
        db = Database()
        db.send_notice_mail()
        print("[dbo].[SP_CCM_Data_Url_Detect] @action= SendNoticeMail \n")
        
    
    def init(self):
        print("[dbo].[SP_CCM_Data_Url_Detect] @action= GetUrlDetectSource \n")
        db = Database()
        return db.get_orig_url()
        
       


if __name__ == "__main__":
    m = UrlDetect()
    rs = m.init()
    m.new(rs)
    m.send_notice_mail()



     