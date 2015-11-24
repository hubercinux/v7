# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 SC. (http://salazarcarlos.com).
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

from openerp.osv import fields, osv, orm
from openerp import tools
from datetime import  datetime
from dateutil.relativedelta import relativedelta

import logging
_logger = logging.getLogger(__name__)

class sale_update_wizard(osv.osv_memory):
    _name = "sale.update.wizard"

    def default_get(self, cr, uid, fields, context=None):
        if context is None: context = {}
        #res = super(purchase_update_date, self).default_get(cr, uid, fields, context=context)
        order_id = context.get('active_ids', [])
        active_model = context.get('active_model')
        date = self.pool.get('sale.order').read(cr, uid, order_id[0], ['date_order'], context=None)
        a = (datetime.strptime(date['date_order'] + ' 10:00:00', '%Y-%m-%d %H:%M:%S') + relativedelta(hours=5)).strftime("%Y-%m-%d %H:%M:%S")             
        return {'fecha_update': a}

    _columns = {
        'fecha_update': fields.datetime('Fecha'),
    }
    def update_date(self, cr, uid, ids, context=None):
        #uid=1
        fech_entrega = None
        user_email = None
        order_id = context.get('active_ids', [])
        
        wizard = self.browse(cr, uid, ids[0], context)
        
        for order in self.pool.get('sale.order').browse(cr, 1, order_id, context=context):
            fech_entrega = order.fecha_expected
            user_email = order.user_id.email
            self.pool.get('sale.order').write(cr, uid, order.id, {'fecha_expected': wizard.fecha_update})
            for picking in order.picking_ids:                
                self.pool.get('stock.picking').write(cr, 1, picking.id, {'min_date': wizard.fecha_update})
                for move in picking.move_lines:                    
                    self.pool.get('stock.move').write(cr, 1, move.id, {'date': wizard.fecha_update})
            abaste_ids = self.pool.get('stock.abastecimiento').search(cr, 1, [('origin', '=',order.name)])            
            if abaste_ids:
                for abas_id in abaste_ids:
                    self.pool.get('stock.abastecimiento').write(cr, uid, abas_id, {'fecha_abast': wizard.fecha_update})
            #_logger.error("ARROR: %r", abaste_ids)
        
        #Enviar por Correo
        email_template_obj = self.pool.get('email.template')
        #template_ids = email_template_obj.search(cr, uid, [('name', 'ilike','Sale Update fecha entrega')])
        template_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'sale_date_expected', 'email_template_sale_fecha_entrega')[1]  
        if template_id:
            values = email_template_obj.generate_email(cr, uid, template_id, order_id[0], context=context)            
            if values['email_from'] == False:
                values['email_from'] = self.pool.get('sale.shop').read(cr, uid, order.shop_id.id, ['shop_email'], context=None)['shop_email'] or user_email
            if values['reply_to'] == False:
                values['reply_to'] = self.pool.get('sale.shop').read(cr, uid, order.shop_id.id, ['shop_email'], context=None)['shop_email'] or user_email
            #values['body'] = values['body'].format(datetime.strptime(fech_entrega,'%Y-%m-%d %H:%M:%S').strftime('%d/%m/%Y %H:%M:%S'), datetime.strptime(wizard.fecha_update,'%Y-%m-%d %H:%M:%S').strftime('%d/%m/%Y %H:%M:%S'))
            if fech_entrega:
                values['body_html'] = values['body_html'].format(datetime.strptime(fech_entrega,'%Y-%m-%d %H:%M:%S').strftime('%d/%m/%Y %H:%M:%S'), datetime.strptime(wizard.fecha_update,'%Y-%m-%d %H:%M:%S').strftime('%d/%m/%Y %H:%M:%S')) 
            else:
                values['body_html'] = values['body_html'].format('No establecido',datetime.strptime(wizard.fecha_update,'%Y-%m-%d %H:%M:%S').strftime('%d/%m/%Y %H:%M:%S')) 
            #values['res_id'] = False
            mail_mail_obj = self.pool.get('mail.mail')
            msg_id = mail_mail_obj.create(cr, uid, values, context=context)
            if msg_id:
                mail_mail_obj.send(cr, uid, [msg_id], context=context) 
        
        return True
    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

