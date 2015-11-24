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


from openerp.osv import fields, osv
import time,dateutil, dateutil.tz
from openerp.tools.translate import _
from dateutil.relativedelta import relativedelta

from datetime import date, datetime

import logging
_logger = logging.getLogger(__name__)


class product_composition_move_wizard(osv.TransientModel):
    _name = 'product.composition.move.wizard'
    _rec_name = 'composition_id'
    _columns = {
        'composition_id': fields.many2one( 'product.composition.wizard', 'Product Composition', ondelete='cascade'),
        'product_id': fields.many2one('product.product', 'Producto'),
        'quantity': fields.float('Cantidad'),       
    }

class product_composition_wizard(osv.TransientModel):
    _name = 'product.composition.wizard'
    _columns = {
        'product_id': fields.many2one('product.product', 'Producto', readonly=True),
        'quantity': fields.float('Cantidad', readonly=True),
        'composition_line_ids': fields.one2many('product.composition.move.wizard', 'composition_id', 'Products Composition', readonly=True ),
    }

    def default_get(self, cr, uid, fields, context=None):
        if context is None: context = {}
        
        order_ids = context.get('active_ids', [])
        active_model = context.get('active_model')

        res = {}
        composition_obj = self.pool.get('product.composition')

        if active_model == 'stock.move':            
            for value in self.pool.get('stock.move').browse(cr, uid, order_ids, context=context):            
                res['product_id'] = value.product_id.id
                comp_ids = composition_obj.search(cr, uid, [('product_id','=',value.product_id.id)])
                if not comp_ids:
                    raise osv.except_osv(_('Warning!'),_('No es un producto compuesto'))
                for order in composition_obj.browse(cr, uid, comp_ids, context):
                    res['quantity'] = order.quantity
                    moves = [self._partial_line_composition(cr, uid, line) for line in order.composition_line_ids ]
                res.update(composition_line_ids=moves)
        #_logger.error("INNNNNN_00000000000: %r", active_model)

        if active_model == 'product.product':
            res['product_id'] = order_ids
            comp_ids = composition_obj.search(cr, uid, [('product_id','=',order_ids)])
            if not comp_ids:
                raise osv.except_osv(_('Warning!'),_('No es un producto compuesto'))
            for order in composition_obj.browse(cr, uid, comp_ids, context):
                res['quantity'] = order.quantity
                moves = [self._partial_line_composition(cr, uid, line) for line in order.composition_line_ids ]
            res.update(composition_line_ids=moves)            
        return res

    def _partial_line_composition(self, cr, uid, line):
        partial_move = {
            'composition_id' : line.composition_id.id,
            'product_id' : line.product_id.id,
            'quantity': line.quantity,
        }
        return partial_move