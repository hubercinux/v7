# -*- encoding: utf-8 -*-
##############################################################################
#
# OpenERP, Open Source Management Solution
# Copyright (c) 2015 S&C. (http://salazarcarlos.com).
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

from sale.report import sale_order
import time
from report import report_sxw
from tools.translate import _

class sale_order_update(sale_order.order):
    item = 0
    def __init__(self, cr, uid, name, context):
        super(sale_order_update, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
        #    'get_item': self._get_item,
        })

    #Para obtener el contador de item
    #def _get_item(self,move_lines):        
    #    self.item = self.item +1
    #    return {'items': self.item,}

report_sxw.report_sxw(
    'report.sale.orden.venta.update',
    'sale.order',
    'addons/sale_cotizacion/report/orden_venta.rml',
    parser=sale_order_update,
    header=False
)

report_sxw.report_sxw(
    'report.sale.orden.venta.update.sin',
    'sale.order',
    'addons/sale_cotizacion/report/orden_venta_sin.rml',
    parser=sale_order_update,
    header=False
)








# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: