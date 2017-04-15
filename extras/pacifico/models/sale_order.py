# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models

class sale_order(models.Model):
	_inherit = 'sale.order'

	@api.one
	@api.depends('order_line')
	def _compute_quantity_total(self):
		self.quantity_total = sum(line.product_uom_qty for line in self.order_line)

	quantity_total = fields.Integer('Cantidad de pares', store=True, compute='_compute_quantity_total')