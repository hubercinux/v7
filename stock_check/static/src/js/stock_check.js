//console.log("Debug statement: archivo leido");
openerp.stock_check = function (instance) {
    //console.log("Modulo leido");
    
    instance.web.client_actions.add('stock_check.action', 'instance.stock_check.verificar');
    
    //instance.stock_check.verificar = function (parent, action) {
    //    console.log("ejecutando the action", action);
    //};

    /*
    instance.stock_check.verificar = instance.web.Widget.extend({
        className: 'oe_stock_check',
        start: function () {
            this.$el.text("Hello, world!");
            return this._super();
        }
    });
    */

    
	instance.stock_check.verificar = instance.web.Widget.extend({
        template: 'stock_check.teme',
        events: {
        'click button': 'confirmar_picking',
        'change :checkbox': 'completar_cantidad',
        },
        init: function (parent,options) {
            this._super(parent);
            options = options || {};
            this.picking_id = options.context.active_id;
            //console.log("ejecutando the arguments2", options.context.active_id);
            //this._super.apply(this, arguments);
            this.model_stock = new instance.web.Model('stock.picking');      
            this.model_move = new instance.web.Model('stock.move'); 
            this.model_product = new instance.web.Model('product.product'); 
            this.URLactual = window.location.href;
            this.product_ids = [];
        },
        start: function () { 
            var self = this;
            var model = new instance.web.Model('stock.move');
            $(".form-control").focus();

            //this.$('.form-control').click(function(){});

            this.$('.form-control').keypress(function(e){
                //self.on_searchbox($(this).val());
                if(e.keyCode == 13){                
                    self.on_searchbox($('input', this).val());
                    //console.log("codigo barras", $('input', this).val());
                }
            });

            if (!this.picking_id) {
                var k = this.URLactual.lastIndexOf('=');
                //console.log("ejecutando the argument1s", k);
                this.picking_id = parseInt(this.URLactual.substring (k+1));
                ///console.log("ejecutando the argument2s", this.picking_id);
            }                                                       
            model.call('search', [[['picking_id','=',this.picking_id]]]).then(function (ids) { 
                var move_ids = [];
                for(var i = 0; i < ids.length; i++){
                    move_ids.push(ids[i]);
                    //$('.table').find("tbody").append('<tr><td class="text_center_'+move[i].product_id[0]+'"></td><td>'+move[i].name+'</td><td class="text_center">'+move[i].product_qty+'</td><td><input type="text" value="0"/></td><td><input type="checkbox"></td></tr>');
                    }
                //console.log("EJECUTANDO1", move_ids);
                return model.call('read', [move_ids, ['id','product_id','name', 'product_qty']]);
            }).then(function (moves) {
                var product_ids = [];
                for(var i = 0; i < moves.length; i++){
                    product_ids.push(moves[i].product_id[0]);
                    $('.table').find("tbody").append('<tr class="product_'+moves[i].product_id[0]+'"><td class="text_center_'+moves[i].product_id[0]+'"></td><td>'+moves[i].name+'</td><td class="qty_db_'+moves[i].product_id[0]+'">'+moves[i].product_qty+'</td><td><input id="qty_'+moves[i].product_id[0]+'"  type="text" value="0"/></td><td><input class="box_check" id="check_'+moves[i].product_id[0]+'" type="checkbox" value="'+moves[i].product_id[0]+'"></td></tr>');
                    }
                //console.log("EJECUTANDO2", product_ids);
                //self.$(".oe_pos_demo_editar_detail").text(result.name);
                return  new instance.web.Model('product.product').call('read', [product_ids, ['id','name', 'ean13']]);
            }).then(function (products) {
                //console.log("EJECUTANDO3", products);
                for(var i = 0; i < products.length; i++){                
                    self.$(".text_center_"+products[i].id).text(products[i].ean13);
                }                
                //return  new instance.web.Model('product.product').call('read', [product_ids, ['id','name', 'ean13']]);
            });    

            return this.model_stock.query()
                .filter([['id', '=', this.picking_id]])
                .all().done(function (picking) {  
                    //_(records).each(display);
                    $('.title_picking_number').text(picking[0].name);

                });
        },

        on_searchbox: function(ean13){  
            var self = this;          
            var model = new instance.web.Model('product.product');
            model.call('search', [[['ean13','=',ean13]]]).then(function (product_id) {
                //console.log("ejecutando esto", product_id);
                if (product_id) {
                    var valor = $('#qty_'+product_id).val();
                    var qty_scaneada = parseInt(valor) + 1;
                    var qty_db = $('.qty_db_'+product_id).text();
                    //console.log("CATN DB", qty_db);
                    if (parseInt(qty_scaneada) == parseInt(qty_db)){
                        $("#check_"+product_id).prop("checked", true);
                        $(".product_"+product_id).css({'background-color':'chartreuse'});
                        //console.log("ejecutando esto", qty_scaneada);
                    }
                    if (parseInt(qty_scaneada) > parseInt(qty_db)) {
                        $("#check_"+product_id).prop("checked", false);
                        $(".product_"+product_id).css({'color':'white','background-color':'red'});

                    }
                    self.$('#qty_'+product_id).val(qty_scaneada);
                    $(".oe_searchbox").val('');
                    $(".form-control").focus();
                    
                }
            });
        },

        confirmar_picking: function (){
            var model = new instance.web.Model('stock.picking');
            var checkboxes =  $(".table input[type=checkbox]");   
            var checkboxes_checked =  $(".table input[type=checkbox]:checked");         
            if (checkboxes.length == checkboxes_checked.length){
                model.call('write',[this.picking_id,{'verificado': true}],{context: new instance.web.CompoundContext()});
                this.do_action({
                    type: 'ir.actions.act_window',
                    res_model: 'stock.picking',
                    res_id: this.picking_id,
                    views: [[false, 'form']],
                    target: 'current',
                });                 
            } else {
                alert('VERIFICACION INCOMPLETA!!!');
            }           
            //console.log("ejecutando 1", checkboxes.length); 
        },

        completar_cantidad: function(){
            var product_id = null;
            //var checkboxes_checked =  $(".table input[type=checkbox]:checked");
            //var input_check = [];
            $(".box_check:checked").each(function() {
                //input_check.push(this.value);
                product_id = this.value;
                var qty = $('.qty_db_'+product_id).text();                
                var new_qty = $('#qty_'+product_id).val();
                //console.log("ejecutando2", new_qty );
                if (parseInt(new_qty) == 0){
                    $('#qty_'+product_id).val(qty);
                    $(".product_"+product_id).css({'background-color':'chartreuse'});
                }
            });
            $(".box_check:unchecked").each(function() {
                //input_check.push(this.value);
                product_id = this.value;
                //console.log("ejecutando2", product_id );
                var qty = $('.qty_db_'+product_id).text();                
                var new_qty = $('#qty_'+product_id).val();
                //console.log("ejecutando2", new_qty );
                if (parseInt(new_qty) != 0){
                    $('#qty_'+product_id).val(0);
                    $(".product_"+product_id).removeAttr("style");
                    $(".product_"+product_id).css({'background-color':'turquoise'});
                }
            });
            
        },

    });   
    
};