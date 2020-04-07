import base64
import requests

class github_downloader:
    def __init__(self, urls):
        self.urls = urls
        self.oauth = "youroauthtoken"
        
    def downloadFile(self, url):
        #headers = {'Authorization': 'token %s' % self.oauth}
        #req = requests.get(url, headers=headers)
        req = requests.get(url)
        if req.status_code == requests.codes.ok:
            req = req.json()
            content = base64.b64decode(req['content'])
            return content
        else:
            print("Content was not found.")
            return -1
            
    def downloadFiles(self):
        fileContents = []
        for url in self.urls:
            fileContents.append(self.downloadFile(url))
        return fileContents
