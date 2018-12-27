# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://aroc.pe>).
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

from openerp import tools
import openerp.addons.decimal_precision as dp
from openerp.osv import fields,osv

class librana_saldo_report(osv.osv):
    _name = "librana.saldo.report"
    _description = "Reporte de saldos a favor de compras"
    _auto = False
    _rec_name = 'number'

    _columns = {
        'id': fields.integer('ID Factura', readonly=True),
        'number': fields.char('Numero', readonly=True),
        'origin': fields.char('Proforma', readonly=True),
        'date_invoice': fields.date('Fecha Compra', readonly=True),
        'date_invoice': fields.date('Fecha Vencimiento', readonly=True),
        'total_factura': fields.float('Total Factura', readonly=True),
        'total_proforma': fields.float('Total Proforma', readonly=True),
        'partner_id': fields.many2one('res.partner', 'Cliente', readonly=True),
        'user_id': fields.many2one('res.users', 'Responsable', readonly=True),
        'period_id': fields.many2one('account.period', 'Periodo', readonly=True),
        'saldo': fields.float('Saldo', readonly=True),
    }
    _order = 'date_invoice desc'

    def _select(self):
        select_str = """
            ai.id,
            ai.number,
            ai.origin,
            ai.date_invoice,
            ai.date_due,
            ai.amount_total as total_factura,
            ai.partner_id,
            ai.user_id,
            ai.period_id,
            (select po.amount_total from purchase_order po where po.name = ai.origin) as total_proforma,
            ai.amount_total - (select po.amount_total from purchase_order po where po.name = ai.origin) as saldo
        """
        return select_str

    def _from(self):
        from_str = """
            account_invoice ai 
            where ai.type='in_invoice'
        """
        return from_str

    def init(self, cr):
        tools.drop_view_if_exists(cr, self._table)
        cr.execute("""CREATE or REPLACE VIEW %s as (
            SELECT %s 
            FROM %s 
        )""" % (self._table,self._select(), self._from()))