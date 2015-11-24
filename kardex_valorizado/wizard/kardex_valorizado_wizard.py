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


#from openerp.osv import fields, osv
from osv import fields, osv

import logging
_logger = logging.getLogger(__name__)

class kardex_valorizado_wizard(osv.osv_memory):
#    _inherit = "account.common.journal.report"
    _name = 'kardex.valorizado.wizard'
    _description = 'Imprime el kardex de un producto'

    _columns = {
    #    'location_ids': fields.many2one('stock.location', 'Ubicacion', required="True"),
        'product_ids': fields.many2one('product.product', 'Producto'),
        'fecha_desde': fields.date('Desde'),
        'fecha_hasta': fields.date('Hasta'),

        #export hoja de calculo
        'name': fields.char('Nombre Archivo', size=64, readonly=True),
        'export_file': fields.binary('Exportar Archivo', readonly=True),
    }

    _defaults = {
    	'fecha_desde': '2015-01-01',
        'fecha_hasta': fields.date.context_today,
        #'fecha_desde': lambda *a: time.strftime('%Y-%m-%d'),
    	#'fecha_hasta': fields.date.context_today,
        #'fecha_hasta': lambda *a: time.strftime('%Y-%m-%d'),
    }

    def print_report(self, cr, uid, ids, context=None):
        datas = {}
        if context is None:
            context = {}
        #datas = {'ids': context.get('active_ids', [])} #
        res = self.read(cr, uid, ids, ['product_ids','fecha_desde','fecha_hasta'], context=context)
        res = res and res[0] or {}
        datas['form'] = res
        #_logger.error("my variable : %r", datas)
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'kardex.valorizado',
            'datas': datas,
        }

    def _get_name_product(self, cr, uid, product_id):

        product_obj = self.pool.get('product.product')
        product_ids = product_obj.search( cr, uid,[('id','=',product_id)]) # Obtenemos el id        
        name_produ = None
        for produ in product_obj.browse(cr, uid, product_ids):
            name_produ = produ.name 
        return name_produ

    def print_report_cal(self, cr, uid, ids, context=None):
        if context is None:
            context = {}

        form = self.read(cr, uid, ids, ['product_ids','fecha_desde','fecha_hasta'], context=context)
        form = form and form[0] or {}
        #data['form'] = res
        
        #_logger.error("SSSS ssdata: %r", data)

        user =  self.pool.get('res.users').browse(cr, uid, uid, context=context)
        user_tz = dateutil.tz.gettz(user.context_tz)
        utc_tz = dateutil.tz.tzutc()

        
        '''
        excel_tmp = cStringIO.StringIO()
        #excel_tmp = StringIO.StringIO()
        libro = xlsxwriter.Workbook(excel_tmp, {'in_memory': True})
        hoja = libro.add_worksheet()
        hoja.write(0,0, 'HOLA MUNDO11111111')
        libro.close()
        '''

        excel_tmp = cStringIO.StringIO()
        libro=Workbook(encoding='utf-8',style_compression=2)
        hoja = libro.add_sheet('Kardex valorizado',cell_overwrite_ok=True)
        #ANCHO DE COLUMNAS
        hoja.col(0).width = 1900
        hoja.col(1).width = 1400 #col tipo
        hoja.col(2).width = 1400 # col serie
        
        hoja.col(5).width = 2000
        hoja.col(6).width = 2500#costo entra unitario
        hoja.col(7).width = 2700#

        hoja.col(8).width = 2000
        hoja.col(9).width = 2500
        hoja.col(10).width = 2700

        hoja.col(11).width = 2000
        hoja.col(12).width = 2500
        hoja.col(13).width = 2700

        #syles0 : negrita
        style_bold = XFStyle()
        #font
        font = Font()
        font.bold = True
        font.height = 140
        style_bold.font = font
        #aling 
        alignment = Alignment()
        alignment.horz = Alignment.HORZ_CENTER
        alignment.vert = Alignment.VERT_CENTER
        style_bold.alignment = alignment


        #syles_01 para periodo, ruc, razon social, negrita
        style_bold_01 = XFStyle()
        #font
        font = Font()
        font.bold = True
        font.height = 140
        style_bold_01.font = font

        #syles_02 para periodo, ruc, razon social(sus valores), sin negrita
        style_02 = XFStyle()
        #font
        font = Font()
        font.height = 140
        style_02.font = font

        #syles_03 para las lineaa de movimiento
        style_03 = XFStyle()
        #font
        font = Font()
        font.height = 140
        style_03.font = font
        #border
        #borders
        borders = Borders()
        borders.bottom = Borders.THIN
        borders.top = Borders.THIN
        borders.left = Borders.THIN
        borders.right = Borders.THIN
        style_03.borders = borders

        #syles_04 celdas de color gris
        style_04 = XFStyle()
        #font
        font = Font()
        font.height = 140
        style_04.font = font
        #border
        #borders
        borders = Borders()
        borders.bottom = Borders.THIN
        borders.top = Borders.THIN
        borders.left = Borders.THIN
        borders.right = Borders.THIN
        style_04.borders = borders
        #color:
        pattern = Pattern()
        pattern.pattern=Pattern.SOLID_PATTERN
        pattern.pattern_fore_colour = 22 #color gray
        style_04.pattern = pattern


        #syles1
        style_headers1 = XFStyle()
        #font
        font = Font()
        font.bold = True
        font.height = 140
        style_headers1.font = font
        #borders
        borders = Borders()
        borders.bottom = Borders.THIN
        borders.top = Borders.THIN
        borders.left = Borders.THIN
        borders.right = Borders.THIN
        style_headers1.borders = borders
        #aling 
        alignment = Alignment()
        alignment.horz = Alignment.HORZ_CENTER
        alignment.vert = Alignment.VERT_CENTER
        style_headers1.alignment = alignment

        #syles1_1
        style_headers1_1 = XFStyle()
        #font
        font = Font()
        font.bold = True
        font.height = 140
        style_headers1_1.font = font
        #borders
        borders = Borders()
        borders.bottom = Borders.THIN
        borders.top = Borders.THIN
        borders.left = Borders.THIN
        borders.right = Borders.THIN
        style_headers1_1.borders = borders

        #syles2
        style_headers2 = XFStyle()
        #font
        font = Font()
        font.bold = True
        font.height = 140
        style_headers2.font = font
        #borders
        borders = Borders()
        borders.top = Borders.THIN
        borders.left = Borders.THIN
        borders.right = Borders.THIN
        style_headers2.borders = borders
        #aling 
        alignment = Alignment()
        alignment.horz = Alignment.HORZ_CENTER
        alignment.vert = Alignment.VERT_CENTER
        style_headers2.alignment = alignment


        #syles3
        style_headers3 = XFStyle()
        #font
        font = Font()
        font.bold = True
        font.height = 140
        style_headers3.font = font
        #borders
        borders = Borders()
        borders.bottom = Borders.THIN
        borders.left = Borders.THIN
        borders.right = Borders.THIN
        style_headers3.borders = borders
        #aling 
        alignment = Alignment()
        alignment.horz = Alignment.HORZ_CENTER
        alignment.vert = Alignment.VERT_CENTER
        style_headers3.alignment = alignment


        #syles4
        style_headers4 = XFStyle()
        #font
        font = Font()
        font.bold = True
        font.height = 140
        style_headers4.font = font
        #borders
        borders = Borders()
        borders.left = Borders.THIN
        borders.right = Borders.THIN
        style_headers4.borders = borders
        #aling 
        alignment = Alignment()
        alignment.horz = Alignment.HORZ_CENTER
        alignment.vert = Alignment.VERT_CENTER
        style_headers4.alignment = alignment


        #Header definition
        hoja.write_merge(0,0,0,13,'REGISTRO DE INVENTARIO PERMANENTE VALORIZADO',style=style_bold)

        hoja.write_merge(2,2,0,2,'PERIODO:',style=style_bold_01)
        hoja.write_merge(3,3,0,2,'RUC:',style=style_bold_01)
        hoja.write_merge(4,4,0,2,'RAZON SOCIAL:',style=style_bold_01)
        hoja.write_merge(5,5,0,2,'PRODUCTO:',style=style_bold_01)
        hoja.write_merge(6,6,0,2,'UNIDAD DE MEDIDA:',style=style_bold_01)

        hoja.write_merge(8,8,0,3,'DOCUMENTO DE TRASLADO, COMPROBANTE',style=style_headers2)
        hoja.write_merge(9,9,0,3,'DE PAGO, DOCUMENTO INTERNO O SIMILIAR',style=style_headers3)

        hoja.write_merge(8,8,4,4,'TIPO DE',style=style_headers2)
        hoja.write_merge(9,9,4,4,'OPERACION',style=style_headers4)

        hoja.write_merge(8,9,5,7,'ENTRADAS',style=style_headers1)
        hoja.write_merge(8,9,8,10,'SALIDAS',style=style_headers1)
        hoja.write_merge(8,9,11,13,'SALDO FINAL',style=style_headers1)

        hoja.write(10,0,'FECHA',style=style_headers1)
        hoja.write(10,1,'TIPO',style=style_headers1)
        hoja.write(10,2,'SERIE',style=style_headers1)
        hoja.write(10,3,'NUMERO',style=style_headers1)
        hoja.write(10,4,'',style=style_headers3)

        hoja.write(10,5,'CANTIDAD',style=style_headers1)
        hoja.write(10,6,'COSTO UNIT',style=style_headers1)
        hoja.write(10,7,'COSTO TOTAL',style=style_headers1)

        hoja.write(10,8,'CANTIDAD',style=style_headers1)
        hoja.write(10,9,'COSTO UNIT',style=style_headers1)
        hoja.write(10,10,'COSTO TOTAL',style=style_headers1)

        hoja.write(10,11,'CANTIDAD',style=style_headers1)
        hoja.write(10,12,'COSTO UNIT',style=style_headers1)
        hoja.write(10,13,'COSTO TOTAL',style=style_headers1)

        fecha_desde = datetime.strptime(form['fecha_desde'],'%Y-%m-%d')
        hoja.write(2,3, fecha_desde.strftime('%d/%m/%Y'),style=style_02)

        hoja.write(2,4, 'AL',style=style_02)

        fecha_hasta = datetime.strptime(form['fecha_hasta'],'%Y-%m-%d')
        hoja.write(2,5, fecha_hasta.strftime('%d/%m/%Y'),style=style_02)

        hoja.write(3,3, '20514540145',style=style_02)
        hoja.write(4,3, 'KIDDYS HOUSE SAC',style=style_02)
        hoja.write(5,3, self._get_name_product(cr, uid, form['product_ids']),style=style_02)
        hoja.write(6,3, 'UND',style=style_02)
        #_logger.error("SSSS ssdata: %r", self._get_move_details(cr,uid,res))

        #_logger.error("SSSS ssdata: %r", res)


        ########################################movimientos por fecha############################

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

        prod_id = form['product_ids'] # muestra una tupla (1,JAVIER SALAZAR CARLOS)
        #locat_id = form['location_ids']  
        
        date_start = form['fecha_desde']
        #date_start = '2013-08-01'
        date_end = form['fecha_hasta']
        #date_end = '2013-12-31'
        
        fecha_utc_desde = (datetime.strptime(date_start + ' 00:00:00', '%Y-%m-%d %H:%M:%S') + relativedelta(hours=0)).strftime("%Y-%m-%d %H:%M:%S") 
        move_ids_desde = stock_move_obj.search(cr, uid,[('date','<',fecha_utc_desde),('product_id','=',prod_id),('state','=','done')], order='date') 
        
        for move_desde in stock_move_obj.browse(cr, uid, move_ids_desde):

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
        
        fecha_utc_hasta = (datetime.strptime(date_end + ' 23:59:59', '%Y-%m-%d %H:%M:%S') + relativedelta(hours=0)).strftime("%Y-%m-%d %H:%M:%S")
        stock_move_obj2 = self.pool.get('stock.move')       
        #move_ids_hasta = stock_move_obj2.search(self.cr,self.uid,[('date','>=',fecha_utc_desde),('date','<=',fecha_utc_hasta),('product_id','=',prod_id),('state','=','done'),'|',('location_id','=',locat_id),('location_dest_id','=',locat_id)], order='date')
        move_ids_hasta = stock_move_obj2.search(cr, uid,[('date','>=',fecha_utc_desde),('date','<=',fecha_utc_hasta),('product_id','=',prod_id),('state','=','done'),], order='date')
        
        row = 11                  
        for move in stock_move_obj2.browse(cr, uid, move_ids_hasta): 
            res = {
                'produ_name': move.product_id.name,
                'date': move.date,
                'n_guia': move.picking_id.name,
                    }            

            ##########INGRESOS DE PRODUCTOS######################
            if move.location_id.usage == 'supplier' and move.location_dest_id.usage == 'internal':              
                fecha=datetime.strptime(move.date,'%Y-%m-%d %H:%M:%S')
                hoja.write(row,0, fecha.strftime('%d/%m/%Y'),style=style_03)

                move_qty_saldo = move_qty_saldo + move.product_qty # Entradas Cantidad
                move_qty_total_in = move_qty_total_in + move.product_qty #Entradas totales(suma vertical)
                costo_total_in = costo_total_in + move.product_qty*((move.product_id.list_price/1.18)*0.8)#Entradas costo total(suma vertical)
                #costo_total_in = costo_total_in + move.product_qty*move.product_id.standard_price                
                #saldo_final = saldo_final + move.product_qty*move.product_id.standard_price
                saldo_final = saldo_final + move.product_qty*((move.product_id.list_price/1.18)*0.8)#saldo costo final por linea

                if move_qty_saldo == 0.0:
                    saldo_costo_unitario_final = 0.0
                else:
                    saldo_costo_unitario_final = saldo_final/move_qty_saldo

                hoja.write(row,5,move.product_qty,style=style_03)

                #res.update({'produ_cost_compra': move.product_id.standard_price })
                hoja.write(row,6, '{0:.2f}'.format((move.product_id.list_price/1.18)*0.8),style=style_03)

                #res.update({'costo_total_compra': move.product_qty*move.product_id.standard_price })
                hoja.write(row,7, '{0:.2f}'.format(move.product_qty*((move.product_id.list_price/1.18)*0.8)),style=style_03)

                hoja.write(row,11, move_qty_saldo,style=style_03)#saldo cantidad final por lina de movimiento

                hoja.write(row,13, '{0:.2f}'.format(saldo_final),style=style_03)#saldo costo final por linea

                hoja.write(row,12, '{0:.2f}'.format(saldo_costo_unitario_final),style=style_03)

                if move.location_id.usage == 'supplier' and move.location_dest_id.usage == 'internal':
                    hoja.write(row,4,'COMPRA',style=style_03)

                if move.origin:
                    if move.picking_id.type in ('in'):
                        purchase_order_id = purchase_obj.search(cr, uid,[('name','=',move.origin)]) # Obtenemos el id
                        for purchase in purchase_obj.browse(cr, uid, purchase_order_id):
                            account_invoice_id  = invoice_obj.search(cr, uid,[('origin','ilike',purchase.name)]) # Obtenemos el id
                            if account_invoice_id:
                                for invoice in invoice_obj.browse(cr, uid, account_invoice_id):                                    
                                    if invoice.number:
                                        hoja.write(row,3, invoice.number,style=style_03)
                                        hoja.write(row,1,'',style=style_03)
                                        hoja.write(row,2,'',style=style_03)
                                    else:
                                        hoja.write(row,3,'',style=style_03)
                                        hoja.write(row,1,'',style=style_03)
                                        hoja.write(row,2,'',style=style_03)
                            else:
                                hoja.write(row,3,'',style=style_03)
                                hoja.write(row,1,'',style=style_03)
                                hoja.write(row,2,'',style=style_03)

                else:
                    hoja.write(row,1,'',style=style_03)
                    hoja.write(row,2,'',style=style_03)
                    hoja.write(row,3,'',style=style_03)
                    
                hoja.write(row,8,'',style=style_03)
                hoja.write(row,9,'',style=style_03)
                hoja.write(row,10,'',style=style_03)
                row =row+1            


            if move.location_id.usage == 'production' and move.location_dest_id.usage == 'internal':
                fecha=datetime.strptime(move.date,'%Y-%m-%d %H:%M:%S')
                hoja.write(row,0, fecha.strftime('%d/%m/%Y'),style=style_03)

                move_qty_saldo = move_qty_saldo + move.product_qty
                move_qty_total_in = move_qty_total_in + move.product_qty
                costo_total_in = costo_total_in + move.product_qty*((move.product_id.list_price/1.18)*0.8)
                
                saldo_final = saldo_final + move.product_qty*((move.product_id.list_price/1.18)*0.8)
                if move_qty_saldo == 0.0:
                    saldo_costo_unitario_final = 0.0
                else:
                    saldo_costo_unitario_final = saldo_final/move_qty_saldo

                hoja.write(row,5,move.product_qty,style=style_03)

                hoja.write(row,6, '{0:.2f}'.format((move.product_id.list_price/1.18)*0.8),style=style_03)

                hoja.write(row,7, '{0:.2f}'.format(move.product_qty*((move.product_id.list_price/1.18)*0.8)),style=style_03)

                hoja.write(row,11, move_qty_saldo,style=style_03)#saldo cantidad final por lina de movimiento

                hoja.write(row,13, '{0:.2f}'.format(saldo_final),style=style_03)#saldo costo final por linea

                hoja.write(row,12, '{0:.2f}'.format(saldo_costo_unitario_final),style=style_03)


                res.update({'n_fact': move.name })
                hoja.write(row,3, move.name,style=style_03)

                if move.location_id.usage == 'production' and move.location_dest_id.usage == 'internal':
                    res.update({'concept_move': 'PRODUCCION' })
                    hoja.write(row,4,'PRODUCCION',style=style_03)

                hoja.write(row,1,'',style=style_03)
                hoja.write(row,2,'',style=style_03)

                hoja.write(row,8,'',style=style_03)
                hoja.write(row,9,'',style=style_03)
                hoja.write(row,10,'',style=style_03)
                row =row+1 

            if move.location_id.usage == 'inventory' and move.location_dest_id.usage == 'internal' and move.location_id.id == 38:
                fecha=datetime.strptime(move.date,'%Y-%m-%d %H:%M:%S')
                hoja.write(row,0, fecha.strftime('%d/%m/%Y'),style=style_03)

                move_qty_saldo = move_qty_saldo + move.product_qty
                move_qty_total_in = move_qty_total_in + move.product_qty 
                costo_total_in = costo_total_in + move.product_qty*((move.product_id.list_price/1.18)*0.8)
                
                saldo_final = saldo_final + move.product_qty*((move.product_id.list_price/1.18)*0.8)
                if move_qty_saldo == 0.0:
                    saldo_costo_unitario_final = 0.0
                else:
                    saldo_costo_unitario_final = saldo_final/move_qty_saldo

                hoja.write(row,5,move.product_qty,style=style_03)

                hoja.write(row,6, '{0:.2f}'.format((move.product_id.list_price/1.18)*0.8),style=style_03)

                hoja.write(row,7, '{0:.2f}'.format(move.product_qty*((move.product_id.list_price/1.18)*0.8)),style=style_03)

                hoja.write(row,11, move_qty_saldo,style=style_03)#saldo cantidad final por lina de movimiento

                hoja.write(row,13, '{0:.2f}'.format(saldo_final),style=style_03)#saldo costo final por linea

                hoja.write(row,12, '{0:.2f}'.format(saldo_costo_unitario_final),style=style_03)

                #res.update({'n_fact': move.name })

                if move.location_id.id == 38:
                    hoja.write(row,4,'INVENTARIO',style=style_03)  
                #if move.location_id.id == 5:
                #    res.update({'concept_move': 'AJUSTE' })
                hoja.write(row,1,'',style=style_03)
                hoja.write(row,2,'',style=style_03)
                hoja.write(row,3,'',style=style_03)

                hoja.write(row,8,'',style=style_03)
                hoja.write(row,9,'',style=style_03)
                hoja.write(row,10,'',style=style_03)
                row =row+1 
                
                

            if move.location_id.usage == 'customer' and move.location_dest_id.usage == 'internal':
                fecha=datetime.strptime(move.date,'%Y-%m-%d %H:%M:%S')
                hoja.write(row,0, fecha.strftime('%d/%m/%Y'),style=style_03)

                move_qty_saldo = move_qty_saldo + move.product_qty
                move_qty_total_in = move_qty_total_in + move.product_qty 
                costo_total_in = costo_total_in + move.product_qty*((move.product_id.list_price/1.18)*0.8)
                
                saldo_final = saldo_final + move.product_qty*((move.product_id.list_price/1.18)*0.8)
                if move_qty_saldo == 0.0:
                    saldo_costo_unitario_final = 0.0
                else:
                    saldo_costo_unitario_final = saldo_final/move_qty_saldo

                hoja.write(row,5,move.product_qty,style=style_03)

                hoja.write(row,6, '{0:.2f}'.format((move.product_id.list_price/1.18)*0.8),style=style_03)

                hoja.write(row,7, '{0:.2f}'.format(move.product_qty*((move.product_id.list_price/1.18)*0.8)),style=style_03)

                hoja.write(row,11, move_qty_saldo,style=style_03)#saldo cantidad final por lina de movimiento

                hoja.write(row,13, '{0:.2f}'.format(saldo_final),style=style_03)#saldo costo final por linea

                hoja.write(row,12, '{0:.2f}'.format(saldo_costo_unitario_final),style=style_03)

                hoja.write(row,3, move.picking_id.name,style=style_03)

                if move.location_id.usage == 'customer' and move.location_dest_id.usage == 'internal':
                    hoja.write(row,4,'DEVOLUCION',style=style_03)  
                
                hoja.write(row,1,'',style=style_03)
                hoja.write(row,2,'',style=style_03)

                hoja.write(row,8,'',style=style_03)
                hoja.write(row,9,'',style=style_03)
                hoja.write(row,10,'',style=style_03)
                row =row+1


            ############EGRESOS DE PRODUCTOS###################
            if move.location_id.usage == 'internal' and move.location_dest_id.usage == 'customer':
                fecha=datetime.strptime(move.date,'%Y-%m-%d %H:%M:%S')
                hoja.write(row,0, fecha.strftime('%d/%m/%Y'),style=style_03)

                move_qty_saldo = move_qty_saldo - move.product_qty #Salidas Cantidad
                move_qty_total_out = move_qty_total_out + move.product_qty #Salidas totales(suma vertical)
                costo_total_out = costo_total_out + move.product_qty*((move.product_id.list_price/1.18)*0.8)#Salidas costo total(suma vertical)
                #costo_total_out = costo_total_out + move.product_qty*move.product_id.standard_price
                #saldo_final = saldo_final - move.product_qty*move.product_id.standard_price
                saldo_final = saldo_final - move.product_qty*((move.product_id.list_price/1.18)*0.8)
                if move_qty_saldo==0.0:
                    saldo_costo_unitario_final = 0.0
                else:
                    saldo_costo_unitario_final = saldo_final/move_qty_saldo

                hoja.write(row,8,move.product_qty,style=style_03)

                hoja.write(row,9, '{0:.2f}'.format((move.product_id.list_price/1.18)*0.8),style=style_03)

                hoja.write(row,10, '{0:.2f}'.format(move.product_qty*((move.product_id.list_price/1.18)*0.8)),style=style_03)

                hoja.write(row,11, move_qty_saldo,style=style_03)#saldo final por linea

                hoja.write(row,13, '{0:.2f}'.format(saldo_final),style=style_03)#saldo costo final por linea

                hoja.write(row,12, '{0:.2f}'.format(saldo_costo_unitario_final),style=style_03)


                if move.location_id.usage == 'internal' and move.location_dest_id.usage == 'customer':
                    hoja.write(row,4,'VENTA',style=style_03)

                if move.origin:
                    if move.picking_id.type in ('out'):
                        sale_order_id = sale_obj.search(cr,uid,[('name','=',move.origin)]) # Obtenemos el id
                        for sale in sale_obj.browse(cr, uid, sale_order_id):
                            account_invoice_id  = invoice_obj.search(cr,uid,[('origin','=',sale.name)]) # Obtenemos el id
                            if account_invoice_id:
                                for invoice in invoice_obj.browse(cr, uid, account_invoice_id):                            
                                    if invoice.number:
                                        hoja.write(row,1, invoice.journal_id.name[:3],style=style_03)
                                        if invoice.journal_id.name[:3] == 'BOL':
                                            hoja.write(row,2, invoice.journal_id.name[7:],style=style_03) 
                                        else:
                                            hoja.write(row,2, invoice.journal_id.name[8:],style=style_03) 
                                        hoja.write(row,3, invoice.number,style=style_03)
                                    else:
                                        hoja.write(row,3, '',style=style_03)
                                        hoja.write(row,1, '',style=style_03) 
                                        hoja.write(row,2, '',style=style_03) 
                            else:
                                hoja.write(row,3, '',style=style_03)
                                hoja.write(row,1, '',style=style_03) 
                                hoja.write(row,2, '',style=style_03)
                else:
                    hoja.write(row,3, '',style=style_03)
                    hoja.write(row,1, '',style=style_03) 
                    hoja.write(row,2, '',style=style_03)

                hoja.write(row,5,'',style=style_03)
                hoja.write(row,6,'',style=style_03)
                hoja.write(row,7,'',style=style_03)
                row =row+1

            if move.location_id.usage == 'internal' and move.location_dest_id.usage == 'production':
                fecha=datetime.strptime(move.date,'%Y-%m-%d %H:%M:%S')
                hoja.write(row,0, fecha.strftime('%d/%m/%Y'),style=style_03)

                move_qty_saldo = move_qty_saldo - move.product_qty
                move_qty_total_out = move_qty_total_out + move.product_qty
                costo_total_out = costo_total_out + move.product_qty*((move.product_id.list_price/1.18)*0.8)
                
                saldo_final = saldo_final - move.product_qty*((move.product_id.list_price/1.18)*0.8)

                if move_qty_saldo == 0.0:
                    saldo_costo_unitario_final = 0.0
                else:
                    saldo_costo_unitario_final = saldo_final/move_qty_saldo

                hoja.write(row,8,move.product_qty,style=style_03)

                hoja.write(row,9, '{0:.2f}'.format((move.product_id.list_price/1.18)*0.8),style=style_03)

                hoja.write(row,10, '{0:.2f}'.format(move.product_qty*((move.product_id.list_price/1.18)*0.8)),style=style_03)

                hoja.write(row,11, move_qty_saldo,style=style_03)#saldo final por linea

                hoja.write(row,13, '{0:.2f}'.format(saldo_final),style=style_03)#saldo costo final por linea

                hoja.write(row,12, '{0:.2f}'.format(saldo_costo_unitario_final),style=style_03)
            
                hoja.write(row,3,move.name,style=style_03)

                if move.location_id.usage == 'internal' and move.location_dest_id.usage == 'production':
                    hoja.write(row,4,'CONSUMO',style=style_03)               
                
                hoja.write(row,1,'',style=style_03)
                hoja.write(row,2,'',style=style_03)
                

                hoja.write(row,5,'',style=style_03)
                hoja.write(row,6,'',style=style_03)
                hoja.write(row,7,'',style=style_03)
                row =row+1

        ########################################fin##############################################

        hoja.write(row,4,'TOTALES',style=style_headers1_1)
        hoja.write(row,5,move_qty_total_in,style=style_03)
        hoja.write(row,6,'',style=style_04)
        hoja.write(row,7,'{0:.2f}'.format(costo_total_in),style=style_03)
        hoja.write(row,8,move_qty_total_out ,style=style_03)
        hoja.write(row,9,'',style=style_04)
        hoja.write(row,10, '{0:.2f}'.format(costo_total_out),style=style_03)
        hoja.write(row,11,'',style=style_04)
        hoja.write(row,12,'',style=style_04)
        hoja.write(row,13,'',style=style_04)        


        libro.save(excel_tmp)
        out = base64.encodestring(excel_tmp.getvalue())
        excel_tmp.close()
        file_time = datetime.now(user_tz).strftime('%Y-%m-%d_%H%M')
        return self.write(cr, uid, ids,{ 'export_file': out, 
                                          'name': 'kardex_valorizado_%s.xls' % (file_time) })




# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
