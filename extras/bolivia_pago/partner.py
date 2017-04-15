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
from openerp.osv import fields,osv
from openerp.exceptions import except_orm, Warning, RedirectWarning
import openerp.addons.decimal_precision as dp
import logging
_logger = logging.getLogger(__name__)

class res_partner(osv.osv):
	_inherit = 'res.partner'

	def _amount_positive(self, cr, uid, ids, field_name, arg, context=None):
		res = dict(map(lambda x: (x,0), ids))
		try:
			favor = 0.00
			for partner in self.browse(cr, uid, ids, context):
				debe = sum(order_id.amount_total for order_id in partner.sale_order_ids)
				haber = sum(pago.amount for pago in partner.pagos_ids)
			favor = haber - debe
			res[partner.id] = favor
		except:
			pass
		return res

	_columns = {
		'amount_positive': fields.function(_amount_positive, string='Monto a favor', digits=dp.get_precision('Account'), type='float'),
		'pagos_ids': fields.one2many('bolivia.pago', 'partner_id', 'Pagos'),
	}