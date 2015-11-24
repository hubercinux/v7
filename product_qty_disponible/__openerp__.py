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


{
    "name": "Product Qty disponible",
    "version": "1.0",
    "description": """
       Añade atributes al producto para mostrar las cantidades disponibles y reservadas
    """,
    "author": "Ing. Javer Salazar Carlos",
    "website": "http://salazarcarlos.com",
    "category": "",
    "depends": [
            "base",
	        'product',
            'stock',
           # 'stock_picking_location',
        ],
    "data":[
            "product_view.xml",
            "wizard/product_location_wizard.xml",

        ],
    "demo_xml": [
        ],
    "update_xml": [
        ],
    "active": False,
    "installable": True,
    "certificate" : "",
    'images': [],
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: