# -*- encoding: utf-8 -*-
##############################################################################
#
# OpenERP, Open Source Management Solution
# Copyright (c) 2014 KIDDYS HOUSE SAC. (http://kiddyshouse.com).
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from osv import osv, fields
import urllib2
import urllib
import cookielib
import re

import logging
_logger = logging.getLogger(__name__)


def get_url(url):
    """Return a string of a get url query"""
    try:
        import urllib
        objfile = urllib.urlopen(url)
        rawfile = objfile.read()
        objfile.close()
        return rawfile
    except ImportError:
        raise Exception ('Error: Unable to import urllib !')
    except IOError:
        raise Exception ('Error: Web Service [%s] does not exist or it is non accesible !' % url)

class res_partner_cookie_reniec(osv.osv):
    _name= 'res.partner.cookie.reniec'
    _columns = {
        'name':fields.char('Codigo', size=4),
        'cookie_reniec': fields.text('Cookie reniec'),
        'urls': fields.char('Enlace',size=200),     
    }

    def open_url(self, cr, uid, ids, context):
        drawing_url = self.browse(cr, uid, ids)[0].urls
        if drawing_url:
            return { 'type': 'ir.actions.act_url', 'url': drawing_url, 'nodestroy': True, 'target': 'new',}
        return True


class res_partner(osv.osv):
    _name= 'res.partner'
    _inherit = 'res.partner'
    _columns = {
        'doc_type': fields.selection([('1','DOCUMENTO NACIONAL DE IDENTIDAD (DNI)'),('6','REGISTRO ÚNICO DE CONTRIBUYENTES'),('4','CARNET DE EXTRANJERIA'),('7','PASAPORTE'),('A','CÉDULA DIPLOMÁTICA DE IDENTIDAD'),('0','OTROS TIPOS DE DOCUMENTOS')],'Tipo Doc. Indentidad',required=False,),
        'doc_number': fields.char('RUC/DNI ',size=32),
        'apellidopaterno': fields.char('Apellido paterno', size=64),
        'apellidomaterno': fields.char('Apellido materno', size=64),
        'nombres': fields.char('Nombres', size=64),

        'codigo_reg_sunat_reniec':fields.char('Codigo', size=4),

        #sunat
        'sunat_state': fields.char('Estado del Contribuyente',size=64),
        'sunat_condicion': fields.char('Condicion del Contribuyente',size=128),
        'sunat_agente_retencion': fields.boolean('Agente de Retencion', help="Es agente de retencion"),
        'sunat_retencion_describe': fields.char('Descripcion Agente Retencion'),
        #Como llega a kiddys
        'llego_kiddys': fields.selection([
            ('1','POR RECOMENDACION'),
            ('2','PUBLICIDAD EN MULTITOP'),
            ('3','PROGRANA MAMA FELIZ'),
            ('4','PASABA POR AQUI'),
            ('5','LO VI POR FACEBOOK'),
            ('6','BUSCANDO POR INTERNET'),
            ('7','OTROS')],'COMO LLEGO A KIDDYS',required=False,),
        'otro_llego_kiddys': fields.char('OTRA FORMA',size=128),

        #venta campo
        'venta_campo': fields.selection([
            ('1','LA VICTORIA'),
            ('2','SURCO'),
            ('3','SAN MIGUEL'),
            ('4','PLAZA NORTE'),
            ('5','PLAZA SUR'),
            ],'Venta campo',),

    }

    _defaults = {
        'doc_type': '1',
    }

    _sql_constraints = [
        ('doc_number_uniq', 'unique(doc_number)', 'Numero de documento ya existe!'),
    ]

    def create(self, cr, uid, vals, context=None):
        #if ('doc_number' in vals):
        #if vals['doc_number'] != False: 
        #    vals.update({'doc_number': vals['doc_number'].strip()})
        new_id = super(res_partner, self).create(cr, uid, vals, context=context)
        for partner in self.browse(cr, uid, [new_id], context=context):
            doc_number = partner.doc_number
        #_logger.error("DOC_TUY111: %r", doc_number)
        if doc_number:
            vals.update({'doc_number': vals['doc_number'].strip()})
            self.write(cr, uid, [new_id], vals, context=context)
        return new_id 

    def onchange_type(self, cr, uid, ids, is_company, doc_type, context=None):
        value = {}
        value['title'] = False
        if is_company:
            domain = {'title': [('domain', '=', 'partner')]}
            value['doc_type'] = '6'
            value['apellidopaterno'] = False
            value['apellidomaterno'] = False
            value['nombres'] = False
        else:
            domain = {'title': [('domain', '=', 'contact')]}
            value['doc_type'] = '1'
        return {'value': value, 'domain': domain}


    #OBTENIENDO DATOS DE https://cel.reniec.gob.pe/valreg/valreg.do FOUND
    def onchange_doc_number_RENIEC(self, cr, uid, ids, doc_type, doc_number, is_company, context=None):
        #response = urllib2.urlopen('http://www.sunat.gob.pe/w/wapS01Alias?ruc=20514540145')
        #html = response.read()
        #url='http://www.sunat.gob.pe/w/wapS01Alias?ruc=20553291501'
        #_logger.error("DOC_TUY: %r", doc_number)
        #str1 = raw_input("NGRESO CODIGO:")
        #_logger.error("DOC_TUY: %r", str1)
        res = {'value':{}}
        if doc_number:
            if doc_type in ('6') and len(doc_number) == 11:
                url="http://www.sunat.gob.pe/w/wapS01Alias?ruc="+doc_number
                data = get_url(url)

                res_empres = re.findall('''<small><b>N&#xFA;mero Ruc. </b> \d+ - .* <br/></small>''', data)
                for d in res_empres:
                    name_empresa =  (d[46:-14])
                    _logger.error("wennnnnnnnn----: %r", name_empresa)
                    import HTMLParser
                    hparser=HTMLParser.HTMLParser()
                    res['value']['name'] = hparser.unescape(hparser.unescape(name_empresa.decode('latin_1')))
        
                res_direcc = re.findall('''<small><b>Direcci&#xF3;n.</b><br/>.*</small><br/>''', data)
                for d in res_direcc:
                    direccion =  (d[34:-13])
                    import HTMLParser
                    hparser=HTMLParser.HTMLParser()
                    res['value']['street'] = hparser.unescape(hparser.unescape(direccion.decode('latin_1')))                 
                return res
            elif doc_type in ('1') and len(doc_number) == 8:

                
                args = []
                reniec_obj = self.pool.get('res.partner.cookie.reniec')
                ids = reniec_obj.search(cr, uid, args, offset=0, limit=None, order=None, context=None, count=False)
                img=None
                micookie = None
                for value in reniec_obj.browse(cr, uid, ids):
                    img = value.name
                    micookie = "JSESSIONID="+value.cookie_reniec
                    #_logger.error("MI Cwwwwww: %r", micookie)

                dni= doc_number
                #---------------------
                #dni='42995230'
                #img=codigo_reg_sunat_reniec
                #img='20M7'
                url="https://cel.reniec.gob.pe/valreg/valreg.do"
                
                #micookie="JSESSIONID=97657851ce58c6a187eb98c45b3af7caaa9519ed812.mALvn6iL-B9zpAzzmMTBpQ8Iq6iUaNaKahD3lN4PagSLa34Iah8K-xuL-AeSa69zaMSLa6aPa64Obh0QawSHc30Ka2bEaAjzawTwp65ynh4IqAjIokjx-ArJmwTKngaLc3iPaN8Sax8xf2bQmkLMnkqxn6jAmljGr5XDqQLvpAe_"

                #cookie_j = cookielib.CookieJar()  
                #cookie_h = urllib2.HTTPCookieProcessor(cookie_j)  
                #opener = urllib2.build_opener(cookie_h)  
                #opener.open("https://cel.reniec.gob.pe/valreg/codigo.do")  
                #opener.open("https://cel.reniec.gob.pe/valreg/valreg.do")
                #micookie=None
                #for num, cookie in enumerate(cookie_j):  
                #    micookie=cookie.name + "="+ cookie.value
                #_logger.error("MI COOKIE WEB: %r", micookie)
                #----------------
                
                #data="accion=buscar&tecla_7=5&tecla_8=6&tecla_9=0&tecla_4=4&tecla_5=9&tecla_6=7&tecla_1=2&tecla_2=8&tecla_3=1&tecla_0=3&nuDni="+dni+"&imagen="+img+"&bot_consultar.x=113&bot_consultar.y=16"
                data="accion=buscar&tecla_7=5&tecla_8=2&tecla_9=0&tecla_4=1&tecla_5=6&tecla_6=9&tecla_1=8&tecla_2=7&tecla_3=3&tecla_0=4&nuDni="+dni+"&imagen="+img+"&bot_consultar.x=75&bot_consultar.y=23"
                req = urllib2.Request(url)
                req.add_header('User-Agent', 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:28.0) Gecko/20100101 Firefox/28.0')
                req.add_header('Cookie',micookie)
                page = urllib2.urlopen(req,data)
                response=page.read();page.close()
                res_empres = re.findall('''<td height="63" class="style2" align="center">\D+<br>''', response)
                name_empresa = None
                for d in res_empres:
                    name_empres =  (d[66:-4])

                    n = name_empres.split()    
                    name_empresa = ' '.join(name_empres.split())
                    #_logger.error("partner000 -: %r", name_empresa)
                    import HTMLParser
                    hparser=HTMLParser.HTMLParser()

                    if len(n)==4:
                        #res['value']['name'] = hparser.unescape(hparser.unescape(name_empresa.decode('latin_1')))
                        #res['value']['name'] = n[2] + ' ' +  n[3]+ ' ' + n[0] + ' ' +  n[1]   
                        res['value']['name'] = (n[2] + ' ' +  n[3]+ ' ' + n[0] + ' ' +  n[1]).decode('latin_1')
                        #_logger.error("partner -: %r", res['value']['name'])
                        res['value']['apellidopaterno'] = (n[2]).decode('latin_1')
                        res['value']['apellidomaterno'] = (n[3]).decode('latin_1')
                        res['value']['nombres'] = (n[0] + ' ' + n[1]).decode('latin_1')
                    if len(n)==3:
                        res['value']['name'] = (n[1] + ' ' +  n[2]+ ' ' + n[0]).decode('latin_1')
                        res['value']['apellidopaterno'] = (n[1]).decode('latin_1')
                        res['value']['apellidomaterno'] = (n[2]).decode('latin_1')
                        res['value']['nombres'] = (n[0]).decode('latin_1')

                    if len(n)==6 and n[2]=='DE':
                        res['value']['name'] = (n[2] + ' ' +  n[3]+ ' ' + n[4]+ ' ' + n[5]+ ' ' + n[0]+ ' ' + n[1]).decode('latin_1')
                        res['value']['apellidopaterno'] = (n[2]+ ' ' + n[3]+ ' ' + n[4]).decode('latin_1')
                        res['value']['apellidomaterno'] = (n[5]).decode('latin_1')
                        res['value']['nombres'] = (n[0]+ ' ' + n[1]).decode('latin_1')

                    if len(n)==6 and n[2]!='DE':
                        res['value']['name'] = (n[2] + ' ' +  n[3]+ ' ' + n[4]+ ' ' + n[5]+ ' ' + n[0]+ ' ' + n[1]).decode('latin_1')
                        res['value']['apellidopaterno'] = (n[2]).decode('latin_1')
                        res['value']['apellidomaterno'] = (n[3]+ ' ' + n[4]+ ' ' + n[5]).decode('latin_1')
                        res['value']['nombres'] = (n[0]+ ' ' + n[1]).decode('latin_1')
    
                #res['value']['name'] = name_empresa
                #JAVIER(0) SALAZAR(1) CARLOS(2)
                return res
            else:
                res['value']['street'] = False
                res['value']['name'] = False
                #res['value']['doc_number'] = False
                return res
        else:
            #res['value']['street'] = False
            #res['value']['name'] = False
            #res['value']['doc_number'] = False
            return res



    #OBTENIENDO DATOS DE http://aplicaciones.pronabec.gob.pe/Feria2014/Servicios/Get_RENIEC FOUND
    def onchange_doc_number_pronabec(self, cr, uid, ids, doc_type, doc_number, is_company, context=None):
        #response = urllib2.urlopen('http://www.sunat.gob.pe/w/wapS01Alias?ruc=20514540145')
        #html = response.read()
        #url='http://www.sunat.gob.pe/w/wapS01Alias?ruc=20553291501'
        #_logger.error("DOC_TUY: %r", doc_number)
        #str1 = raw_input("NGRESO CODIGO:")
        #_logger.error("DOC_TUY: %r", str1)
        res = {'value':{}}
        import HTMLParser
        hparser=HTMLParser.HTMLParser()
        if doc_number:
            if doc_type in ('6') and len(doc_number) == 11:
                url="http://www.sunat.gob.pe/w/wapS01Alias?ruc="+doc_number
                data = get_url(url)
 		_logger.error("WEEEEEEEEEEEE----: %r", data)
                #Obteniendo la razon social
                res_empres = re.findall('''<small><b>N&#xFA;mero Ruc. </b> \d+ - .* <br/></small>''', data)
                for d in res_empres:
                    name_empresa =  (d[46:-14])
                    #_logger.error("WEEEEEEEEEEEE----: %r", data)                    
                    res['value']['name'] = hparser.unescape(hparser.unescape(name_empresa.decode('latin_1')))
                
                #Obteniendo la direccion de la empresa
                res_direcc = re.findall('''<small><b>Direcci&#xF3;n.</b><br/>.*</small><br/>''', data)
                for d in res_direcc:
                    direccion =  (d[34:-13])
                    res['value']['street'] = hparser.unescape(hparser.unescape(direccion.decode('latin_1')))                 
                
                #Obteniendo estado del contribuyente
                res_estado = re.findall('''<small><b>Estado.</b>.*</small><br/>''', data)
                for d in res_estado:
                    estado = (d[21:-13])
                    #_logger.error("ESTADO----: %r", estado)        
                    res['value']['sunat_state'] = estado

                #Obteniendo el telefono
                res_telefono = re.findall('''<small><b>Tel&#xE9;fono.*</b><br/>.*</small><br/>''', data)                
                for d in res_telefono:
                    telefono = (d[36:-13])   
                    #_logger.error("ESTADO----: %r", res_telefono)                       
                    res['value']['phone'] = telefono

                #Obteniendo condicion de contribuyente
                res_condicion = re.findall('''<small>Situaci&#xF3;n.<b> .*</b></small><br/>''', data)                
                for d in res_condicion:
                    condicion = (d[26:-17])   
                    #_logger.error("ESTADO----: %r", res_telefono)                       
                    res['value']['sunat_condicion'] = condicion

                #Obteniendo agente de retencion
                res_agente = re.findall('''<strong>\w{0,2}</strong> .*\r\n''', data)                
                for d in res_agente:
                    agente = (d[8:10])   
                    #_logger.error("AGENTE----: %r", (d[20:-2]))
                    if agente == 'SI':
                        res['value']['sunat_agente_retencion'] = True
                        res['value']['sunat_retencion_describe'] = (d[20:-2])

                res['value']['ref'] = doc_number
                res['value']['vat'] = 'PER' + doc_number #PARA VALIDAR RUC DEBE DE INICIAR CON PER
                res['value']['vat_subjected'] = True
                return res

            elif doc_type in ('1') and len(doc_number) == 8:                
                args = []
                reniec_obj = self.pool.get('res.partner.cookie.reniec')
                ids = reniec_obj.search(cr, uid, args, offset=0, limit=None, order=None, context=None, count=False)
                img=None
                micookie = None
                for value in reniec_obj.browse(cr, uid, ids):
                    img = value.name
                    micookie = "JSESSIONID="+value.cookie_reniec
                    #_logger.error("MI Cwwwwww: %r", micookie)

                dni= doc_number
                #---------------------

                url="http://aplicaciones.pronabec.gob.pe/Feria2014/Servicios/Get_RENIEC"
                
                micookie="__RequestVerificationToken_L0ZlcmlhMjAxNA2=bzJyrpSo_yH--r4fpeIy1JMVdenQ3h_bo67Sf6BKPHIwT7_RmA0hk1vXnH1sPYlzZDnMirH2Lrs6tSTSDR8hvl-IsenZPfVBGtqd_giqMiQ1"

                #cookie_j = cookielib.CookieJar()  
                #cookie_h = urllib2.HTTPCookieProcessor(cookie_j)  
                #opener = urllib2.build_opener(cookie_h)  
                #opener.open("https://cel.reniec.gob.pe/valreg/codigo.do")  
                #opener.open("https://cel.reniec.gob.pe/valreg/valreg.do")
                #micookie=None
                #for num, cookie in enumerate(cookie_j):  
                #    micookie=cookie.name + "="+ cookie.value
                #_logger.error("MI COOKIE WEB: %r", micookie)
                #----------------
                
                #data="accion=buscar&tecla_7=5&tecla_8=2&tecla_9=0&tecla_4=1&tecla_5=6&tecla_6=9&tecla_1=8&tecla_2=7&tecla_3=3&tecla_0=4&nuDni="+dni+"&imagen="+img+"&bot_consultar.x=75&bot_consultar.y=23"
                data="__RequestVerificationToken=NG_F7TKTxs-HAmDaa7iQcdt214TUli5hHrLElSYv8reoYbFNH_Rj_3jhqyn9wmNSg3797Cyf_5fcvQKYFYbj_jTMARWXPs-ckdyNQlPYBJk1&Formulario_Nro_Documento="+dni+"&Formulario_Ape_Paterno=&Formulario_Ape_Materno=&Formulario_Ape_Nombres=&Formulario_Fecha_Nacimiento=&Formulario_Ocupacion=&Formulario_Grado=&Formulario_Tercio=&Formulario_Correo_Electronico=&Formulario_Correo_Electronico_Repita=&Formulario_Telefono_Contacto=&Formulario_Pais=&Formulario_Especialidad="
                req = urllib2.Request(url)
                req.add_header('User-Agent', 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:28.0) Gecko/20100101 Firefox/28.0')
                req.add_header('Cookie',micookie)
                page = urllib2.urlopen(req,data)
                response=page.read();page.close()
                
                lista0= (response.strip("{}; "))
                lista1 = lista0.replace('"', "")

                lista2 = lista1.split(',')
                Apaterno= lista2[1]
                Amaterno= lista2[2]
                Nombres= lista2[3]
		
		#COMENTADO POR ERRORES AL RECORTAR LA CADENA
                #res['value']['name'] = Apaterno.lstrip("apePaterno:" ) +' ' +Amaterno.lstrip("apeMaterno:" ) + ' ' +Nombres.lstrip("Nombres:" )
                #res['value']['apellidopaterno'] = Apaterno.lstrip("apePaterno:" )
                #res['value']['apellidomaterno'] = Amaterno.lstrip("apeMaterno:" )
                #res['value']['nombres'] = Nombres.lstrip("Nombres:" )
                res['value']['name'] = Apaterno.replace("apePaterno:", "") +' ' +Amaterno.replace("apeMaterno:", "") + ' ' +Nombres.replace("Nombres:", "")
                res['value']['apellidopaterno'] = Apaterno.replace("apePaterno:", "")
                res['value']['apellidomaterno'] = Amaterno.replace("apeMaterno:", "")
                res['value']['nombres'] = Nombres.replace("Nombres:", "")

                #_logger.error("partner000 -: %r", res['value']['name'])

                #res['value']['name'] = name_empresa
                #JAVIER(0) SALAZAR(1) CARLOS(2)

                res['value']['ref'] = doc_number
                return res
            else:
                res['value']['street'] = False
                res['value']['name'] = False
                #res['value']['doc_number'] = False
                return res
        else:
            #res['value']['street'] = False
            #res['value']['name'] = False
            #res['value']['doc_number'] = False
            return res

    #OBTENIENDO DATOS DE http://aplicaciones.pronabec.gob.pe/b18/postula/registro? FOUND
    def onchange_doc_number_LARGO(self, cr, uid, ids, doc_type, doc_number, is_company, context=None):
        #response = urllib2.urlopen('http://www.sunat.gob.pe/w/wapS01Alias?ruc=20514540145')
        #html = response.read()
        #url='http://www.sunat.gob.pe/w/wapS01Alias?ruc=20553291501'
        #_logger.error("DOC_TUY: %r", doc_number)
        #str1 = raw_input("NGRESO CODIGO:")
        #_logger.error("DOC_TUY: %r", str1)
        res = {'value':{}}
        import HTMLParser
        hparser=HTMLParser.HTMLParser()
        if doc_number:
            if doc_type in ('6') and len(doc_number) == 11:
                url="http://www.sunat.gob.pe/w/wapS01Alias?ruc="+doc_number
                data = get_url(url)

                #Obteniendo la razon social
                res_empres = re.findall('''<small><b>N&#xFA;mero Ruc. </b> \d+ - .* <br/></small>''', data)
                for d in res_empres:
                    name_empresa =  (d[46:-14])
                    #_logger.error("wennnnnnnnn----: %r", name_empresa)                    
                    res['value']['name'] = hparser.unescape(hparser.unescape(name_empresa.decode('latin_1')))
                
                #Obteniendo la direccion de la empresa
                res_direcc = re.findall('''<small><b>Direcci&#xF3;n.</b><br/>.*</small><br/>''', data)
                for d in res_direcc:
                    direccion =  (d[34:-13])
                    res['value']['street'] = hparser.unescape(hparser.unescape(direccion.decode('latin_1')))                 
                
                #Obteniendo estado del contribuyente
                res_estado = re.findall('''<small><b>Estado.</b>.*</small><br/>''', data)
                for d in res_estado:
                    estado = (d[21:-13])
                    #_logger.error("ESTADO----: %r", estado)        
                    res['value']['sunat_state'] = estado

                #Obteniendo el telefono
                res_telefono = re.findall('''<small><b>Tel&#xE9;fono.*</b><br/>.*</small><br/>''', data)                
                for d in res_telefono:
                    telefono = (d[36:-13])   
                    #_logger.error("ESTADO----: %r", res_telefono)                       
                    res['value']['phone'] = telefono

                #Obteniendo condicion de contribuyente
                res_condicion = re.findall('''<small>Situaci&#xF3;n.<b> .*</b></small><br/>''', data)                
                for d in res_condicion:
                    condicion = (d[26:-17])   
                    #_logger.error("ESTADO----: %r", res_telefono)                       
                    res['value']['sunat_condicion'] = condicion

                #Obteniendo agente de retencion
                res_agente = re.findall('''<strong>\w{0,2}</strong> .*\r\n''', data)                
                for d in res_agente:
                    agente = (d[8:10])   
                    #_logger.error("AGENTE----: %r", (d[20:-2]))
                    if agente == 'SI':
                        res['value']['sunat_agente_retencion'] = True
                        res['value']['sunat_retencion_describe'] = (d[20:-2])

                res['value']['ref'] = doc_number
                res['value']['vat'] = 'PER' + doc_number #PARA VALIDAR RUC DEBE DE INICIAR CON PER
                res['value']['vat_subjected'] = True
                return res

            elif doc_type in ('1') and len(doc_number) == 8:                
                args = []
                reniec_obj = self.pool.get('res.partner.cookie.reniec')
                ids = reniec_obj.search(cr, uid, args, offset=0, limit=None, order=None, context=None, count=False)
                img=None
                micookie = None
                for value in reniec_obj.browse(cr, uid, ids):
                    img = value.name
                    micookie = "JSESSIONID="+value.cookie_reniec
                    #_logger.error("MI Cwwwwww: %r", micookie)

                dni= doc_number
                #---------------------

                url='http://aplicaciones.pronabec.gob.pe/b18/postula/registro?__RequestVerificationToken=8uZps7DLpSQzvgqYMQkUmnq7-Se6i1KsPwOfwj7MPPgPE-L59q1DjCGqHBxQM5SghWYkOOv6ROXCwtPy71tsY1q968F_yHuHp1KjugMLPm01&numero_documento='+dni
                data = get_url(url)
                #_logger.error("MI wwwww: %r", data)
                res_partner = re.findall('''<input class="form-control required" id="nombre_completo" name="nombre_completo" readOnly="true" type="text" value=".*" />''', data)
                for d in res_partner:
                    name_partner =  (d[116:-4])
                    n = name_partner.split()    
                    #_logger.error("wennnnnnnnn----: %r", name_empresa)                    
                    if len(n)==4:
                        #res['value']['name'] = hparser.unescape(hparser.unescape(name_empresa.decode('latin_1')))
                        #res['value']['name'] = n[2] + ' ' +  n[3]+ ' ' + n[0] + ' ' +  n[1]   
                        res['value']['name'] = (n[2] + ' ' +  n[3]+ ' ' + n[0] + ' ' +  n[1])
                        #_logger.error("partner -: %r", res['value']['name'])
                        res['value']['apellidopaterno'] = (n[2])
                        res['value']['apellidomaterno'] = (n[3])
                        res['value']['nombres'] = (n[0] + ' ' + n[1])
                    if len(n)==3:
                        res['value']['name'] = (n[1] + ' ' +  n[2]+ ' ' + n[0])
                        res['value']['apellidopaterno'] = (n[1])
                        res['value']['apellidomaterno'] = (n[2])
                        res['value']['nombres'] = (n[0])

                    if len(n)==6 and n[2]=='DE':
                        res['value']['name'] = (n[2] + ' ' +  n[3]+ ' ' + n[4]+ ' ' + n[5]+ ' ' + n[0]+ ' ' + n[1])
                        res['value']['apellidopaterno'] = (n[2]+ ' ' + n[3]+ ' ' + n[4])
                        res['value']['apellidomaterno'] = (n[5])
                        res['value']['nombres'] = (n[0]+ ' ' + n[1])

                    if len(n)==6 and n[2]!='DE':
                        res['value']['name'] = (n[2] + ' ' +  n[3]+ ' ' + n[4]+ ' ' + n[5]+ ' ' + n[0]+ ' ' + n[1])
                        res['value']['apellidopaterno'] = (n[2])
                        res['value']['apellidomaterno'] = (n[3]+ ' ' + n[4]+ ' ' + n[5])
                        res['value']['nombres'] = (n[0]+ ' ' + n[1])
                
                res['value']['ref'] = doc_number
                return res
            else:
                res['value']['street'] = False
                res['value']['name'] = False
                #res['value']['doc_number'] = False
                return res
        else:
            #res['value']['street'] = False
            #res['value']['name'] = False
            #res['value']['doc_number'] = False
            return res

    #Obteniendo datos: http://aplicaciones.pronabec.gob.pe/Sibecb182014c1/acceso/registro/95 
    def onchange_doc_number(self, cr, uid, ids, doc_type, doc_number, is_company, context=None):
        res = {'value':{}}
        import HTMLParser
        hparser=HTMLParser.HTMLParser()
        if doc_number:
            if doc_type in ('6') and len(doc_number) == 11:
                url="http://www.sunat.gob.pe/w/wapS01Alias?ruc="+doc_number
                data = get_url(url)

                #Obteniendo la razon social
                res_empres = re.findall('''<small><b>N&#xFA;mero Ruc. </b> \d+ - .* <br/></small>''', data)
                for d in res_empres:
                    name_empresa =  (d[46:-14])
                    #_logger.error("wennnnnnnnn----: %r", name_empresa)                    
                    res['value']['name'] = hparser.unescape(hparser.unescape(name_empresa.decode('latin_1')))
                
                #Obteniendo la direccion de la empresa
                res_direcc = re.findall('''<small><b>Direcci&#xF3;n.</b><br/>.*</small><br/>''', data)
                for d in res_direcc:
                    direccion =  (d[34:-13])
                    res['value']['street'] = hparser.unescape(hparser.unescape(direccion.decode('latin_1')))                 
                
                #Obteniendo estado del contribuyente
                res_estado = re.findall('''<small><b>Estado.</b>.*</small><br/>''', data)
                for d in res_estado:
                    estado = (d[21:-13])
                    #_logger.error("ESTADO----: %r", estado)        
                    res['value']['sunat_state'] = estado

                #Obteniendo el telefono
                res_telefono = re.findall('''<small><b>Tel&#xE9;fono.*</b><br/>.*</small><br/>''', data)                
                for d in res_telefono:
                    telefono = (d[36:-13])   
                    #_logger.error("ESTADO----: %r", res_telefono)                       
                    res['value']['phone'] = telefono

                #Obteniendo condicion de contribuyente
                res_condicion = re.findall('''<small>Situaci&#xF3;n.<b> .*</b></small><br/>''', data)                
                for d in res_condicion:
                    condicion = (d[26:-17])   
                    #_logger.error("ESTADO----: %r", res_telefono)                       
                    res['value']['sunat_condicion'] = condicion

                #Obteniendo agente de retencion
                res_agente = re.findall('''<strong>\w{0,2}</strong> .*\r\n''', data)                
                for d in res_agente:
                    agente = (d[8:10])   
                    #_logger.error("AGENTE----: %r", (d[20:-2]))
                    if agente == 'SI':
                        res['value']['sunat_agente_retencion'] = True
                        res['value']['sunat_retencion_describe'] = (d[20:-2])

                res['value']['ref'] = doc_number
                res['value']['vat'] = 'PER' + doc_number #PARA VALIDAR RUC DEBE DE INICIAR CON PER
                res['value']['vat_subjected'] = True
                return res

            elif doc_type in ('1') and len(doc_number) == 8:                
                args = []
                reniec_obj = self.pool.get('res.partner.cookie.reniec')
                ids = reniec_obj.search(cr, uid, args, offset=0, limit=None, order=None, context=None, count=False)
                img=None
                micookie = None
                for value in reniec_obj.browse(cr, uid, ids):
                    img = value.name
                    micookie = "JSESSIONID="+value.cookie_reniec
                    #_logger.error("MI Cwwwwww: %r", micookie)

                dni= doc_number
                #---------------------

                url = 'http://aplicaciones.pronabec.gob.pe/Sibecb182014c1/acceso/registro/95'
                micookie = "_ga=GA1.3.1811174037.1417526764; __RequestVerificationToken_L2IxOA2=In61X4dhJ72qShFgPaGR8y5_JC_dPmhG9OPuNaDiPgTnhpfy8Z85aU-ZJFrwBFp3ExHIbovxqtyJns8QSVah45oAs6Z_IRMyK3wW1d_9IBk1; ASP.NET_SessionId=vulaujw2squn1ixmw4kmhme0; __RequestVerificationToken_L0JDYW5hbA2=asP1a-jE5f18avVgPjPDzrTbStt38Q90MpIGPzpPE0C9CvtxVAkrUA9JQy6RHFdCcizV2EglwygMclTg_dSiVOeMxnhpi54dKPDZ5mOxrwE1; _gat=1"
                data="__EVENTTARGET=&__EVENTARGUMENT=&__VIEWSTATE=%2FwEPDwUKMTI2NjEyNTIxNQ9kFgJmD2QWAgIBD2QWAgIDD2QWBAIBDxYCHgRUZXh0BUBDT05DVVJTTyBQw5pCTElDTyBOQUNJT05BTCAtIFBSRVNJREVOVEUgREUgTEEgUkVQw5pCTElDQSAyMDE1ICAgZAIJD2QWCAIJD2QWAmYPZBYGAgEPEA8WBh4NRGF0YVRleHRGaWVsZAULRGVzY3JpcGNpb24eDkRhdGFWYWx1ZUZpZWxkBQZDb2RpZ28eC18hRGF0YUJvdW5kZ2QQFRoJW1JlZ2nDs25dCEFNQVpPTkFTBkFOQ0FTSAhBUFVSSU1BQwhBUkVRVUlQQQhBWUFDVUNITwlDQUpBTUFSQ0EGQ0FMTEFPBUNVU0NPDEhVQU5DQVZFTElDQQdIVUFOVUNPA0lDQQVKVU5JTgtMQSBMSUJFUlRBRApMQU1CQVlFUVVFBExJTUEGTE9SRVRPDU1BRFJFIERFIERJT1MITU9RVUVHVUEFUEFTQ08FUElVUkEEUFVOTwpTQU4gTUFSVElOBVRBQ05BBlRVTUJFUwdVQ0FZQUxJFRoAAjAxAjAyAjAzAjA0AjA1AjA2AjA3AjA4AjA5AjEwAjExAjEyAjEzAjE0AjE1AjE2AjE3AjE4AjE5AjIwAjIxAjIyAjIzAjI0AjI1FCsDGmdnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnFgFmZAIDDxBkZBYAZAIFDxBkZBYAZAILD2QWAmYPZBYGAgEPEA8WBh8BBQtEZXNjcmlwY2lvbh8CBQZDb2RpZ28fA2dkEBUaCVtSZWdpw7NuXQhBTUFaT05BUwZBTkNBU0gIQVBVUklNQUMIQVJFUVVJUEEIQVlBQ1VDSE8JQ0FKQU1BUkNBBkNBTExBTwVDVVNDTwxIVUFOQ0FWRUxJQ0EHSFVBTlVDTwNJQ0EFSlVOSU4LTEEgTElCRVJUQUQKTEFNQkFZRVFVRQRMSU1BBkxPUkVUTw1NQURSRSBERSBESU9TCE1PUVVFR1VBBVBBU0NPBVBJVVJBBFBVTk8KU0FOIE1BUlRJTgVUQUNOQQZUVU1CRVMHVUNBWUFMSRUaAAIwMQIwMgIwMwIwNAIwNQIwNgIwNwIwOAIwOQIxMAIxMQIxMgIxMwIxNAIxNQIxNgIxNwIxOAIxOQIyMAIyMQIyMgIyMwIyNAIyNRQrAxpnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZxYBZmQCAw8QZGQWAGQCBQ8QZGQWAGQCDQ8QDxYGHwEFC0Rlc2NyaXBjaW9uHwIFCklkX0dlbmVyYWwfA2dkEBUDDFtTZWxlY2Npb25lXQhGRU1FTklOTwlNQVNDVUxJTk8VAwAEMjEwMAQyMDk5FCsDA2dnZxYBZmQCFw8WAh4FVmFsdWUFAjk1ZGSTJ16BcCeNR5vgCWC%2F8YUq%2BEe9CbgLFZ6uc%2BvDTKfxZQ%3D%3D&__EVENTVALIDATION=%2FwEdAAPFI7l5fPJznJOi9Z3rNS80XqLFjcWng7eGRzT9F5QMFZh9xF4MuplgA3lroIIig6cRiJIvK1x4z1%2BGfH9hQDVUVyB4luMJZR%2BTnVyJ5E2Vgg%3D%3D&ctl00%24body%24UserName="+dni+"&ctl00%24body%24btn_siguiente=Continuar"
                req = urllib2.Request(url)
                req.add_header('User-Agent', 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:28.0) Gecko/20100101 Firefox/28.0')
                req.add_header('Cookie',micookie)
                page = urllib2.urlopen(req,data)
                response=page.read();page.close()
                partner_ap = re.findall('''<input name=".*" type="text" value=".*" maxlength="30" id="txtApePat" disabled="disabled" class="form-control" PlaceHolder="Paterno" style="width:100%;" />''', response)
                partner_am = re.findall('''<input name=".*" type="text" value=".*" maxlength="30" id="txtApeMat" disabled="disabled" class="form-control" PlaceHolder="Materno" style="width:100%;" />''', response)
                partner_nomb = re.findall('''<input name=".*" type="text" value=".*" maxlength="30" id="txtNombres" disabled="disabled" class="form-control" autocomplete="off" />''', response)
                Appaterno = None
                Apmaterno = None
                Nombre = None
                for d in partner_ap:
                    Appaterno=  (d[54:-117])
                    res['value']['apellidopaterno']  = Appaterno
                for d in partner_am:
                    Apmaterno =  (d[54:-117])
                    res['value']['apellidomaterno'] = Apmaterno
                for d in partner_nomb:
                    Nombre =  (d[55:-95])
                    res['value']['nombres'] = Nombre
                res['value']['name'] = Appaterno + ' ' +  Apmaterno + ' ' + Nombre
                res['value']['ref'] = doc_number
                return res
            else:
                res['value']['street'] = False
                res['value']['name'] = False
                #res['value']['doc_number'] = False
                return res
        else:
            #res['value']['street'] = False
            #res['value']['name'] = False
            #res['value']['doc_number'] = False
            return res          


    def onchange_cod(self, cr, uid, ids, doc_type, doc_number,codigo_reg_sunat_reniec, is_company, context=None):

        #Inicializamos un objeto que nos servira para poder abrir conexiones con una pagina 
        #y poder guardar las coiokies que nos mande esta pagina
        args = []
        reniec_obj = self.pool.get('res.partner.cookie.reniec')
        ids = reniec_obj.search(cr, uid, args, offset=0, limit=None, order=None, context=None, count=False)
        img=None
        micookie = None
        for value in reniec_obj.browse(cr, uid, ids):
            img = value.name
            micookie = "JSESSIONID="+value.cookie_reniec
            _logger.error("MI Cwwwwww: %r", micookie)



        dni= doc_number
        #dni='42995230'
        #img=codigo_reg_sunat_reniec
        #img='20M7'
        url="https://cel.reniec.gob.pe/valreg/valreg.do"
        
        #micookie="JSESSIONID=97657851ce58c6a187eb98c45b3af7caaa9519ed812.mALvn6iL-B9zpAzzmMTBpQ8Iq6iUaNaKahD3lN4PagSLa34Iah8K-xuL-AeSa69zaMSLa6aPa64Obh0QawSHc30Ka2bEaAjzawTwp65ynh4IqAjIokjx-ArJmwTKngaLc3iPaN8Sax8xf2bQmkLMnkqxn6jAmljGr5XDqQLvpAe_"

        #cookie_j = cookielib.CookieJar()  
        #cookie_h = urllib2.HTTPCookieProcessor(cookie_j)  
        #opener = urllib2.build_opener(cookie_h)  
        #opener.open("https://cel.reniec.gob.pe/valreg/codigo.do")  
        #opener.open("https://cel.reniec.gob.pe/valreg/valreg.do")
        #micookie=None
        #for num, cookie in enumerate(cookie_j):  
        #    micookie=cookie.name + "="+ cookie.value
        #_logger.error("MI COOKIE WEB: %r", micookie)

        data="accion=buscar&tecla_7=5&tecla_8=6&tecla_9=0&tecla_4=4&tecla_5=9&tecla_6=7&tecla_1=2&tecla_2=8&tecla_3=1&tecla_0=3&nuDni="+dni+"&imagen="+img+"&bot_consultar.x=113&bot_consultar.y=16"
        req = urllib2.Request(url)
        req.add_header('User-Agent', 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:28.0) Gecko/20100101 Firefox/28.0')
        req.add_header('Cookie',micookie)
        page = urllib2.urlopen(req,data)
        response=page.read();page.close()
        res_empres = re.findall('''<td height="63" class="style2" align="center">\D+<br>''', response)
        name_empresa = None
        for d in res_empres:
            name_empres =  (d[66:-4])
            n = name_empres.split()    
            name_empresa = ' '.join(name_empres.split())
            _logger.error("partner ------: %r", name_empresa)
	
        value = {}
        value['name'] = name_empresa
        return {'value': value}
    
    def onchange_doc_type(self, cr, uid, ids, doc_type, doc_number, is_company, context=None):
        value = {}
        value['doc_number'] = False
        value['name'] = False
        value['street'] = False
        value['apellidopaterno'] = False
        value['apellidomaterno'] = False
        value['nombres'] = False

        #if doc_type in ('6'):
        #    value['is_company'] = True
        #if doc_type in ('1'):
        #    value['is_company'] = True

        return {'value': value}

    def onchange_person(self, cr, uid, ids, name, nombres, apellidopaterno, apellidomaterno, context=None):
        #res = {'value':{}}
        #res['value']['name'] = (apellidopaterno and (apellidopaterno+' ') or '') + (apellidomaterno and (apellidomaterno+' ') or '') + (nombres and (nombres+' ') or '')
        #return res
        return True

    def address_get(self, cr, uid, ids, adr_pref=None, context=None):
        """ Find contacts/addresses of the right type(s) by doing a depth-first-search
        through descendants within company boundaries (stop at entities flagged ``is_company``)
        then continuing the search at the ancestors that are within the same company boundaries.
        Defaults to partners of type ``'default'`` when the exact type is not found, or to the
        provided partner itself if no type ``'default'`` is found either. """
        adr_pref = set(adr_pref or [])#set(['delivery', 'default', 'contact', 'invoice'])
        if 'default' not in adr_pref:
            adr_pref.add('default')
        result = {}
        visited = set()
        for partner in self.browse(cr, uid, filter(None, ids), context=context):
            current_partner = partner
            while current_partner:
                to_scan = [current_partner]
                # Scan descendants, DFS
                while to_scan:
                    record = to_scan.pop(0)                    
                    visited.add(record)
                    if record.type in adr_pref and not result.get(record.type):
                        result[record.type] = record.id
                    if len(result) == len(adr_pref):
                        return result
                    to_scan = [c for c in record.child_ids if c not in visited if not c.is_company] + to_scan

                # Continue scanning at ancestor if current_partner is not a commercial entity
                if current_partner.is_company or not current_partner.parent_id:
                    break
                current_partner = current_partner.parent_id

        # default to type 'default' or the partner itself
        default = result.get('default', partner.id)
        for adr_type in adr_pref:
            result[adr_type] = result.get(adr_type) or default
            #_logger.error("PARTNER QTY----: %r", result[adr_type])  
        return result




