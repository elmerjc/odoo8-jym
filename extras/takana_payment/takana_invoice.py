# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015-2016 S&C (<http://takanags.com>).
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
from datetime import datetime
from openerp import api
from openerp.exceptions import except_orm, Warning, RedirectWarning
from openerp.osv import osv, fields, expression
import openerp.addons.decimal_precision as dp
from openerp.tools.translate import _
import logging
_logger = logging.getLogger(__name__)

class takana_guia(osv.osv):
	_name = 'takana.guia'
	_description = "Gestiona el numero de guia de remision"
	_order = "id desc"

	_columns = {
		'name': fields.char('Numero de guia de remision', index=True),
	}

class takana_invoice(osv.osv):
	_name = 'takana.invoice'
	_description = "Gestiona los datos de la factura"
	_order = "id desc"

	@api.one
	@api.depends('amount_total', 'currency_id', 'tax_id')
	def _compute_amount(self):
		total = self.amount_total
		tax = self.amount_total * self.tax_id.amount
		untaxed = self.amount_total - tax

		if self.currency_id:
			if self.date_invoice:
				if not self.currency_id.base:
					rate = self._get_current_rate(self.date_invoice, self.currency_id.id)
					if rate:
						total = total * rate
						tax = total * self.tax_id.amount
						untaxed = total - tax
			total = self.currency_id.compute(total, self.currency_id, round=False)
			untaxed = self.currency_id.compute(untaxed, self.currency_id, round=False)
			tax = self.currency_id.compute(tax, self.currency_id, round=False)

		self.amount_total = self.currency_id.round(total)
		self.amount_untaxed = self.currency_id.round(untaxed)
		self.amount_tax = self.currency_id.round(tax)

	@api.one
	@api.depends('amount_total', 'payment_ids', 'currency_id', 'tax_id')
	def _compute_residual(self):
		residual = 0.00
		debe = 0.00
		haber = self.amount_total
		#debe = sum(payment.amount_total for payment in self.payment_ids)
		for payment in self.payment_ids:
			if payment.date_cancel:
				debe += payment.amount_total
		residual = haber - debe
		
		self.residual = self.currency_id.round(residual)

	def _get_current_rate(self, date, currency_id):
		#_logger.debug("CURRENCY : %r", currency_id)
		self.env.cr.execute("""SELECT rate FROM res_currency_rate 
			WHERE currency_id = %s 
			AND TO_CHAR(name, 'YYYY-mm-dd') <= %s 
			ORDER BY name desc LIMIT 1 """,
			(currency_id, date))
		if self.env.cr.rowcount:
			rate = self.env.cr.fetchone()[0]
		else:
			rate = False
			currency = self.env['res.currency'].browse(currency_id)
			raise osv.except_osv(_('Error!'),_("No existe tipo de cambio en '%s' para la fecha %s" % (currency.name, date)))
		return rate

	_columns = {
		'name': fields.char('Registro', index=True,  default='/', readonly=True),
		'comment': fields.char('Observaciones', copy=False),
		'date_invoice': fields.date('Fecha de emisión', required=True, index=True, readonly=True, states={'open': [('readonly', False)], 'done': [('readonly', False)]}),
		'date_expiration': fields.date('Fecha de vencimiento', readonly=True, states={'open': [('readonly', False)], 'done': [('readonly', False)]}),
		'type_invoice': fields.selection([('supplier', 'Proveedor'), ('customer', 'Cliente')], 'Tipo de factura', readonly=True),
		'type_voucher': fields.selection([('BOL', 'Boleta'), ('FAC', 'Factura'), ('NDC', 'Nota de credito'), ('NDD', 'Nota de debito')], 'Tipo de Comprobante', required=True, readonly=True, states={'open': [('readonly', False)], 'done': [('readonly', False)]}),
		'number_invoice': fields.char('Numero', required=True, index=True),
		'guia_ids': fields.many2many('takana.guia', 'takana_invoice_guia_rel', 'invoice_id', 'guia_id', 'Guia de remision'),
		'origin_invoice': fields.char('Numero Factura'),
		'partner_id': fields.many2one('res.partner', 'Proveedor', readonly=True, states={'open': [('readonly', False)]}, required=True, change_default=True, select=True, track_visibility='always'),
		'amount_total': fields.float('Importe', digits=(16,2), required=True, readonly=True, states={'open': [('readonly', False)], 'done': [('readonly', False)]}),
		'amount_tax': fields.float('Impuesto', digits=(16,2), readonly=True, store=True, compute='_compute_amount'),
		'amount_untaxed': fields.float('Importe bruto', digits=(16,2), readonly=True, store=True, compute='_compute_amount'),
		'residual':  fields.float('Saldo', digits=(16,2), readonly=True, store=True, compute='_compute_residual'),
		'tax_id': fields.many2one('account.tax', 'Impuesto', required=True, readonly=True, states={'open': [('readonly', False)]}, default=2),
		'currency_id': fields.many2one('res.currency', 'Moneda', required=True, readonly=True, states={'open': [('readonly', False)]}, default=3),
		'payment_term': fields.selection([('Contado', 'Contado'), ('Credito', 'Credito')], 'Pago', default='Contado', required=True, readonly=True, states={'open': [('readonly', False)], 'done': [('readonly', False)]}),
		'payment_dues': fields.integer('N° Cuotas', default=1, required=True),
		'payment_ids': fields.one2many('takana.payment', 'invoice_id', string='Pagos',  readonly=True, states={'open': [('readonly', False)], 'done': [('readonly', False)]}, copy=True),
		'user_id' : fields.many2one('res.users', string='Responsable', track_visibility='onchange', readonly=True, default=lambda self: self.env.user),
		'state' : fields.selection([
			('open','Abierto'),
			('cancel','Cancelado'),
			('done','Realizado'),
			('close','Cerrado'),
			], string='Estado', index=True, readonly=True, default='open', track_visibility='onchange', copy=False),
	}

	_sql_constraints = [
		('number_invoice_uniq', 'unique(number_invoice, partner_id)', 'El numero de factura debe ser unico por proveedor'),
	]

	def create(self, cr, uid, vals, context=None):
		if context is None:
			context = {}
		if vals.get('name', '/') == '/':
			vals['name'] = self.pool.get('ir.sequence').get(cr, uid, 'takana.invoice', context=context) or '/'
		new_id = super(takana_invoice, self).create(cr, uid, vals, context=context)
		return new_id

	def action_done(self, cr, uid, ids, context=None):
		self.write(cr, uid, ids, {'state': 'done'})
		return True

	def action_cancel(self, cr, uid, ids, context=None):
		self.write(cr, uid, ids, {'state': 'cancel'})
		return True

	def action_open(self, cr, uid, ids, context=None):
		self.write(cr, uid, ids, {'state': 'open'})
		return True

	def action_close(self, cr, uid, ids, context=None):
		self.write(cr, uid, ids, {'state': 'close'})
		return True

	def number_invoice_change(self, cr, uid, ids, number_invoice, partner_id, context=None):
		context = context or {}
		invoice_obj = self.pool.get('takana.invoice')

		if not number_invoice:
			return {'value': {}, 'domain': {}}
		else:
			result = {}
			domain = {}
			warning = False

			invoice_id = invoice_obj.search(cr, uid, [('number_invoice','=', number_invoice),('partner_id','=', partner_id)])
			invoice_obj = invoice_obj.browse(cr, uid, invoice_id, context=context)

			result['origin_invoice'] = invoice_obj.number_invoice
			#result['partner_id'] = invoice_obj.partner_id.id
			result['currency_id'] = invoice_obj.currency_id.id
			result['amount_total'] = invoice_obj.amount_total

			return {'value': result, 'domain': domain, 'warning': warning}