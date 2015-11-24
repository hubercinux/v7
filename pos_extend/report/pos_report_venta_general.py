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
from dateutil.relativedelta import relativedelta
from datetime import  datetime
from openerp.report import report_sxw
from openerp import pooler
import logging
_logger = logging.getLogger(__name__)

def titlize(journal_name):
    words = journal_name.split()
    while words.pop() != 'journal':
        continue
    return ' '.join(words)

class pos_venta_general(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        super(pos_venta_general, self).__init__(cr, uid, name, context=context)

        user = pooler.get_pool(cr.dbname).get('res.users').browse(cr, uid, uid, context=context)
        partner = user.company_id.partner_id
        self.monto_total= 0.0
        self.monto_total2= 0.0
        self.localcontext.update({
            'time': time,
            'titlize': titlize,
            'ticket_boleta_factura': self._ticket_boleta_factura,
            'getmonto_total': self._get_monto_total,
            'boleta_factura': self._boleta_factura,
            'getmonto_total2': self._get_monto_total2,
        })
    def _ticket_boleta_factura(self, session_id):
        pos_order_obj = self.pool.get('pos.order')
        data=[]
        res = {}
        pos_order_id = pos_order_obj.search(self.cr,self.uid,['|','|',('state','=','done'),('state','=','paid'),('state','=','cancel'),'|',('pos_reference','ilike','TF 0%'),('pos_reference','ilike','TB 0%'),('session_id','=',session_id)], order='name')
        #_logger.error("ORDER sesion: %r", pos_order_id)   
        for id in pos_order_id:
            for pos_order in pos_order_obj.browse(self.cr, self.uid, [id]):
                res= {
                    'name':pos_order.name, 
                    'ref':pos_order.pos_reference,                                    
                    'partner': pos_order.partner_id.name,                    
                    'fecha_pedido': (datetime.strptime(pos_order.date_order,'%Y-%m-%d %H:%M:%S') - relativedelta(hours=5)).strftime("%Y-%m-%d %H:%M:%S"),
                    'total': pos_order.amount_total,
                    'estado': pos_order.state,
                    }
                self.monto_total += pos_order.amount_total
                data.append(res)                 
        return data 
    def _get_monto_total(self, ):
        return self.monto_total

    #FORMATO GRANDE
    def _boleta_factura(self, tienda_id, fecha):
        data=[]
        res = {}
        invoice_obj = self.pool.get('account.invoice')
        tienda_ids= self.pool.get('sale.shop').search(self.cr,self.uid,['|',('id','=',tienda_id),('shop_parent_id','=',tienda_id)], )        
        invoice_ids=invoice_obj.search(self.cr,self.uid,[('shop_id','in',tienda_ids),('date_invoice','=',fecha[0:10])])
        
        for id in invoice_ids:
            for invoice in  invoice_obj.browse(self.cr, self.uid, [id]):
                if invoice.type=='out_invoice':
                    res= {
                        'ref':invoice.origin, 
                        'numero':invoice.internal_number,                                    
                        'partner': invoice.partner_id.name,
                        'fecha': invoice.date_invoice,                    
                        'estado': invoice.state,
                        'importe': invoice.amount_total,
                        }
                    self.monto_total2 += invoice.amount_total
                    data.append(res)
                if invoice.type=='out_refund':
                    res= {
                        'ref':invoice.origin, 
                        'numero':invoice.internal_number,                                    
                        'partner': invoice.partner_id.name,
                        'fecha': invoice.date_invoice,                    
                        'estado': invoice.state,
                        'importe':  - invoice.amount_total,
                        }
                    self.monto_total2 = self.monto_total2 - invoice.amount_total
                    data.append(res)                     
        #_logger.error("ORDER sesion: %r", data)   
        return data
    def _get_monto_total2(self):
        return self.monto_total2
report_sxw.report_sxw('report.pos.session.venta.general.print', 'pos.session', 'addons/pos_extend/report/pos_report_venta_general.rml', parser=pos_venta_general, header=False)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

