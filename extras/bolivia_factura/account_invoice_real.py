# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015-2016 S&C (<http://arc.pe>).
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
from openerp import api
from openerp.osv import osv, fields, expression
import openerp.addons.decimal_precision as dp

class account_invoice_real(osv.osv):
	_name = 'account.invoice.real'
	_description = "Factura"
	_order = "number desc, id desc"
	
	@api.one
	@api.depends('invoice_line')
	def _compute_amount_real(self):
		self.amount_untaxed_real = sum(line.price_subtotal_real for line in self.invoice_line)
		self.quantity_total = sum(line.quantity for line in self.invoice_line)
		self.amount_tax_real = 0 #sum(line.amount for line in self.tax_line) moficiar de acuerdo al impuesto
		self.amount_total_real = self.amount_untaxed_real + self.amount_tax_real

	_columns = {
		'name': fields.char('Referencia', index=True, readonly=True),
		'origin': fields.char('Pedido', index=True, readonly=True),
		'number': fields.char('Numero', store=True, readonly=True, copy=False),
		'comment': fields.text('Comentarios', store=True, readonly=True, copy=False),
		'date_invoice': fields.date('Fecha', index=True),
		'date_due': fields.date('Fecha Vencimiento', readonly=True, index=True, copy=False),
		'partner_id': fields.many2one('res.partner', string='Cliente', change_default=True, required=True),
		'invoice_line': fields.one2many('account.invoice.line.real', 'invoice_id', string='Items de la factura',  readonly=False, copy=True),
		'reconciled': fields.boolean('Pago', store=True, readonly=True),
		'residual': fields.boolean('Saldo', store=True, digits=dp.get_precision('Account')),
		'amount_untaxed': fields.float('Subtotal', digits=dp.get_precision('Account'), 
			store=True, readonly=True),
		'amount_tax': fields.float('Impuesto', digits=dp.get_precision('Account'), 
			store=True, readonly=True),
		'amount_total': fields.float('Total', digits=dp.get_precision('Account'), 
			store=True, readonly=True),
		'amount_untaxed_real': fields.float('Subtotal r', digits=dp.get_precision('Account'), 
			store=True, readonly=True, compute='_compute_amount_real'),
		'amount_tax_real': fields.float('Impuesto r', digits=dp.get_precision('Account'), 
			store=True, readonly=True, compute='_compute_amount_real'),
		'amount_total_real': fields.float('Total r', digits=dp.get_precision('Account'), 
			store=True, readonly=True, compute='_compute_amount_real'),
		'quantity_total': fields.integer('Cantidad de pares',
			store=True, readonly=True, compute='_compute_amount_real'),
		'currency_id' : fields.many2one('res.currency', string='Moneda',
			required=True, track_visibility='always'),
		'user_id' : fields.many2one('res.users', string='Responsable', track_visibility='onchange', readonly=True, default=lambda self: self.env.user),
		'state' : fields.selection([
			('draft','Borrador'),
			('open','Abierto'),
			('paid','Pagado'),
			('cancel','Cancelado'),
			], string='Estado', index=True, readonly=True, default='draft', track_visibility='onchange', copy=False,
			help=" * 'Borrador' comprobante aun no validado.\n"
			" * 'Abierto' comprobante aun no pagado.\n"
			" * 'Pagado' comprobante pagado.\n")
	}

	_sql_constraints = [
		('number_uniq', 'unique(number)', 'El numero de factura debe ser unico!'),
	]

	def action_create_comprobante(self, cr, uid, ids, context=None):
		number = self.pool.get('ir.sequence').get(cr, uid, 'account.invoice.real')
		self.write(cr, uid, ids, {'number': number, 'state': 'open'})
		return True

	def action_cancel_comprobante(self, cr, uid, ids, context=None):
		self.write(cr, uid, ids, {'state': 'cancel'})
		return True

	def action_open_comprobante(self, cr, uid, ids, context=None):
		self.write(cr, uid, ids, {'state': 'open'})
		return True

class account_invoice_line_real(osv.osv):
	_name = 'account.invoice.line.real'
	_description = "Items de la factura"
	_order = "invoice_id,id"

	@api.one
	@api.depends('price_unit_real', 'quantity', 'invoice_id')
	def _compute_price_real(self):
		self.price_subtotal_real = self.price_unit_real * self.quantity
		if self.invoice_id:
			self.price_subtotal_real = self.invoice_id.currency_id.round(self.price_subtotal_real)

	_columns = {
		'name': fields.char('Description', required=True),
		'origin': fields.char('Referencia', required=True),
		'sequence': fields.integer('Secuencia', default=10),
		'invoice_id' : fields.many2one('account.invoice.real', string='Comprobante referencia', ondelete='cascade', index=True),
		'product_id': fields.many2one('product.product', string='Producto', ondelete='set null', index=True),
		'price_unit': fields.float('Precio', digits=dp.get_precision('Product Price'), store=True, required=True),
		'price_subtotal': fields.float('Subtotal', digits=dp.get_precision('Account'),  store=True, readonly=True),
		'price_unit_real': fields.float('Precio r', digits=dp.get_precision('Product Price'), store=True),
		'price_subtotal_real': fields.float('Subtotal r', digits=dp.get_precision('Account'), store=True, readonly=True, compute='_compute_price_real'),
		'quantity': fields.float('Cantidad', digits= dp.get_precision('Product Unit of Measure'), required=True, default=1),
		'partner_id' : fields.many2one('res.partner', string='Cliente', related='invoice_id.partner_id', store=True, readonly=True),
	}