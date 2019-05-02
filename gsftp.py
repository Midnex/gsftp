import argparse, paramiko, os

#   TODO    switch from PySFTP to Paramiko
#           If in known hosts skip login and use RSA key, need to test on unix, since, windows doesn't have known hosts
#   TODO    Use hashlib to check if file is up to date (allows for changes, will add, but not needed)
#   TODO    Flesh out more functions to clean up code
#   TODO    Error handling

# check argsparser for valid formats, and return errors, otherwise pushes to connection if not local to email.
def main(args):
    localPATH = args.localPath
    remotePATH = args.remotePath
    host = args.host
    username = args.user
    password = args.password
    port = args.port
    getFilesArg = args.get
    putFilesArg = args.put
    emailFilesArg = args.email

    print(getFilesArg, putFilesArg)
    if args.file != '':
        fileName = args.file
    else:
        fileName = ''
    if putFilesArg == 1:
        if '"' in localPATH:
            remotePATH = localPATH.split('"')[1][4:]
            localPATH = localPATH.split('"')[0] + os.sep
    if getFilesArg == 1:
        if '"' in localPATH:
            remotePATH = localPATH.split('"')[1][4:]
            localPATH = localPATH.split('"')[0] + os.sep

    makeConnection(localPATH, remotePATH, host, username, password, port, fileName, getFilesArg, putFilesArg, emailFilesArg)


# starts the connection, code is probably crap, not proud of it, need help making it cleaner, but for now works perfectly.
def makeConnection(localPATH, remotePATH, host, username, password, port, fileName, getFilesArg, putFilesArg, emailFilesArg):
    with paramiko.Transport(host, port) as t:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.load_system_host_keys()
        client.connect(host, port=port, username=username, password=password)
        sftp_client = client.open_sftp()
        t.connect(username=username, password=password)
        sftp_client = t.open_session()
        sftp_client = paramiko.SFTPClient.from_transport(t)


        if putFilesArg == 1:
            putFiles(localPATH, remotePATH, sftp_client, fileName)
        if getFilesArg == 1:
            getFiles(localPATH, remotePATH, sftp_client, fileName)
            print('Getting files is not yet supported')
        if emailFilesArg == 1:
            print('E-mailing files is not yet supported')

# pulls files from remote, needs written, will work on later
def getFiles(localPATH, remotePATH, sftp_client, fileName):
    count = 0
    if fileName == None:
        print('do stuff')
        if remotePATH != '':
            sftp_client.chdir(remotePATH)
        remotePATH = ''
        print(sftp_client.listdir(remotePATH))
        for fname in sftp_client.listdir(remotePATH):
            print(fname)
            sftp_client.get(fname, localPATH + fname)
            count += 1

        # counts files transfered!
        if count == 0:
            print('Transfer Failed, or no files found in localPATH')
        else:
            print(count, 'files transfered')
    else:
        print('failed')
        return # needs programmed for single files.

# passes files to remote, needs work!
def putFiles(localPATH, remotePATH, sftp_client, fileName):
    count = 0
    if fileName == None:
        if remotePATH != '':
            try:
                sftp_client.chdir(remotePATH)
            except:
                sftp_client.mkdir(remotePATH, mode=777)
                sftp_client.chdir(remotePATH)
            remotePATH = ''

        # walks through localPath transfering each file
        for root, dir, file, in os.walk(localPATH):
            for fname in file:
                sftp_client.put(root + fname, fname)
                count += 1

        # counts files transfered!
        if count == 0:
            print('Transfer Failed, or no files found in localPATH')
        else:
            print(count, 'files transfered')
    else:
        print('failed')
        return # needs programmed for single files.

# email files from local, or remote, will be done last.
def emailFiles():
    return

# need to finish adding everything in.
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-H', '--host', help='Host name or FTP IP')
    parser.add_argument('-U', '--user', help='Username')
    parser.add_argument('-P', '--password', help='Password')

    parser.add_argument('-e', '--email', action='count', help='send local or remote file to email')
    parser.add_argument('-s', '--put', action='count', help='Put local file to Remote')
    parser.add_argument('-g', '--get', action='count', help='Get local file from remote')

    parser.add_argument('-f', '--file', help='Specify a specific file, supports wild cards')
    parser.add_argument('-L', '--localPath', default='', help='local path to files')
    parser.add_argument('-R', '--remotePath', default='', help='remote path to store files')

    parser.add_argument('-p', '--port', type=int, default='22', help='Port if not 22')
    # parser.add_argument('-r', '--RSA', help='Pass RSA Key')
    args = parser.parse_args()

    if args.host != '':
        main(args)
    else:
        print('Type -h for help.')