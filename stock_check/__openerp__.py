{
    'name': "Stock picking check",
    'description': "Verifica los productos contenido en un picking",
    'category': 'Hidden',
    'depends': ['stock','web'],
    'data': ['stock_check.xml'],
    'js': ['static/src/js/stock_check.js'],
    'css': ['static/src/css/stock_check.css'],
    'qweb': ['static/src/xml/stock_check.xml'],
}