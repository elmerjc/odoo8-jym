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
from openerp import api, _
from openerp.exceptions import except_orm, Warning, RedirectWarning
from openerp.osv import fields, osv, expression
import openerp.addons.decimal_precision as dp

class bolivia_pago(osv.osv):
	_name = 'bolivia.pago'
	_description = 'Pagos de los comprobantes cliente'
	_order = 'date'

	_columns = {
		'sequence': fields.integer('Secuencia', default=1),
		'sale_id': fields.many2one('sale.order', 'Pedido', index=True),
		'date': fields.date('Fecha', required=True),
		'metodo': fields.selection([
			('fassil','FASSIL'),
			('union','UNION'),
			('efectivo','Efectivo'),
			('favor','A favor'),
			], string='Metodo', default='efectivo'),
		'name': fields.char('Operación'),
		'amount': fields.float('Monto', digits=dp.get_precision('Account'), store=True, required=True, change_default=True),
		'state': fields.selection([('open', 'Abierto'), ('close', 'Cerrado')], 'Estado', default='open'),
		'sale_total': fields.float('Total', related='sale_id.amount_total', readonly=True),
		'sale_name': fields.char('Pedido', related='sale_id.name', readonly=True),
		'partner_id': fields.related('sale_id', 'partner_id', type='many2one', relation='res.partner', string='Cliente', readonly=True, store=True),
		'comment': fields.text('Comentarios', store=True, readonly=True, copy=False),
	}

	_defaults = {
		'date': fields.datetime.now,
	}

	def check_pago_change(self, cr, uid, ids, sale, partner_id, monto, total, context=None):
		
		sale_obj = self.pool.get('sale.order')
		sale_id = sale_obj.search(cr, uid, [('name', '=', sale)], context=context)
		#sale_data = sale_obj.browse(cr, uid, sale_id, context=context)
		pago_ids = self.search(cr, uid, [('sale_id', '=', sale_id)], context=context)
		pagos = self.browse (cr, uid, pago_ids, context=context)

		partner_obj = self.pool.get('res.partner')
		partner_data = partner_obj.browse(cr, uid, partner_id, context=context)

		debe = total
		haber = sum(pago.amount for pago in pagos)
		amortizacion = monto

		saldo = debe - haber

		if saldo > 0:
			if amortizacion > saldo:
				sale_obj.write(cr, uid, ids, {'state': 'done'})
				raise Warning(_('Pago a favor'), _("Se agrego al cliente %s un monto a favor") % (partner_data.name) )
			else:
				if amortizacion == saldo:
					sale_obj.write(cr, uid, ids, {'state': 'done'})
				else:
					sale_obj.write(cr, uid, ids, {'state': 'progress'})
		else:
			raise except_orm(_('Error en el saldo'), _("El pedido ya fue pagado") )

		val = {
			'amount' : monto
		}
		return {'value' : val}