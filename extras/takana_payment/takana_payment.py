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
from openerp.osv import osv, fields, expression

class takana_payment(osv.osv):
	_name = 'takana.payment'
	_description = "Pagos realizados"
	_order = "numero_cuota asc"

	@api.one
	@api.depends('amount_expiration', 'amount_due', 'amount', 'amount_commission', 'amount_ift')
	def _compute_total(self):
		self.amount_total = self.amount + self.amount_expiration + self.amount_due + self.amount_commission + self.amount_ift

	@api.one
	@api.depends('date_expiration', 'date_cancel')
	def _compute_days_due(self):
		date_format = '%Y-%m-%d'
		from_date = self.date_expiration
		today = datetime.today()

		d1 = datetime.strptime(from_date, date_format)

		if self.date_cancel:
			to_date = self.date_cancel
			d2 = datetime.strptime(to_date, date_format)
		else:
			d2 = today.strftime(date_format)
			d2 = datetime.strptime(d2, date_format)

		daysDiff = str((d2-d1).days)
		if int(daysDiff) > 0:
			self.days_due = int(daysDiff)
		else:
			self.days_due = 0

	_columns = {
		'name': fields.char('Description', default=''),
		'sequence': fields.integer('Secuencia', default=1),
		'numero_cuota': fields.integer('N°', default=1),
		'reference': fields.char('Letra'),
		'payment_type': fields.selection([('supplier', 'Proveedor'), ('customer', 'Cliente')], 'Tipo de pago', readonly=True),
		'invoice_id' : fields.many2one('takana.invoice', string='Factura', ondelete='cascade'),
		'date_issue': fields.date('Fecha emision', required=True),
		'date_expiration': fields.date('Fecha vencimiento', required=True),
		'date_cancel': fields.date('Fecha pago'),
		'days_due': fields.integer('Dias de mora', store=True, compute='_compute_days_due', readonly=True),
		'amount_expiration': fields.float('Intereses por vencimiento', digits=(16,2), default=0),
		'amount_due': fields.float('Intereses por mora', digits=(16,2), default=0),
		'amount_commission': fields.float('Com. Dev. valorado', digits=(16,2), default=0),
		'amount_protesto': fields.float('Com. de protesto', digits=(16,2), default=0),
		'amount_notaria': fields.float('Gastos notariales', digits=(16,2), default=0),
		'amount_ift': fields.float('ITF', digits=(16,2), default=0),
		'amount': fields.float('Importe', digits=(16,2)),
		'amount_total': fields.float('Total', digits=(16,2), store=True, compute='_compute_total'),
		#'amount': fields.related('invoice_id', 'amount_total', type='float', digits=(16,2), string='Importe', readonly=True, store=True),
		'bank': fields.selection([('BCP', 'BCP'), ('IBK', 'IBK'), ('BBVA', 'BBVA'), ('SBK', 'SBK')], 'Banco', default='BCP', required=True),
		'comment': fields.char('Observaciones', copy=False),
		'number_invoice': fields.related('invoice_id', 'number_invoice', type='char', string='Numero', readonly=True, store=True),
	}