# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 S&C (<http://salazarcarlos.com>).
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

from openerp.osv import osv, fields
import openerp.addons.decimal_precision as dp
from openerp.tools.translate import _

import logging

_logger = logging.getLogger(__name__)

class stock_abast_consol_wizard(osv.osv_memory):
    _name = 'stock.abast.consol.wizard'
    def consolidar_abast(self, cr, uid, ids, context=None):
        if context is None:
            context = {}   
        abastec_id = None     

        datas = {'ids': context.get('active_ids', [])}    

        abast_obj =  self.pool.get('stock.abastecimiento')
        abast_line_obj =  self.pool.get('stock.abastecimiento.line')

        warehouse_id = None
        l = []
        for id in datas['ids']:
            abast = abast_obj.browse(cr, uid, [id], context)[0]
            if not abast.consolidar:
                raise osv.except_osv(_('Error!'),_('Esta escogiendo abastecimiento que tiene fecha de entrega, Abastecimiento N°: "%s"') %(abast.name))
            if  abast.state in ('consol'):
                raise osv.except_osv(_('Error!'),_('Esta escogiendo abastecimiento consolidados, Abastecimiento N°: "%s"') %(abast.name))
            if  abast.state in ('cancel'):
                raise osv.except_osv(_('Error!'),_('Esta escogiendo abastecimiento Anulados, Abastecimiento N°: "%s"') %(abast.name))
        #Permite hacer una comparacion de almacences
            l.append(abast.warehouse_id.id)
            for n in l:
                p = l.count(n)
                if p != len(l):
                    raise osv.except_osv(_('Error!'),_('Esta escogiendo abastecimiento de diferentes almacenes, Abastecimiento N°: "%s"') %(abast.name))
            warehouse_id = abast.warehouse_id.id    
            #_logger.error("INNNNNN_00000000000: %r", abast.warehouse_id.id)
            abast_obj.write(cr, uid, [abast.id], {'state': 'consol'},context)

        #Permite sumar las cantidades de productos iguales en busqueda
        cr.execute('SELECT SUM(product_qty), product_id, COUNT (product_id) FROM stock_abastecimiento_line WHERE abastec_id in %s GROUP BY product_id ORDER BY COUNT DESC', (tuple(datas['ids']),))
        lines = cr.fetchall()

        for line in lines:
            if not abastec_id:
                abastec_id = abast_obj.create(cr, uid, self._consolidar(cr, uid, warehouse_id, context), context) 
            move_id = abast_line_obj.create(cr, uid, self._consolidar_line(cr, uid, line, abastec_id, context))  

        return True

    def _consolidar(self, cr, uid, warehouse_id, context=None):
        return {
            'warehouse_id': warehouse_id,
            'date': time.strftime('%Y-%m-%d %H:%M:%S'),
            'abastec_line_ids': False,
            'user_id': uid ,
            'state': 'draft',
            'fecha_abast': time.strftime('%Y-%m-%d %H:%M:%S'),
            'origin': '',
            'consolidar': True,
        }  

    def _consolidar_line(self, cr, uid, line, abastec_id, context=None):
        return {
            'product_id': line[1] , 
            'product_qty': line[0], 
            'product_qty_abast': 0.0,
            'abastec_id': abastec_id,                            
        }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
