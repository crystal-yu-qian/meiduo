from django.core.files.storage import Storage


class FastDFSStorage(Storage):
    def _open(self,name,mode= "rb"):
        pass
    def _save(self,name,context,max_length=None):
        pass
    def url(self, name):
        return "http://192.168.17.84:8888/" + name
