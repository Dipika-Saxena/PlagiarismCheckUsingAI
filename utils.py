import requests

class plagueChecker:
    def __init__(self, key):
        self.key = key
        self.baseurl = "https://www.prepostseo.com/apis"

    
    def checkSingle():
        data = {
            'key': self.key
            }
        return self.getResponse(self.baseurl+'/checkSentence', data)
    
    def checkFullArticle(self, article):
        data = {
            'key': self.key,
            'data':article
        }

        return self.getResponse(self.baseurl+'/checkPlag', data)
    

    
    def getResponse(self, url, data):
        try:
            response = requests.post(url, data = data)
            if(response.status_code == 200):
                return response.text
            else:
                print(response.status_code)
        except Exception as e:
            print(e)
            print('could not make request!!')


if __name__ == "__main__":
    pg = plagueChecker('361b62e1609a67f64296bf1958acafa7')
    result = pg.checkFullArticle("""I searched a lot and got confused. I tried to write a piece of code, although I could not fully understand. It didn't work.""")
    print(result)
    