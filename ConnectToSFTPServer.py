import pysftp
import os
import Configuration.ConfigurationReader as configReader

def RecursiveFolderWalkAndAddFiles(srv, splittedPath, localPath):
    size = len(splittedPath)
    if size == 1:
        firstpart = splittedPath[0]
        if not srv.isdir(firstpart): 
            srv.mkdir(firstpart)
        with srv.cd(firstpart):
            put_r_portable(srv,localPath)
            return 
    else:
        firstpart = splittedPath[0]
        del splittedPath[0]
        if not srv.isdir(firstpart): 
            srv.mkdir(firstpart)
        with srv.cd(firstpart):
            RecursiveFolderWalkAndAddFiles(srv, splittedPath, localPath)

def RecursiveFolderWalk(srv, splittedPath):
    size = len(splittedPath)
    if size == 1:
        firstpart = splittedPath[0]
        if not srv.isdir(firstpart): 
            srv.mkdir(firstpart)
        with srv.cd(firstpart):
            return 
    else:
        firstpart = splittedPath[0]
        del splittedPath[0]
        if not srv.isdir(firstpart): 
            srv.mkdir(firstpart)
        with srv.cd(firstpart):
            RecursiveFolderWalk(srv, splittedPath)

def RecursiveFolderOnlyAddDestinationFolderFiles(srv, splittedPath, localPath):
    size = len(splittedPath)
    if size == 1:
        firstpart = splittedPath[0]
        if not srv.isdir(firstpart): 
            srv.mkdir(firstpart)
        with srv.cd(firstpart):
            PutFilesFromFolder(srv,localPath)
            return 
    else:
        firstpart = splittedPath[0]
        del splittedPath[0]
        if not srv.isdir(firstpart): 
            srv.mkdir(firstpart)
        with srv.cd(firstpart):
            RecursiveFolderOnlyAddDestinationFolderFiles(srv, splittedPath, localPath)


def put_r_portable(sftp, localdir, preserve_mtime=False):
    for entry in os.listdir(localdir):
        localpath = os.path.join(localdir, entry)
        if not os.path.isfile(localpath):
            try:
                print("File is a path " + localpath)
                pass
            except OSError:     
                pass
            put_r_portable(sftp, localpath, preserve_mtime)
        else:
            sftp.put(localpath, preserve_mtime=preserve_mtime)  

def PutFilesFromFolder(sftp, localdir, preserve_mtime=False):
    for entry in os.listdir(localdir):
        localpath = os.path.join(localdir, entry)
        if not os.path.isfile(localpath):
            try:
                print("File is a path " + localpath)
                pass
            except OSError:     
                pass
        else:
            sftp.put(localpath, preserve_mtime=preserve_mtime)  

def CreateSubjectFolders(log_Id, remotepath, config):
    remotePathWithLog_Id = remotepath + '/' + log_Id + '/Maxforce'
    print(remotePathWithLog_Id)
    pathsplitted = remotePathWithLog_Id.split("/")
    srv = LogOntoERDA(config)

    with srv.cd(RecursiveFolderWalk(srv, pathsplitted)): 
        print("file transfer to " + remotepath + " done!")    
    srv.close()

def UploadFilesFromFolders(localPath, remotepath, config):
    pathsplitted = remotepath.split("/")
    srv = LogOntoERDA(config)
    with srv.cd(RecursiveFolderWalkAndAddFiles(srv, pathsplitted, localPath)):
        print("file transfer to " + remotepath + " done!")    
    srv.close()

def UploadFilesFromFolder(localPath, remotepath, config):
    pathsplitted = remotepath.split("/")
    srv = LogOntoERDA(config)
    with srv.cd(RecursiveFolderOnlyAddDestinationFolderFiles(srv, pathsplitted, localPath)):
        print("file transfer to " + remotepath + " done!")    
    srv.close()

def LogOntoERDA(config):
    cnopts = pysftp.CnOpts()
    cnopts.hostkeys = None
    host = configReader.GetHost(config)
    user = configReader.GetUser(config)
    psw = configReader.GetPsw(config)
    srv = pysftp.Connection(host=host, username=user, password=psw,port= 22, cnopts=cnopts)
    return srv
    

# === Main ===
#srv = LogOntoERDA(config)
#remotePath = 'NEXS/Sections/MN/VIP_Projects/ReScale/ReScale2/Trial Master File/19. Data-filer/1. Raw Data'
#localPath = "C:\\Github\\Folder"
#log_Id = '239291_test23'
#pathsplitted = remotePath.split("/")
#srv.close()
