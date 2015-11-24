# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import time
from openerp.report import report_sxw
from openerp import pooler
import logging
_logger = logging.getLogger(__name__)

def titlize(journal_name):
    words = journal_name.split()
    while words.pop() != 'journal':
        continue
    return ' '.join(words)

class pos_report_fact_venta(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        super(pos_report_fact_venta, self).__init__(cr, uid, name, context=context)

        user = pooler.get_pool(cr.dbname).get('res.users').browse(cr, uid, uid, context=context)
        partner = user.company_id.partner_id
        #TICKET BOLETA
        self.total_ticket_boleta_tarjeta= 0.0
        self.total_ticket_boleta_efectivo= 0.0
        self.total_ticket_boleta_deposito= 0.0
        #TICKET FACTURA
        self.total_tarjeta= 0.0
        self.total_efectivo= 0.0
        self.total_deposito= 0.0
        #formato grande
        self.total_tarjeta_form_grande= 0.0
        self.total_efectivo_form_grande= 0.0

        self.localcontext.update({
            'time': time,
            'address': partner or False,
            'titlize': titlize,

            #TICKET BOLETA
            'ticket_boleta_pago_tarjeta': self._ticket_boleta_pago_tarjeta,
            'gettotal_boleta_tarjeta': self._get_total_boleta_tarjeta,
            'ticket_boleta_pago_efectivo': self._ticket_boleta_pago_efectivo,            
            'gettotal_boleta_efectivo': self._get_total_boleta_efectivo, 
            'ticket_boleta_pago_deposito': self._ticket_boleta_pago_deposito,            
            'gettotal_boleta_deposito': self._get_total_boleta_deposito,      
            #TICKET FACTURA
            'factura_pago_tarjeta': self._ticket_factura_pago_tarjeta,
            'gettotal_tarjeta': self._get_total_tarjeta,
            'factura_pago_efectivo': self._ticket_factura_pago_efectivo,
            'gettotal_efectivo': self._get_total_efectivo,
            'factura_pago_deposito': self._ticket_factura_pago_deposito,
            'gettotal_deposito': self._get_total_deposito,
            #FACTURA/BOLETA FORMATO GRANDE
            'factura_pago_form_grande': self._factura_pago_form_grande,
            'gettotal_form_grande': self._get_total_form_grande,
        })
    #TICKET BOLETA
    def _ticket_boleta_pago_tarjeta(self, session_id):
        pos_order_obj = self.pool.get('pos.order')
        data=[]
        res = {}
        pos_order_id = pos_order_obj.search(self.cr,self.uid,['|',('state','=','done'),('state','=','paid'),('pos_reference','ilike','TB 0%'),('session_id','=',session_id)])
        #_logger.error("ORDER sesion: %r", pos_order_id)   
        for id in pos_order_id:
            for pos_line in pos_order_obj.browse(self.cr, self.uid, [id]): 
                for pago in pos_line.statement_ids:
                    if pago.journal_id.forma_pago =='tarjeta' or pago.journal_id.forma_pago =='deposito' :                        
                        if pago.journal_id.name.find(' LA VICTORIA') != -1:
                            res= {
                            'ref':pos_line.pos_reference,
                            'name':pos_line.name,                       
                            'name_tarjeta': pago.journal_id.name[:-12],
                            'ref_voucher': pago.ref_card,
                            'monto': pago.amount,
                            }
                            self.total_ticket_boleta_tarjeta += pago.amount
                            data.append(res) 
                        if pago.journal_id.name.find(' SAN MIGUEL') != -1:
                            res= {
                            'ref':pos_line.pos_reference,
                            'name':pos_line.name,                       
                            'name_tarjeta': pago.journal_id.name[:-11],
                            'ref_voucher': pago.ref_card,
                            'monto': pago.amount,
                            }
                            self.total_ticket_boleta_tarjeta += pago.amount
                            data.append(res)   
                        if pago.journal_id.name.find(' SURCO') != -1:
                            res= {
                            'ref':pos_line.pos_reference,
                            'name':pos_line.name,                       
                            'name_tarjeta': pago.journal_id.name[:-6],
                            'ref_voucher': pago.ref_card,
                            'monto': pago.amount,
                            }
                            self.total_ticket_boleta_tarjeta += pago.amount
                            data.append(res)
                        if pago.journal_id.name.find(' PLAZA NORTE') != -1:
                            res= {
                            'ref':pos_line.pos_reference,
                            'name':pos_line.name,                       
                            'name_tarjeta': pago.journal_id.name[:-12],
                            'ref_voucher': pago.ref_card,
                            'monto': pago.amount,
                            }
                            self.total_ticket_boleta_tarjeta += pago.amount
                            data.append(res)
        return data 
    def _get_total_boleta_tarjeta(self):
        return self.total_ticket_boleta_tarjeta
    def _ticket_boleta_pago_efectivo(self, session_id):
        pos_order_obj = self.pool.get('pos.order')
        data=[]
        res = {}
        pos_order_id = pos_order_obj.search(self.cr,self.uid,['|',('state','=','done'),('state','=','paid'),('pos_reference','ilike','TB 0%'),('session_id','=',session_id)])
        #  
        for id in pos_order_id:
            for pos_line in pos_order_obj.browse(self.cr, self.uid, [id]): 
                for pago in pos_line.statement_ids:
                    if pago.journal_id.forma_pago =='efectivo': 
                        #_logger.error("ORDER sesion: %r", pago.journal_id.name.find(' LA VICTORIA')) 
                        if pago.journal_id.name.find(' LA VICTORIA') != -1:
                            res= {
                            'ref':pos_line.pos_reference,
                            'name':pos_line.name,                       
                            'name_tarjeta': pago.journal_id.name[:-12],
                            'ref_voucher': pago.ref_card,
                            'monto': pago.amount,
                            }
                            self.total_ticket_boleta_efectivo += pago.amount
                            data.append(res)
                        if pago.journal_id.name.find(' SAN MIGUEL') != -1:
                            res= {
                            'ref':pos_line.pos_reference,
                            'name':pos_line.name,                       
                            'name_tarjeta': pago.journal_id.name[:-11],
                            'ref_voucher': pago.ref_card,
                            'monto': pago.amount,
                            }
                            self.total_ticket_boleta_efectivo += pago.amount
                            data.append(res)
                        if pago.journal_id.name.find(' SURCO') != -1:
                            res= {
                            'ref':pos_line.pos_reference,
                            'name':pos_line.name,                       
                            'name_tarjeta': pago.journal_id.name[:-6],
                            'ref_voucher': pago.ref_card,
                            'monto': pago.amount,
                            }
                            self.total_ticket_boleta_efectivo += pago.amount
                            data.append(res)
                        if pago.journal_id.name.find(' PLAZA NORTE') != -1:
                            res= {
                            'ref':pos_line.pos_reference,
                            'name':pos_line.name,                       
                            'name_tarjeta': pago.journal_id.name[:-12],
                            'ref_voucher': pago.ref_card,
                            'monto': pago.amount,
                            }
                            self.total_ticket_boleta_efectivo += pago.amount
                            data.append(res)

                if not pos_line.statement_ids:                
                    res= {
                    'ref':pos_line.pos_reference,
                    'name':pos_line.name,                       
                    'name_tarjeta': 'OBSEQUIO/DONACION',
                    'ref_voucher': False,
                    'monto': 0.0,
                    }
                    _logger.error("ORDER: %r", res) 
                    self.total_ticket_boleta_efectivo += 0.0
                    data.append(res)
                                                               
        return data               
    def _get_total_boleta_efectivo(self):
        return self.total_ticket_boleta_efectivo  
    def _ticket_boleta_pago_deposito(self, session_id):
        pos_order_obj = self.pool.get('pos.order')
        data=[]
        res = {}
        pos_order_id = pos_order_obj.search(self.cr,self.uid,['|',('state','=','done'),('state','=','paid'),('pos_reference','ilike','TB 0%'),('session_id','=',session_id)])
        #  
        for id in pos_order_id:
            for pos_line in pos_order_obj.browse(self.cr, self.uid, [id]): 
                for pago in pos_line.statement_ids:
                    if pago.journal_id.forma_pago =='deposito': 
                        #_logger.error("ORDER sesion: %r", pago.journal_id.name.find(' LA VICTORIA')) 
                        if pago.journal_id.name.find(' LA VICTORIA') != -1:
                            res= {
                            'ref':pos_line.pos_reference,
                            'name':pos_line.name,                       
                            'name_tarjeta': pago.journal_id.name[:-12],
                            'ref_voucher': pago.ref_card,
                            'monto': pago.amount,
                            }
                            self.total_ticket_boleta_deposito += pago.amount
                            data.append(res)
                        if pago.journal_id.name.find(' SAN MIGUEL') != -1:
                            res= {
                            'ref':pos_line.pos_reference,
                            'name':pos_line.name,                       
                            'name_tarjeta': pago.journal_id.name[:-11],
                            'ref_voucher': pago.ref_card,
                            'monto': pago.amount,
                            }
                            self.total_ticket_boleta_deposito += pago.amount
                            data.append(res)
                        if pago.journal_id.name.find(' SURCO') != -1:
                            res= {
                            'ref':pos_line.pos_reference,
                            'name':pos_line.name,                       
                            'name_tarjeta': pago.journal_id.name[:-6],
                            'ref_voucher': pago.ref_card,
                            'monto': pago.amount,
                            }
                            self.total_ticket_boleta_deposito += pago.amount
                            data.append(res)
                        if pago.journal_id.name.find(' PLAZA NORTE') != -1:
                            res= {
                            'ref':pos_line.pos_reference,
                            'name':pos_line.name,                       
                            'name_tarjeta': pago.journal_id.name[:-12],
                            'ref_voucher': pago.ref_card,
                            'monto': pago.amount,
                            }
                            self.total_ticket_boleta_deposito += pago.amount
                            data.append(res)
                                                               
        return data               
    def _get_total_boleta_deposito(self):
        return self.total_ticket_boleta_deposito   
       
    #TICKET FACTURA   
    def _ticket_factura_pago_tarjeta(self, session_id):
        pos_order_obj = self.pool.get('pos.order')
        data=[]
        res = {}
        pos_order_id = pos_order_obj.search(self.cr,self.uid,['|',('state','=','done'),('state','=','paid'),('pos_reference','ilike','TF 0%'),('session_id','=',session_id)])
        #_logger.error("ORDER sesion: %r", pos_order_id)   
        for id in pos_order_id:
            for pos_line in pos_order_obj.browse(self.cr, self.uid, [id]): 
                for pago in pos_line.statement_ids:
                    if pago.journal_id.forma_pago =='tarjeta':                        
                        if pago.journal_id.name.find(' LA VICTORIA') != -1:
                            res= {
                            'ref':pos_line.pos_reference,
                            'name':pos_line.name,                       
                            'name_tarjeta': pago.journal_id.name[:-12],
                            'ref_voucher': pago.ref_card,
                            'monto': pago.amount,
                            }
                            self.total_tarjeta += pago.amount
                            data.append(res) 
                        if pago.journal_id.name.find(' SAN MIGUEL') != -1:
                            res= {
                            'ref':pos_line.pos_reference,
                            'name':pos_line.name,                       
                            'name_tarjeta': pago.journal_id.name[:-11],
                            'ref_voucher': pago.ref_card,
                            'monto': pago.amount,
                            }
                            self.total_tarjeta += pago.amount
                            data.append(res)   
                        if pago.journal_id.name.find(' SURCO') != -1:
                            res= {
                            'ref':pos_line.pos_reference,
                            'name':pos_line.name,                       
                            'name_tarjeta': pago.journal_id.name[:-6],
                            'ref_voucher': pago.ref_card,
                            'monto': pago.amount,
                            }
                            self.total_tarjeta += pago.amount
                            data.append(res)
                        if pago.journal_id.name.find(' PLAZA NORTE') != -1:
                            res= {
                            'ref':pos_line.pos_reference,
                            'name':pos_line.name,                       
                            'name_tarjeta': pago.journal_id.name[:-12],
                            'ref_voucher': pago.ref_card,
                            'monto': pago.amount,
                            }
                            self.total_tarjeta += pago.amount
                            data.append(res) 
        return data 
    def _get_total_tarjeta(self):
        return self.total_tarjeta
    def _ticket_factura_pago_efectivo(self, session_id):
        pos_order_obj = self.pool.get('pos.order')
        data=[]
        res = {}
        pos_order_id = pos_order_obj.search(self.cr,self.uid,['|',('state','=','done'),('state','=','paid'),('pos_reference','ilike','TF 0%'),('session_id','=',session_id)])
        #  
        for id in pos_order_id:
            for pos_line in pos_order_obj.browse(self.cr, self.uid, [id]): 
                for pago in pos_line.statement_ids:
                    if pago.journal_id.forma_pago =='efectivo': 
                        #_logger.error("ORDER sesion: %r", pago.journal_id.name.find(' LA VICTORIA')) 
                        if pago.journal_id.name.find(' LA VICTORIA') != -1:
                            res= {
                            'ref':pos_line.pos_reference,
                            'name':pos_line.name,                       
                            'name_tarjeta': pago.journal_id.name[:-12],
                            'ref_voucher': pago.ref_card,
                            'monto': pago.amount,
                            }
                            self.total_efectivo += pago.amount
                            data.append(res)
                        if pago.journal_id.name.find(' SAN MIGUEL') != -1:
                            res= {
                            'ref':pos_line.pos_reference,
                            'name':pos_line.name,                       
                            'name_tarjeta': pago.journal_id.name[:-11],
                            'ref_voucher': pago.ref_card,
                            'monto': pago.amount,
                            }
                            self.total_efectivo += pago.amount
                            data.append(res)
                        if pago.journal_id.name.find(' SURCO') != -1:
                            res= {
                            'ref':pos_line.pos_reference,
                            'name':pos_line.name,                       
                            'name_tarjeta': pago.journal_id.name[:-6],
                            'ref_voucher': pago.ref_card,
                            'monto': pago.amount,
                            }
                            self.total_efectivo += pago.amount
                            data.append(res) 
                        if pago.journal_id.name.find(' PLAZA NORTE') != -1:
                            res= {
                            'ref':pos_line.pos_reference,
                            'name':pos_line.name,                       
                            'name_tarjeta': pago.journal_id.name[:-12],
                            'ref_voucher': pago.ref_card,
                            'monto': pago.amount,
                            }
                            self.total_efectivo += pago.amount
                            data.append(res)

            if not pos_line.statement_ids:                
                res= {
                'ref':pos_line.pos_reference,
                'name':pos_line.name,                       
                'name_tarjeta': 'OBSEQUIO/DONACION',
                'ref_voucher': False,
                'monto': 0.0,
                }
                #_logger.error("ORDER: %r", res) 
                self.total_efectivo += 0.0
                data.append(res) 
                                                               
        return data               
    def _get_total_efectivo(self):
        return self.total_efectivo
    def _ticket_factura_pago_deposito(self, session_id):
        pos_order_obj = self.pool.get('pos.order')
        data=[]
        res = {}
        pos_order_id = pos_order_obj.search(self.cr,self.uid,['|',('state','=','done'),('state','=','paid'),('pos_reference','ilike','TF 0%'),('session_id','=',session_id)])
        #  
        for id in pos_order_id:
            for pos_line in pos_order_obj.browse(self.cr, self.uid, [id]): 
                for pago in pos_line.statement_ids:
                    if pago.journal_id.forma_pago =='deposito': 
                        #_logger.error("ORDER sesion: %r", pago.journal_id.name.find(' LA VICTORIA')) 
                        if pago.journal_id.name.find(' LA VICTORIA') != -1:
                            res= {
                            'ref':pos_line.pos_reference,
                            'name':pos_line.name,                       
                            'name_tarjeta': pago.journal_id.name[:-12],
                            'ref_voucher': pago.ref_card,
                            'monto': pago.amount,
                            }
                            self.total_deposito += pago.amount
                            data.append(res)
                        if pago.journal_id.name.find(' SAN MIGUEL') != -1:
                            res= {
                            'ref':pos_line.pos_reference,
                            'name':pos_line.name,                       
                            'name_tarjeta': pago.journal_id.name[:-11],
                            'ref_voucher': pago.ref_card,
                            'monto': pago.amount,
                            }
                            self.total_deposito += pago.amount
                            data.append(res)
                        if pago.journal_id.name.find(' SURCO') != -1:
                            res= {
                            'ref':pos_line.pos_reference,
                            'name':pos_line.name,                       
                            'name_tarjeta': pago.journal_id.name[:-6],
                            'ref_voucher': pago.ref_card,
                            'monto': pago.amount,
                            }
                            self.total_deposito += pago.amount
                            data.append(res) 
                        if pago.journal_id.name.find(' PLAZA NORTE') != -1:
                            res= {
                            'ref':pos_line.pos_reference,
                            'name':pos_line.name,                       
                            'name_tarjeta': pago.journal_id.name[:-12],
                            'ref_voucher': pago.ref_card,
                            'monto': pago.amount,
                            }
                            self.total_deposito += pago.amount
                            data.append(res)                                                              
        return data               
    def _get_total_deposito(self):
        return self.total_deposito

    #PARA FORMATOS GRANDE
    def _factura_pago_form_grande(self, session_id, tienda_id):
        #session_obj = self.pool.get('pos.sesion')
        statement_obj = self.pool.get('account.bank.statement')
        statement_line_obj = self.pool.get('account.bank.statement.line')
        voucher_obj= self.pool.get('account.voucher')
        #voucher_line_obj= self.pool.get('account.voucher.line')
        invoice_obj= self.pool.get('account.invoice')
        data=[]
        res = {}
        statement_ids = statement_obj.search(self.cr, self.uid,[('pos_session_id','=',session_id)])       
        statement_line_ids = statement_line_obj.search(self.cr, self.uid,[('statement_id','in',statement_ids),('voucher_id','!=',False)])           
        for id in statement_line_ids:
            for statement_line in statement_line_obj.browse(self.cr, self.uid, [id]):
                if statement_line.voucher_id:                    
                    for voucher in voucher_obj.browse(self.cr, self.uid, [statement_line.voucher_id.id]):
                        for line in voucher.line_ids:
                            if line.amount>0:
                                invoice_ids = invoice_obj.search(self.cr,self.uid,[('internal_number','ilike',line.name)])
                                for id in invoice_ids:
                                    for invoice in invoice_obj.browse(self.cr, self.uid, [id]):
                                        if line.type=='cr':
                                            res= {
                                            'numero': invoice.internal_number,                                    
                                            'onden_venta':invoice.origin,
                                            'cliente': invoice.partner_id.name,
                                            'fecha_factura': invoice.date_invoice,
                                            'forma_pago': voucher.journal_id.name,                                
                                            'monto': line.amount,
                                            }
                                            self.total_tarjeta_form_grande += line.amount
                                            data.append(res)
                                        if line.type=='dr':
                                            res= {
                                            'numero': invoice.internal_number,                                    
                                            'onden_venta':invoice.origin,
                                            'cliente': invoice.partner_id.name,
                                            'fecha_factura': invoice.date_invoice,
                                            'forma_pago': voucher.journal_id.name,                                
                                            'monto': - line.amount,
                                            }
                                            self.total_tarjeta_form_grande = self.total_tarjeta_form_grande - line.amount
                                            data.append(res)

        #_logger.error("ORDER sesion: %r", data)           
        return data
    def _get_total_form_grande(self):
        return self.total_tarjeta_form_grande

report_sxw.report_sxw('report.pos.session.venta.factura.print', 'pos.session', 'addons/pos_extend/report/pos_report_fact_venta.rml', parser=pos_report_fact_venta, header=False)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:


