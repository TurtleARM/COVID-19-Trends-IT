class CSV_parser:
    def __init__(self, filename):
        self.filename = filename
    
    def getTitles(self):
        with open(self.filename, "r") as csv:
            titles = csv.readline()
            return titles.split(',')
        
    def parseFileRegioni(self):
        fileObj = open(self.filename, "r")
        dataOnly = fileObj.readlines()[1:]
        return dataOnly
    
    def parseFileNazione(self):
        fileObj = open(self.filename, "r")
        fileStr = fileObj.read()
        dataOnly = '\n'.join(fileStr.split('\n')[1:])
        return dataOnly

