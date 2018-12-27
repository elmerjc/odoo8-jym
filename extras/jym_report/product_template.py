# -*- coding: utf-8 -*-
from openerp.osv import fields,osv

class product_template(osv.osv):
    _inherit = 'product.template'

    _columns = {
        'verificar_stock': fields.boolean(string='Verificar stock', default=False),
    }