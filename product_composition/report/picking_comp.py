# -*- encoding: utf-8 -*-
##############################################################################
#
# OpenERP, Open Source Management Solution
# Copyright (c) 2013 SysNeo Consulting SAC. (http://sysneoconsulting.com).
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
import time

from stock.report import picking

from report import report_sxw

from tools.translate import _

import logging
_logger = logging.getLogger(__name__)

class picking_composition(picking.picking):
    def __init__(self, cr, uid, name, context):
        super(picking_composition, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,        
            'get_qtytotal':self._get_qtytotal,
            'get_composition': self._get_product_composition,
        })

    def _get_product_composition(self,product_id, qty):
        comp_ids = self.pool.get('product.composition').search(self.cr, self.uid, [('product_id','=',product_id)])
        data=[]
        res = {}
        formato=''
        if comp_ids:
            for order in self.pool.get('product.composition').browse(self.cr, self.uid, comp_ids):
                for line in order.composition_line_ids:
                    formato += "- %s %s\r\n"%(int(line.quantity*qty),line.product_id.name)                    
        #_logger.error("ORDER ID 1: %r", formato)
        return formato

    #Para obtener el total de productos en la GR
    def _get_qtytotal(self,move_lines):
        total = 0.0
        uom = move_lines[0].product_uom.name
        for move in move_lines:
            total+=move.product_qty
        return {'quantity':total,'uom':uom}


report_sxw.report_sxw('report.stock.picking.composition',
                      'stock.picking.out',
                      'addons/product_composition/report/picking_comp.rml',
                      parser=picking_composition,header=False)


#PARA IMPRESIONES DE ALMACEN EN SALE.ORDER
from sale.report import sale_order
class sale_order_almacen(sale_order.order):
    item = 0
    def __init__(self, cr, uid, name, context):
        super(sale_order_almacen, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'get_qtytotal':self._get_qtytotal,
            'get_composition': self._get_product_composition,
        #    'get_item': self._get_item,
        })
    def _get_product_composition(self,product_id, qty):
        comp_ids = self.pool.get('product.composition').search(self.cr, self.uid, [('product_id','=',product_id)])
        data=[]
        res = {}
        formato=''
        if comp_ids:
            for order in self.pool.get('product.composition').browse(self.cr, self.uid, comp_ids):
                for line in order.composition_line_ids:
                    formato += "- %s %s\r\n"%(int(line.quantity*qty),line.product_id.name)                    
        #_logger.error("ORDER ID 1: %r", formato)
        return formato

    #Para obtener el total de productos en la GR
    def _get_qtytotal(self,move_lines):
        total = 0.0
        uom = move_lines[0].product_uom.name
        for move in move_lines:
            total+=move.product_uom_qty
        return {'quantity':total,'uom':uom}    

    #Para obtener el contador de item
    #def _get_item(self,move_lines):        
    #    self.item = self.item +1
    #    return {'items': self.item,}

report_sxw.report_sxw(
    'report.sale.order.print.almacen',
    'sale.order',
    'addons/product_composition/report/sale_order_print_almacen.rml',
    parser=sale_order_almacen,
    header=False
)

#PARA IMPRESIONES DE ALMACEN EN POS ORDER
from pos_extend.report import pos_order_venta_nuevo_formato

class pos_order_almacen(pos_order_venta_nuevo_formato.pos_order_venta_nuevo_formato):
    item = 0
    def __init__(self, cr, uid, name, context):
        super(pos_order_almacen, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'get_qtytotal':self._get_qtytotal,
            'get_composition': self._get_product_composition,
        #    'get_item': self._get_item,
        })
    def _get_product_composition(self,product_id, qty):
        comp_ids = self.pool.get('product.composition').search(self.cr, self.uid, [('product_id','=',product_id)])
        data=[]
        res = {}
        formato=''
        if comp_ids:
            for order in self.pool.get('product.composition').browse(self.cr, self.uid, comp_ids):
                for line in order.composition_line_ids:
                    formato += "- %s %s\r\n"%(int(line.quantity*qty),line.product_id.name)                    
        #_logger.error("ORDER ID 1: %r", formato)
        return formato

    #Para obtener el total de productos en la GR
    def _get_qtytotal(self,move_lines):
        total = 0.0
        uom = move_lines[0].product_id.uom_id.name
        for move in move_lines:
            total+=move.qty
        return {'quantity':total,'uom':uom}    

    #Para obtener el contador de item
    #def _get_item(self,move_lines):        
    #    self.item = self.item +1
    #    return {'items': self.item,}

report_sxw.report_sxw(
    'report.pos.order.print.almacen',
    'pos.order',
    'addons/product_composition/report/pos_order_print_almacen.rml',
    parser=pos_order_almacen,
    header=False
)




# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

