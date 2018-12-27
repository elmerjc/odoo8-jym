# -*- coding: utf-8 -*-
{
    'name': "Nota de Credito",

    'summary': """
        Nota de credito
    """,

    'description': """
        Nota de credito
    """,

    'author': "arc.pe",
    'website': "http://www.arc.pe",

    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': [
        'base',
        'account'
    ],
    'data' : [
        'views/account_invoice_view.xml',
    ],
    'active': False,
    'installable' : True,
}