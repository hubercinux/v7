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

{
    "name" : "Stock abastecimiento",
    "version" : "0.1",
    "author" : "Ing. Javier Salazar Carlos",
    "description" : """
                    Permite gestionar los abasteciminietos por locales, gestiona los stock minimos y maximo.
                    """,
    "website" : "http://salazarcarlos.com",
    "depends" : ["base", "stock", 'product', 'pos_printer_extend','sale_order_cancel',],
    "data" : [
            'security/security.xml',
            'security/ir.model.access.csv',
            'wizard/stock_max_min_wizard.xml',
            'wizard/abast_consol_wizard.xml',
            'stock_abastecimiento.xml',
	    'report.xml',
            'search.xml',

    ],
    "demo_xml" : [
    ],
    "update_xml" : [

    ],
    "active": False,
    "installable": True,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
