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

class pos_order_update_wizard(osv.osv_memory):
    _name = "pos.order.update.wizard"

    def default_get(self, cr, uid, fields, context=None):
        if context is None: context = {}
        #res = super(purchase_update_date, self).default_get(cr, uid, fields, context=context)
        order_id = context.get('active_ids', [])
        active_model = context.get('active_model')
        date = self.pool.get('pos.order').read(cr, uid, order_id[0], ['date_order'], context=None)
        #a = (datetime.strptime(date['date_order'] + ' 10:00:00', '%Y-%m-%d %H:%M:%S') + relativedelta(hours=5)).strftime("%Y-%m-%d %H:%M:%S")             
        return {'fecha_update': date['date_order']}

    _columns = {
        'fecha_update': fields.datetime('Fecha'),
    }
    def update_date(self, cr, uid, ids, context=None):
        #uid=1
        fech_entrega = None
        user_email = None
        #order_id = context.get('active_ids', [])
        active_id = context and context.get('active_id', False)
        wizard = self.browse(cr, uid, ids[0], context)  
        order_obj = self.pool.get('pos.order')

        for pos_order in order_obj.browse(cr, uid, [active_id], context=context):
            _logger.error("ERROR: %r", pos_order.name)
            fech_entrega = pos_order.fecha_expected
            user_email = pos_order.user_id.email
            order_obj.write(cr, uid, [pos_order.id], {'fecha_expected': wizard.fecha_update})                        
            self.pool.get('stock.picking').write(cr, 1, pos_order.picking_id.id, {'min_date': wizard.fecha_update})
            for move in self.pool.get('stock.move').search(cr, 1, [('picking_id', '=',pos_order.picking_id.id)]):                    
                    self.pool.get('stock.move').write(cr, 1, move, {'date': wizard.fecha_update})
            abaste_ids = self.pool.get('stock.abastecimiento').search(cr, 1, [('origin', '=',pos_order.name)])            
            if abaste_ids:
                for abas_id in abaste_ids:
                    self.pool.get('stock.abastecimiento').write(cr, uid, abas_id, {'fecha_abast': wizard.fecha_update})
            
        
        #Enviar por Correo
        email_template_obj = self.pool.get('email.template')
        #template_ids = email_template_obj.search(cr, uid, [('name', 'ilike','Sale Update fecha entrega')])
        template_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'pos_extend', 'email_template_pos_fecha_entrega')[1]  
        if template_id:
            values = email_template_obj.generate_email(cr, uid, template_id, active_id, context=context)            
            if values['email_from'] == False:
                values['email_from'] = self.pool.get('sale.shop').read(cr, uid, pos_order.shop_id.id, ['shop_email'], context=None)['shop_email'] or user_email
            if values['reply_to'] == False:
                values['reply_to'] = self.pool.get('sale.shop').read(cr, uid, pos_order.shop_id.id, ['shop_email'], context=None)['shop_email'] or user_email
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

