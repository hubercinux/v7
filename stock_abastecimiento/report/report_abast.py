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

from openerp.report import report_sxw

from tools.translate import _

import logging
_logger = logging.getLogger(__name__)

class stock_abast_report(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(stock_abast_report, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,        
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


report_sxw.report_sxw('report.stock.abastecimiento.print',
                      'stock.abastecimiento',
                      'addons/stock_abastecimiento/report/report_abast.rml',
                      parser=stock_abast_report,header=False)
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:


