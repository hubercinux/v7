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

class purchase_update_date(osv.osv_memory):
    _name = "purchase.update.date"

    def default_get(self, cr, uid, fields, context=None):
        if context is None: context = {}
        #res = super(purchase_update_date, self).default_get(cr, uid, fields, context=context)
        order_id = context.get('active_ids', [])
        active_model = context.get('active_model')
        date = self.pool.get('purchase.order').read(cr, uid, order_id[0], ['date_order'], context=None)
        a = (datetime.strptime(date['date_order'] + ' 10:00:00', '%Y-%m-%d %H:%M:%S') + relativedelta(hours=5)).strftime("%Y-%m-%d %H:%M:%S")
        #_logger.error("updateee22: %r", a)               
        return {'fecha_update': a}

    _columns = {
        'fecha_update': fields.datetime('Fecha'),
    }
    def update_date(self, cr, uid, ids, context=None):
        order_id = context.get('active_ids', [])
        wizard = self.browse(cr, uid, ids[0], context)
        for order in self.pool.get('purchase.order').browse(cr, uid, order_id, context=context):
            self.pool.get('purchase.order').write(cr, uid, order.id, {'date_order': wizard.fecha_update})
            for picking in order.picking_ids:
                self.pool.get('stock.picking').write(cr, uid, picking.id, {'date_done': wizard.fecha_update})
                for move in picking.move_lines:
                    self.pool.get('stock.move').write(cr, uid, move.id, {'date': wizard.fecha_update})
        return True
    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
