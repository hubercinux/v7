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


#from openerp.report import report_sxw
from report import report_sxw

import time
import netsvc
from datetime import datetime
from dateutil.relativedelta import relativedelta
import pytz
import logging
_logger = logging.getLogger(__name__)

#from openerp.osv import fields, osv, orm
#from openerp import tools

class kardex_valorizado_report(report_sxw.rml_parse):

    def _get_move_details(self, form):
        res = {}
        val= {}
        data = []
        move_qty_saldo = 0.0
        move_qty_saldo_ini = 0.0
        move_qty_total_in = 0.0
        move_qty_total_out = 0.0
        costo_total_in = 0.0
        costo_total_out = 0.0
        saldo_final = 0.0

        stock_move_obj = self.pool.get('stock.move')

        sale_obj = self.pool.get('sale.order')
        invoice_obj = self.pool.get('account.invoice')
        purchase_obj = self.pool.get('purchase.order')

        prod_id = form['product_ids'] 
        
        date_start = form['fecha_desde']
        date_end = form['fecha_hasta']
        
        fecha_utc_desde = (datetime.strptime(date_start + ' 00:00:00', '%Y-%m-%d %H:%M:%S') + relativedelta(hours=5)).strftime("%Y-%m-%d %H:%M:%S") 
        move_ids_desde = stock_move_obj.search(self.cr,self.uid,[('date','<',fecha_utc_desde),('product_id','=',prod_id[0]),('state','=','done')], order='date') 
        
        for move_desde in stock_move_obj.browse(self.cr, self.uid, move_ids_desde):

            #INGRESO DE PRODUCTOS
            if move_desde.location_id.usage == 'supplier' and move_desde.location_dest_id.usage == 'internal':
                move_qty_saldo_ini = move_qty_saldo_ini + move_desde.product_qty
                move_qty_saldo = move_qty_saldo_ini
                #PARA CORTES
                #saldo_final = saldo_final + move_desde.product_qty*((move_desde.product_id.list_price/1.18)*0.8)
                #saldo_costo_unitario_final = saldo_final/move_qty_saldo
            if move_desde.location_id.usage == 'production' and move_desde.location_dest_id.usage == 'internal':
                move_qty_saldo_ini = move_qty_saldo_ini + move_desde.product_qty
                move_qty_saldo = move_qty_saldo_ini
            if move_desde.location_id.usage == 'inventory' and move_desde.location_dest_id.usage == 'internal':
                move_qty_saldo_ini = move_qty_saldo_ini + move_desde.product_qty
                move_qty_saldo = move_qty_saldo_ini

            #SALIDAS DE PRODUCTOS
            if move_desde.location_id.usage == 'internal' and move_desde.location_dest_id.usage == 'customer':
                move_qty_saldo_ini = move_qty_saldo_ini - move_desde.product_qty
                move_qty_saldo = move_qty_saldo_ini
                #PARA CORTEZ
                #saldo_final = saldo_final - move_desde.product_qty*((move_desde.product_id.list_price/1.18)*0.8)
                #saldo_costo_unitario_final = saldo_final/move_qty_saldo
            if move_desde.location_id.usage == 'internal' and move_desde.location_dest_id.usage == 'production':
                move_qty_saldo_ini = move_qty_saldo_ini - move_desde.product_qty
                move_qty_saldo = move_qty_saldo_ini
            if move_desde.location_id.usage == 'internal' and move_desde.location_dest_id.usage == 'inventory':
                move_qty_saldo_ini = move_qty_saldo_ini - move_desde.product_qty
                move_qty_saldo = move_qty_saldo_ini          
        
        fecha_utc_hasta = (datetime.strptime(date_end + ' 23:59:59', '%Y-%m-%d %H:%M:%S') + relativedelta(hours=5)).strftime("%Y-%m-%d %H:%M:%S")
        stock_move_obj2 = self.pool.get('stock.move')       
        move_ids_hasta = stock_move_obj2.search(self.cr,self.uid,[('date','>=',fecha_utc_desde),('date','<=',fecha_utc_hasta),('product_id','=',prod_id[0]),('state','=','done'),], order='date')
                            
        for move in stock_move_obj2.browse(self.cr, self.uid, move_ids_hasta):
            res = {'produ_name': move.product_id.name,
                       'date': self._get_date_move(move.date),
                       'n_guia': move.picking_id.name,
                    }             
            ##########INGRESOS DE PRODUCTOS######################
            if move.location_id.usage == 'supplier' and move.location_dest_id.usage == 'internal':
                move_qty_saldo = move_qty_saldo + move.product_qty # Entradas Cantidad
                move_qty_total_in = move_qty_total_in + move.product_qty #Entradas totales(suma vertical)
                costo_total_in = costo_total_in + move.product_qty*(move.price_unit)#Entradas costo total(suma vertical)
                #costo_total_in = costo_total_in + move.product_qty*move.product_id.standard_price                
                #saldo_final = saldo_final + move.product_qty*move.product_id.standard_price
                saldo_final = saldo_final + move.product_qty*(move.price_unit)
                if move_qty_saldo == 0.0:
                    saldo_costo_unitario_final = 0.0
                else:
                    saldo_costo_unitario_final = saldo_final/move_qty_saldo

                res.update({'product_qty_in': move.product_qty , 'move_saldo': move_qty_saldo })
                #res.update({'product_qty_out': 0.0 })
                res.update({'produ_cost_compra': (move.price_unit) })
                #res.update({'produ_cost_compra': move.product_id.standard_price })
                res.update({'costo_total_compra': move.product_qty*(move.price_unit) })
                #res.update({'costo_total_compra': move.product_qty*move.product_id.standard_price })
                res.update({'saldo_final': saldo_final})
                res.update({'saldo_costo_unitario_final': saldo_costo_unitario_final })

                val.update({'move_qty_total_in': move_qty_total_in})
                val.update({'costo_total_in': costo_total_in})

                if move.location_id.usage == 'supplier' and move.location_dest_id.usage == 'internal':
                    res.update({'concept_move': 'COMPRA' })

                if move.origin:
                    if move.picking_id.type in ('in'):
                        purchase_order_id = purchase_obj.search(self.cr,self.uid,[('name','=',move.origin)]) # Obtenemos el id
                        for purchase in purchase_obj.browse(self.cr, self.uid, purchase_order_id):
                            account_invoice_id  = invoice_obj.search(self.cr,self.uid,[('origin','ilike',purchase.name)]) # Obtenemos el id
                            if account_invoice_id:
                                for invoice in invoice_obj.browse(self.cr, self.uid, account_invoice_id):                                    
                                    res.update({'n_fact': invoice.number })

                data.append(res)

            if move.location_id.usage == 'production' and move.location_dest_id.usage == 'internal':
                move_qty_saldo = move_qty_saldo + move.product_qty
                move_qty_total_in = move_qty_total_in + move.product_qty
                costo_total_in = costo_total_in + move.product_qty*(move.price_unit)
                
                saldo_final = saldo_final + move.product_qty*(move.price_unit)
                if move_qty_saldo == 0.0:
                    saldo_costo_unitario_final = 0.0
                else:
                    saldo_costo_unitario_final = saldo_final/move_qty_saldo

                res.update({'product_qty_in': move.product_qty , 'move_saldo': move_qty_saldo })
                #res.update({'product_qty_out': 0.0 })
                res.update({'produ_cost_compra': move.price_unit })
                res.update({'costo_total_compra': move.product_qty*(move.price_unit) })

                res.update({'saldo_final': saldo_final})
                res.update({'saldo_costo_unitario_final': saldo_costo_unitario_final })

                val.update({'move_qty_total_in': move_qty_total_in})
                val.update({'costo_total_in': costo_total_in})

                res.update({'n_fact': move.name })

                if move.location_id.usage == 'production' and move.location_dest_id.usage == 'internal':
                    res.update({'concept_move': 'PRODUCCION' })              
                data.append(res)

            if move.location_id.usage == 'inventory' and move.location_dest_id.usage == 'internal':
                move_qty_saldo = move_qty_saldo + move.product_qty
                move_qty_total_in = move_qty_total_in + move.product_qty 
                costo_total_in = costo_total_in + move.product_qty*(move.price_unit)
                
                saldo_final = saldo_final + move.product_qty*(move.price_unit)
                if move_qty_saldo == 0.0:
                    saldo_costo_unitario_final = 0.0
                else:
                    saldo_costo_unitario_final = saldo_final/move_qty_saldo

                res.update({'product_qty_in': move.product_qty , 'move_saldo': move_qty_saldo })
                #res.update({'product_qty_out': 0.0 })
                res.update({'produ_cost_compra': move.price_unit })
                res.update({'costo_total_compra': move.product_qty*(move.price_unit) })

                res.update({'saldo_final': saldo_final})
                res.update({'saldo_costo_unitario_final': saldo_costo_unitario_final })

                val.update({'move_qty_total_in': move_qty_total_in})
                val.update({'costo_total_in': costo_total_in})

                #res.update({'n_fact': move.name })

                res.update({'concept_move': 'INVENTARIO' })

                data.append(res)

            if move.location_id.usage == 'customer' and move.location_dest_id.usage == 'internal':
                move_qty_saldo = move_qty_saldo + move.product_qty
                move_qty_total_in = move_qty_total_in + move.product_qty 
                costo_total_in = costo_total_in + move.product_qty*(move.price_unit)
                
                saldo_final = saldo_final + move.product_qty*(move.price_unit)
                if move_qty_saldo == 0.0:
                    saldo_costo_unitario_final = 0.0
                else:
                    saldo_costo_unitario_final = saldo_final/move_qty_saldo

                res.update({'product_qty_in': move.product_qty , 'move_saldo': move_qty_saldo })
                #res.update({'product_qty_out': 0.0 })
                res.update({'produ_cost_compra': move.price_unit })
                res.update({'costo_total_compra': move.product_qty*(move.price_unit) })

                res.update({'saldo_final': saldo_final})
                res.update({'saldo_costo_unitario_final': saldo_costo_unitario_final })

                val.update({'move_qty_total_in': move_qty_total_in})
                val.update({'costo_total_in': costo_total_in})

                res.update({'n_fact': move.picking_id.name })

                if move.location_id.usage == 'customer' and move.location_dest_id.usage == 'internal':
                    res.update({'concept_move': 'DEVOLUCION' })
                
                data.append(res)

            if move.location_id.usage == 'composition' and move.location_dest_id.usage == 'internal':
                move_qty_saldo = move_qty_saldo + move.product_qty
                move_qty_total_in = move_qty_total_in + move.product_qty 
                costo_total_in = costo_total_in + move.product_qty*(move.price_unit)

                saldo_final = saldo_final + move.product_qty*(move.price_unit)
                if move_qty_saldo == 0.0:
                    saldo_costo_unitario_final = 0.0
                else:
                    saldo_costo_unitario_final = saldo_final/move_qty_saldo

                res.update({'product_qty_in': move.product_qty , 'move_saldo': move_qty_saldo })
                #res.update({'product_qty_out': 0.0 })
                res.update({'produ_cost_compra': move.price_unit })
                res.update({'costo_total_compra': move.product_qty*(move.price_unit) })

                res.update({'saldo_final': saldo_final})
                res.update({'saldo_costo_unitario_final': saldo_costo_unitario_final })

                val.update({'move_qty_total_in': move_qty_total_in})
                val.update({'costo_total_in': costo_total_in})

                res.update({'n_fact': move.picking_id.name })

                res.update({'concept_move': 'COMPOSICION' })
                
                data.append(res)

            if move.location_id.usage == 'ajuste' and move.location_dest_id.usage == 'internal':
                move_qty_saldo = move_qty_saldo + move.product_qty
                move_qty_total_in = move_qty_total_in + move.product_qty 
                costo_total_in = costo_total_in + move.product_qty*(move.price_unit)
                
                saldo_final = saldo_final + move.product_qty*(move.price_unit)
                if move_qty_saldo == 0.0:
                    saldo_costo_unitario_final = 0.0
                else:
                    saldo_costo_unitario_final = saldo_final/move_qty_saldo

                res.update({'product_qty_in': move.product_qty , 'move_saldo': move_qty_saldo })
                res.update({'produ_cost_compra': move.price_unit })
                res.update({'costo_total_compra': move.product_qty*(move.price_unit) })

                res.update({'saldo_final': saldo_final})
                res.update({'saldo_costo_unitario_final': saldo_costo_unitario_final })

                val.update({'move_qty_total_in': move_qty_total_in})
                val.update({'costo_total_in': costo_total_in})

                #res.update({'n_fact': move.name })

                res.update({'concept_move': 'AJUSTE' })

                data.append(res)

            ############EGRESOS DE PRODUCTOS###################
            if move.location_id.usage == 'internal' and move.location_dest_id.usage == 'customer':
                move_qty_saldo = move_qty_saldo - move.product_qty #Salidas Cantidad
                move_qty_total_out = move_qty_total_out + move.product_qty #Salidas totales(suma vertical)
                costo_total_out = costo_total_out + move.product_qty*(move.price_unit)#Salidas costo total(suma vertical)
                #costo_total_out = costo_total_out + move.product_qty*move.product_id.standard_price
                #saldo_final = saldo_final - move.product_qty*move.product_id.standard_price
                saldo_final = saldo_final - move.product_qty*(move.price_unit)
                if move_qty_saldo==0.0:
                    saldo_costo_unitario_final = 0.0
                else:
                    saldo_costo_unitario_final = saldo_final/move_qty_saldo

                res.update({'product_qty_out': move.product_qty,'move_saldo': move_qty_saldo})
                #res.update({'product_qty_in': 0.0})
                res.update({'produ_cost_venta': move.price_unit })
                #res.update({'produ_cost_venta': move.product_id.standard_price })
                res.update({'costo_total_venta': move.product_qty*(move.price_unit) })
                #res.update({'costo_total_venta': move.product_qty*move.product_id.standard_price })
                res.update({'saldo_final': saldo_final})
                res.update({'saldo_costo_unitario_final': saldo_costo_unitario_final })

                val.update({'move_qty_total_out': move_qty_total_out})
                val.update({'costo_total_out': costo_total_out})

                if move.location_id.usage == 'internal' and move.location_dest_id.usage == 'customer':
                    res.update({'concept_move': 'VENTA' })

                if move.origin:
                    if move.picking_id.type in ('out'):
                        sale_order_id = sale_obj.search(self.cr,self.uid,[('name','=',move.origin)]) # Obtenemos el id
                        for sale in sale_obj.browse(self.cr, self.uid, sale_order_id):
                            account_invoice_id  = invoice_obj.search(self.cr,self.uid,[('origin','=',sale.name)]) # Obtenemos el id
                            if account_invoice_id:
                                for invoice in invoice_obj.browse(self.cr, self.uid, account_invoice_id):
                                    res.update({'n_tipo': invoice.journal_id.name })
                                    res.update({'n_serie': invoice.journal_id.code })
                                    #_logger.error("DIARIOOOO: %r", invoice.journal_id.name )
                                    #_logger.error("DIARIOOOO: %r", invoice.journal_id.name[-2] )
                                    '''
                                    if invoice.journal_id.name[-2]=='01':
                                        res.update({'n_serie': '001' })
                                    if invoice.journal_id.name[-2]=='02':
                                        res.update({'n_serie': '002' }) 
                                    if invoice.journal_id.name[-2]=='03':
                                        res.update({'n_serie': '003' })
                                    if invoice.journal_id.name[-2]=='04':
                                        res.update({'n_serie': '004' })
                                    if invoice.journal_id.name[-2]=='06':
                                        res.update({'n_serie': '006' })
                                    if invoice.journal_id.name[-2]=='07':
                                        res.update({'n_serie': '007' })
                                    if invoice.journal_id.name[-2]=='08':
                                        res.update({'n_serie': '008' })
                                    if invoice.journal_id.name[-2]=='09':
                                        res.update({'n_serie': '009' })
                                    if invoice.journal_id.name[-2]=='10':
                                        res.update({'n_serie': '010' })
                                    '''
                                    res.update({'n_fact': invoice.number })                
                data.append(res)

            if move.location_id.usage == 'internal' and move.location_dest_id.usage == 'production':
                move_qty_saldo = move_qty_saldo - move.product_qty
                move_qty_total_out = move_qty_total_out + move.product_qty
                costo_total_out = costo_total_out + move.product_qty*(move.price_unit)
                
                saldo_final = saldo_final - move.product_qty*(move.price_unit)

                if move_qty_saldo == 0.0:
                    saldo_costo_unitario_final = 0.0
                else:
                    saldo_costo_unitario_final = saldo_final/move_qty_saldo

                res.update({'product_qty_out': move.product_qty,'move_saldo': move_qty_saldo})
                #res.update({'product_qty_in': 0.0})
                res.update({'produ_cost_venta': move.price_unit })                
                res.update({'costo_total_venta': move.product_qty*(move.price_unit) })

                res.update({'saldo_final': saldo_final})
                res.update({'saldo_costo_unitario_final': saldo_costo_unitario_final })
                
                val.update({'move_qty_total_out': move_qty_total_out})
                val.update({'costo_total_out': costo_total_out})

                res.update({'n_fact': move.name })

                if move.location_id.usage == 'internal' and move.location_dest_id.usage == 'production':
                    res.update({'concept_move': 'CONSUMO' })                
                data.append(res)

            if move.location_id.usage == 'internal' and move.location_dest_id.usage == 'composition':
                move_qty_saldo = move_qty_saldo - move.product_qty
                move_qty_total_out = move_qty_total_out + move.product_qty
                costo_total_out = costo_total_out + move.product_qty*(move.price_unit)
                
                saldo_final = saldo_final - move.product_qty*(move.price_unit)

                if move_qty_saldo == 0.0:
                    saldo_costo_unitario_final = 0.0
                else:
                    saldo_costo_unitario_final = saldo_final/move_qty_saldo

                res.update({'product_qty_out': move.product_qty,'move_saldo': move_qty_saldo})
                #res.update({'product_qty_in': 0.0})
                res.update({'produ_cost_venta': move.price_unit })                
                res.update({'costo_total_venta': move.product_qty*(move.price_unit) })

                res.update({'saldo_final': saldo_final})
                res.update({'saldo_costo_unitario_final': saldo_costo_unitario_final })
                
                val.update({'move_qty_total_out': move_qty_total_out})
                val.update({'costo_total_out': costo_total_out})

                res.update({'n_fact': move.name })

                res.update({'concept_move': 'COMPOSICION' })

                data.append(res)

            if move.location_id.usage == 'internal' and move.location_dest_id.usage == 'ajuste':
                move_qty_saldo = move_qty_saldo - move.product_qty
                move_qty_total_out = move_qty_total_out + move.product_qty
                costo_total_out = costo_total_out + move.product_qty*(move.price_unit)
                
                saldo_final = saldo_final - move.product_qty*(move.price_unit)
                if move_qty_saldo == 0.0:
                    saldo_costo_unitario_final =0.0
                else:
                    saldo_costo_unitario_final = saldo_final/move_qty_saldo

                res.update({'product_qty_out': move.product_qty,'move_saldo': move_qty_saldo})
                #res.update({'product_qty_in': 0.0})
                res.update({'produ_cost_venta': move.price_unit })
                res.update({'costo_total_venta': move.product_qty*(move.price_unit) })
                
                res.update({'saldo_final': saldo_final})
                res.update({'saldo_costo_unitario_final': saldo_costo_unitario_final })

                val.update({'move_qty_total_out': move_qty_total_out})
                val.update({'costo_total_out': costo_total_out})

                res.update({'concept_move': 'AJUSTE' })
                
                data.append(res)
       
        data.append(val)   
        
        return data
         
    def _get_name_product(self,form):
        res = {}
        data = []
        product_obj = self.pool.get('product.product')
        #_logger.error("my variable11 : %r", form['product_ids'])
        prod_id = form['product_ids'] 
        product_ids = product_obj.search(self.cr,self.uid,[('id','=',prod_id[0])]) # Obtenemos el id
        
        for produ in product_obj.browse(self.cr, self.uid, product_ids):
            res = {'product_name': produ.name }
            data.append(res)
        return data

    def __init__(self, cr, uid, name, context):
        super(kardex_valorizado_report, self).__init__(cr, uid, name, context)
        self.localcontext.update({
                        'time': time,
                        'get_move_details': self._get_move_details,
                        'get_name_product' : self._get_name_product,
                        'get_date_move': self._get_date_move,
                        #'get_name_location': self._get_name_location,               
        })

    def _get_date_move(self, fecha):
        if fecha:
            d = datetime.strptime(fecha, '%Y-%m-%d %H:%M:%S')
            d1=datetime.strftime(d, '%d/%m/%Y %H:%M:%S')
            return d1
        return ''
report_sxw.report_sxw('report.kardex.valorizado','stock.move', 'addons/kardex_valorizado/report/kardex_valorizado_report.rml',parser=kardex_valorizado_report,header=False)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
