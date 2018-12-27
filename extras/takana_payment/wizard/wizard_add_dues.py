# -*- coding: utf-8 -*-
from openerp import models, fields, api
from datetime import datetime, timedelta
import logging
_logger = logging.getLogger(__name__)

class wizard_add_dues(models.TransientModel):
	_name = 'wizard.add.dues'
	_description = 'Agregar cuotas'
	
	@api.model
	def _default_amount_total(self):
		invoice_id = self._context['active_id']
		invoice = self.env['takana.invoice'].browse(invoice_id)
		return invoice.amount_total

	payment_dues = fields.Integer('Numero de cuotas', required=True)
	amount_total = fields.Float('Importe de la factura', digits=(16,2), required=False, default=_default_amount_total)
	date_issue = fields.Date('Fecha de emision', required=True, default=datetime.today())
	date_expiration = fields.Date('Fecha de vencimiento', required=True, default=datetime.today())

	@api.one
	def add_dues(self):
		active_id = self._context['active_id']

		payment_term = 'Contado'
		if self.payment_dues > 1:
			payment_term = 'Credito'

		i = 1
		days = 30
		date_expiration = self.date_expiration
		date_expiration = datetime.strptime(date_expiration, '%Y-%m-%d')

		amount = self.amount_total / self.payment_dues
		#_logger.debug("AMOUNT : %r", amount)

		while i <= self.payment_dues:
			date_expiration = date_expiration + timedelta(days=days)
			val = {
				'numero_cuota': i,
				'payment_type': 'supplier',
				'invoice_id': active_id,
				'date_issue': self.date_issue,
				'date_expiration': date_expiration,
				'amount': amount,
			}
			self.env['takana.payment'].create(val)
			i += 1
			days = 15

		self.env.cr.execute(""" 
			UPDATE takana_invoice 
			SET date_expiration = '%s', 
				payment_dues = %s, 
				amount_total = %s, 
				payment_term = '%s' 
			WHERE id = %s""" %(date_expiration.strftime('%Y-%m-%d'), self.payment_dues, self.amount_total, payment_term, active_id))