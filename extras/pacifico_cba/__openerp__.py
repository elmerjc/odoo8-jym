# -*- coding: utf-8 -*-
{
    'name': "Comunicacion de baja",

    'summary': """
        Comunicacion de baja""",

    'description': """
        Comunicacion de baja
    """,

    'author': "ARC.PE",
    'website': "http://www.arc.pe",
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': [
        'base',
        'account',
    ],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'account_invoice_view.xml',
    ],
}