# -*- coding: utf-8 -*-

from ftplib import FTP
import config as C
import sys
import os

port = 21
ip = "ftp.fullcarga.com.ec"
password = "facele2014$$"
user = "lexus@fullcarga.com.ec"

def download():
    ftp = FTP(ip)
    ftp.login(user, password)
    a = ftp.cwd("FILES_SIGMA")
    for csv_name in C.csv_files:
        with open(os.path.join("/home/fec/csv", csv_name), "wb") as gFile:
            retr_cmd = 'RETR %s' % csv_name
            ftp.retrbinary(retr_cmd, gFile.write)
    ftp.quit()

def download_eris():
    ftp = FTP(ip)
    ftp.login(user, password)
    a = ftp.cwd("FILES_SIGMA")
    ftp.voidcmd("TYPE I")
    retr_cmd = 'RETR logo_fullcarga.png'
    datasock, estsize = ftp.ntransfercmd(retr_cmd)
    transbytes = 0
    fd =open("/home/fec/fec/fec/fec/lexus/logo.png", "wb")
    while 1:
        buf = datasock.recv(2048)
        if not len(buf):
            break
        fd.write(buf)
        transbytes += len(buf)
        sys.stdout.write("received %d" % transbytes)

        if estsize:
            sys.stdout.write("of %d bytes (%.1f%%)\r" % \
                    (estsize, 100.0 * float(transbytes) / float(estsize)))
        else:
            sys.stdout.write("bytes\r")

        sys.stdout.flush()
    sys.stdout.write("\n")
    fd.close()
    datasock.close()
    ftp.voidresp()
    ftp.quit()


if __name__ == '__main__':
    download_eris()
