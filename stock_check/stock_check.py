from openerp.osv import osv, fields
import openerp.netsvc as netsvc
from openerp.tools.translate import _
import logging
_logger = logging.getLogger(__name__)


class stock_picking(osv.Model):
    _inherit = 'stock.picking'

    def open_client_stock_check(self, cr, uid, ids, context=None):
        context = context or {}
        #data = self.browse(cr, uid, ids[0], context=context)
        context['active_id'] = ids[0]        
        #_logger.error("CONETXT----: %r", context) 
        return {
            'type' : 'ir.actions.client',
            'name' : 'Start Modulo Stock Ckeck',
            'tag' : 'stock_check.action',
            'context' : context,
        }
class stock_picking(osv.Model):
    _inherit = 'stock.picking.out'

    def open_client_stock_check(self, cr, uid, ids, context=None):
        context = context or {}
        #data = self.browse(cr, uid, ids[0], context=context)
        context['active_id'] = ids[0]
        return {
            'type' : 'ir.actions.client',
            'name' : 'Start Modulo Stock Ckeck',
            'tag' : 'stock_check.action',
            'context' : context,
        }    