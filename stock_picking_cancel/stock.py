# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2010 Vauxoo - http://www.vauxoo.com/
#    All Rights Reserved.
#    info Vauxoo (info@vauxoo.com)
############################################################################
#    Coded by: Luis Torres (luis_t@vauxoo.com)
############################################################################
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
from openerp.osv import osv, fields
import openerp.netsvc as netsvc
from openerp.tools.translate import _


class stock_picking(osv.Model):
    _inherit = 'stock.picking'

    def action_cancel(self, cr, uid, ids, context=None):
        """ Changes picking state to cancel.
        @return: True
        """
        move_obj = self.pool.get('stock.move')

        #INCIO CAMBIOS PARA CANCELAR PICKING 
        picking_obj= self.pool.get('stock.picking')
        date = None
        sale= None
        pick_name=None
        pick_type =  None
        for pick in self.browse(cr, uid, ids, context=context):
            date=pick.date
            sale = pick.sale_id
            pick_name = pick.name
            pick_type = pick.type
        if not sale and pick_type == 'internal': 
            uid=1
            pick_ids=picking_obj.search(cr, uid,[('date','=',date),('name','=',pick_name),], order='date')          
            #_logger.error("stock IDDDD----: %r", pick_ids)
            for picks in picking_obj.browse(cr, uid, pick_ids):
                if picks.state in ('draft', 'assigned','confirmed'):
                    #_logger.error("IDDDD----: %r", ids)
                    ids2 = [move.id for move in picks.move_lines]
                    move_obj.action_cancel(cr, uid, ids2, context)
                    self.write(cr, uid, ids, {'state': 'cancel', 'invoice_state': 'none'})
        #FIN CAMBIOS

        for pick in self.browse(cr, uid, ids, context=context):
            ids2 = [move.id for move in pick.move_lines]
            move_obj.action_cancel(cr, uid, ids2, context)
        self.write(cr, uid, ids, {'state': 'cancel', 'invoice_state': 'none'})
        return True

    def action_cancel_draft(self, cr, uid, ids, *args):
        if not len(ids):
            return False
        move_obj = self.pool.get('stock.move')
        self.write(cr, uid, ids, {'state': 'draft'})
        wf_service = netsvc.LocalService("workflow")
        for p_id in ids:
            moves = move_obj.search(cr, uid, [('picking_id', '=', p_id)])
            move_obj.write(cr, uid, moves, {'state': 'draft'})
            # Deleting the existing instance of workflow for PO
            wf_service.trg_delete(uid, 'stock.picking', p_id, cr)
            wf_service.trg_create(uid, 'stock.picking', p_id, cr)
        for (id, name) in self.name_get(cr, uid, ids):
            message = _("Picking '%s' has been set in draft state.") % name
            self.log(cr, uid, id, message)
        return True
        
class stock_picking_in(osv.Model):
    _inherit = 'stock.picking.in'

    def action_cancel_draft(self, cr, uid, ids, *args):
        if not len(ids):
            return False
        move_obj = self.pool.get('stock.move')
        self.write(cr, uid, ids, {'state': 'draft'})
        wf_service = netsvc.LocalService("workflow")
        for p_id in ids:
            moves = move_obj.search(cr, uid, [('picking_id', '=', p_id)])
            move_obj.write(cr, uid, moves, {'state': 'draft'})
            # Deleting the existing instance of workflow for PO
            wf_service.trg_delete(uid, 'stock.picking', p_id, cr)
            wf_service.trg_create(uid, 'stock.picking', p_id, cr)
        for (id, name) in self.name_get(cr, uid, ids):
            message = _("Picking '%s' has been set in draft state.") % name
            self.log(cr, uid, id, message)
        return True
        
class stock_picking_out(osv.Model):
    _inherit = 'stock.picking.out'

    def action_cancel_draft(self, cr, uid, ids, *args):
        if not len(ids):
            return False
        move_obj = self.pool.get('stock.move')
        self.write(cr, uid, ids, {'state': 'draft'})
        wf_service = netsvc.LocalService("workflow")
        for p_id in ids:
            moves = move_obj.search(cr, uid, [('picking_id', '=', p_id)])
            move_obj.write(cr, uid, moves, {'state': 'draft'})
            # Deleting the existing instance of workflow for PO
            wf_service.trg_delete(uid, 'stock.picking', p_id, cr)
            wf_service.trg_create(uid, 'stock.picking', p_id, cr)
        for (id, name) in self.name_get(cr, uid, ids):
            message = _("Picking '%s' has been set in draft state.") % name
            self.log(cr, uid, id, message)
        return True

class stock_move(osv.Model):
    _inherit = 'stock.move'

    def action_cancel(self, cr, uid, ids, context=None):
        account_move_line = self.pool.get('account.move.line')
        account_move = self.pool.get('account.move')
        result = {}
        for move in self.browse(cr, uid, ids, context=context):
            account_move_line_id = account_move_line.search(
                cr, uid, [('stock_move_id', '=', move.id)])
            for move_line in account_move_line.browse(cr, uid, account_move_line_id,
                                                    context=context):
                result.setdefault(move_line.move_id.id, move.id)
                account_move_line.unlink(cr, uid, [move_line.id])
        for lin in result.items():
            account_production = account_move.browse(
                cr, uid, lin[0], context=context)
            if len(account_production.line_id) == 0:
                try:
                    account_move.button_cancel(cr, uid, [lin[0]], context=context)
                except:
                    pass
                account_move.unlink(cr, uid, [lin[0]])
        return super(stock_move, self).action_cancel(cr, uid, ids, context=context)