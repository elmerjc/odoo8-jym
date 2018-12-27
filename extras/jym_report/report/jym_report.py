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

class account_invoice_report(osv.osv):
    _name = "jym.report"
    _description = "Reporte de Comprobantes"
    _auto = False
    _rec_name = 'date_invoice'

    _columns = {
        'date_invoice': fields.date('Fecha', readonly=True),
        'journal_id': fields.many2one('account.journal', 'Diario', readonly=True),
        'partner_id': fields.many2one('res.partner', 'Cliente', readonly=True),
        'company_id': fields.many2one('res.company', 'Empresa', readonly=True),
        'user_id': fields.many2one('res.users', 'Responsable', readonly=True),
        'period_id': fields.many2one('account.period', 'Periodo', domain=[('state','<>','done')], readonly=True),
        'amount_untaxed': fields.float('Total Bruto', readonly=True),
        'amount_tax': fields.float('Impuesto', readonly=True),
        'amount_total': fields.float('Total', readonly=True),
        'nbr': fields.integer('# Facturas', readonly=True), 
        'type': fields.selection([
            ('out_invoice','Customer Invoice'),
            ('in_invoice','Supplier Invoice'),
            ('out_refund','Customer Refund'),
            ('in_refund','Supplier Refund'),
            ],'Tipo', readonly=True),
        'state': fields.selection([
            ('draft','Draft'),
            ('proforma','Pro-forma'),
            ('proforma2','Pro-forma'),
            ('open','Open'),
            ('paid','Done'),
            ('cancel','Cancelled')
            ], 'Estado', readonly=True),
        'number': fields.char('Numero', readonly=True),
        
    }
    _order = 'date_invoice desc'

    def _select(self):
        select_str = """
                ai.id, 
                ai.partner_id,
                ai.number,
                ai.date_invoice,
                ai.journal_id,
                aj.name as diario,
                ai.amount_untaxed,
                ai.amount_tax,
                ai.amount_total, 
                ai.type, 
                ai.state,
                ai.company_id,
                ai.user_id,
                count(ai.*) as nbr,
                ai.period_id
        """
        return select_str

    def _from(self):
        from_str = """
                account_invoice ai
                inner join res_partner rp ON ai.partner_id = rp.id
                inner join account_journal aj ON ai.journal_id = aj.id
                where ai.type='out_invoice' and ai.state not in ('cancel', 'draft')
        """
        return from_str

    def init(self, cr):
        tools.drop_view_if_exists(cr, self._table)
        cr.execute("""CREATE or REPLACE VIEW %s as (
            SELECT %s 
            FROM %s 
            GROUP BY  
                ai.id, 
                ai.partner_id,
                rp.name,
                ai.internal_number,
                ai.number,
                ai.date_invoice,
                ai.journal_id,
                aj.name,
                ai.amount_untaxed,
                ai.amount_tax,
                ai.amount_total, 
                ai.type, 
                ai.state,
                ai.company_id,
                ai.user_id,
                ai.period_id 
        )""" % (self._table,self._select(), self._from()))