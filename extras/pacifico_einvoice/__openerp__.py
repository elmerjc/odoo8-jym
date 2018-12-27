# -*- coding: utf-8 -*-
{
    'name': "Factura Electronica Distribuidor del Pacifico",

    'summary': """
        Factura electronica      
    """,

    'description': """
        Factura electronica
    """,

    'author': "",
    'website': "http://www.arc.pe",
    'category': 'Uncategorized',
    'version': '0.1',

    'depends': [
    	'base',
    	'base_ubl'
    ],

    'data': [
        'account_invoice_view.xml',
        'company_view.xml',
    ],
}