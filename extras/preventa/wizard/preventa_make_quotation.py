##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
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

from openerp.osv import fields, osv
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp

class preventa_make_quotation(osv.osv_memory):
    _name = "preventa.make.quotation"
    _description = "Generacion de proforma"

    _columns = {
        'pricelist_id': fields.many2one('product.pricelist', 'Lista de Precios', required=True),
        'currency_id': fields.related('pricelist_id', 'currency_id', type="many2one", relation="res.currency", string="Moneda", required=True),
    }

    _defaults = {}

    def _prepare_quotation(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        preventa_obj = self.pool.get('preventa.visita')
        preventa_ids = context.get('active_ids', [])

        result = []
        for preventa in preventa_obj.browse(cr, uid, preventa_ids, context=context):
            sale_values = {
                'name': preventa.name,
                'partner_invoice_id': preventa.partner_id,
                'partner_shipping_id': preventa.partner_id,
                'pricelist_id': preventa.partner_id.property_product_pricelist,
                'currency_id': preventa.partner_id.property_product_pricelist.currency_id,
                'partner_id': preventa.partner_id,
            }
            result.append((preventa.id, sale_values))
        return result

    def _create_quotation(self, cr, uid, sale_values, preventa_id, context=None):
        sale_obj = self.pool.get('sale.order')
        preventa_obj = self.pool.get('preventa.visita')
        sale_id = sale_obj.create(cr, uid, sale_values, context=context)
        # add the preventa to the sales order
        preventa_obj.write(cr, uid, preventa_id, {'proforma': sale_id}, context=context)
        return sale_id

    def create_quotation(self, cr, uid, ids, context=None):
        """ create quotation for the active sales orders """
        preventa_obj = self.pool.get('preventa.visita')
        act_window = self.pool.get('ir.actions.act_window')
        wizard = self.browse(cr, uid, ids[0], context)
        preventa_ids = context.get('active_ids', [])

        sale_ids = []
        for preventa_id, sale_values in self._prepare_quotation(cr, uid, ids, context=context):
            sale_ids.append(self._create_quotation(cr, uid, sale_values, preventa_id, context=context))

        if context.get('open_quotation', False):
            return self.open_quotation( cr, uid, ids, sale_ids, context=context)
        return {'type': 'ir.actions.act_window_close'}

    def open_quotation(self, cr, uid, ids, sale_ids, context=None):
        """ open a view on one of the given sale_ids """
        ir_model_data = self.pool.get('ir.model.data')
        form_res = ir_model_data.get_object_reference(cr, uid, 'sale', 'view_order_form')
        form_id = form_res and form_res[1] or False
        tree_res = ir_model_data.get_object_reference(cr, uid, 'sale', 'view_quotation_tree')
        tree_id = tree_res and tree_res[1] or False

        return {
            'name': _('Generar Proforma'),
            'view_type': 'form',
            'view_mode': 'form,tree',
            'res_model': 'sale.order',
            'res_id': sale_ids[0],
            'view_id': False,
            'views': [(form_id, 'form'), (tree_id, 'tree')],
            'context': "",
            'type': 'ir.actions.act_window',
        }