# -*- coding: utf-8 -*-
{
    'name': "Facturador SUNAT",

    'summary': """
		Crea los archivos planos para el facturador de SUNAT
    """,

    'description': """
        Crea los archivos planos para el facturador de SUNAT
        Factura, Nota de credito y Comunicación de baja
    """,

    'author': "ARC.PE",
    'website': "http://www.arc.pe",

    'category': 'Uncategorized',
    'version': '0.1',

    'depends': [
    	'base',
        'knowledge',
    	'account',
        'pacifico_cba',
        'pacifico_nota_credito',
    ],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'account_invoice_view.xml',
    ],
}