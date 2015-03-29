#-*- coding: utf-8 -*-
'''
Created on May 26, 2014

@author: accioma
'''
import suds, pdb
import logging
import config as C
import os
from suds.client import Client
from suds import sudsobject
from lexus_model import model as M

logging.basicConfig(
         filename="/home/fec/eris.log"
        ,level = logging.ERROR)

class ErisError(Exception):
    def __init__(self, errornumber, message):
        self.errornumber = errornumber
        self.message = message

    def __str__(self):
        return "Error %s. %s" %(self.errornumber, self.message)

def xml_2_byte(filename):
    import base64
    encoded_data = base64.b64encode(open(filename, 'rb').read())
    strg = ''
    for i in xrange((len(encoded_data)/40)+1):
        strg += encoded_data[i*40:(i+1)*40]

    return strg
def send_doc(docstyle, filename):
    logging.basicConfig(level=logging.INFO)

    fn = os.path.join(C.signed_docs_folder, filename)
    if not os.path.isfile(fn):
        raise FileNotFoundError(C.signed_docs_folder, filename)
    logging.info("Enviando: %s: %s" % (docstyle,filename))
    try:
        if docstyle == "comprobante":
            client_rec = Client(C.deliver_url)
            response_rec = client_rec.service.validarComprobante(xml_2_byte(fn))
        elif docstyle == "lote":
            client_rec = Client(C.deliver_batch_url)
            response_rec = client_rec.service.validarLoteMasivo(xml_2_byte(fn))
    except Exception,e:
        logging.exception(e)
        return False
    if hasattr(response_rec, "estado"):
        #Lee el archivo XML para sacar la informacion
        # response_rec.comprobantes
        return response_rec.estado
    return "ERROR"
        #res = sudsobject.asdict(response_rec)
        #print res['estado']
        #for k,v in res.items():
        #    print k
        #    if k == 'comprobantes':
        #        c = sudsobject.asdict(v)
        #        print c
        #print str(response_rec.estado)

def authorize_doc(claveacceso, docstyle):
    from suds.client import Client
    import logging
    logging.getLogger('suds.transport.http').setLevel(logging.INFO)
    logging.info("Autorizando: %s" % (claveacceso))

    try:
        headers = {'Content-Type': 'application/soap+xml; charset="UTF-8"'}
        client_aut = Client(C.authorization_url, headers=headers)
        if docstyle == "comprobante":
            response_aut = client_aut.service.autorizacionComprobante(claveacceso)
        elif docstyle == "lote":
            response_aut = client_aut.service.autorizacionComprobanteLoteMasivo(claveacceso)

        res = sudsobject.asdict(response_aut)
        ak = ""

        if "claveAccesoConsultada" in res.keys():
            ak = res["claveAccesoConsultada"]
        if "autorizaciones" in res.keys():
            aut = sudsobject.asdict(res["autorizaciones"])
            if not aut:
                raise ErisError("102", "La clave de acceso %s no tiene autorizaciones" % claveacceso)
            return (ak, aut)

        for authk, authv in res.items():
            logging.info("k{}, v {}".format(authk, authv))
    except Exception, e:
        logging.exception(e)
    return (ak, None)

def test_send():
    import xml_writer
    m = M()
    fns = [os.path.join(C.signed_docs_folder,\
            "{}.{}.{}.{}.{}.xml".format(int(r[0]),int(r[1]),r[2],r[3],int(r[4]))) \
            for r in m.get_outstanding_vouchers()]
    for fn in fns:
        if os.path.isfile(fn):
            send_doc("comprobante", fn)
    auths = []
    for r in m.get_outstanding_vouchers():
        auth = authorize_doc(r[5], 'comprobante')
#        xml_writer.write_authorized_voucher(*auth)
        auths.append(auth)
    for auth in auths:
        m.proxy_authorization(*auth)

if __name__ == '__main__':
    test_send()
