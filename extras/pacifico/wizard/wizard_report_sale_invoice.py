from datetime import datetime
from openerp import tools, api
from openerp.osv import osv, orm, fields
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp

class wizard_report_sale_invoice(osv.osv_memory):
    _name = 'wizard.report.sale.invoice'
    _description = 'Reporte del analisis de factura de venta'
    _columns = {
        'date_inicio': fields.date('Desde', required=True),
        'date_fin': fields.date('Hasta', required=True),
    }

    _defaults = {
        'date_inicio': False,
        'date_fin': False,
    }

    def open_table(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        data = self.read(cr, uid, ids, context=context)[0]
        ctx = context.copy()
        ctx['date_inicio'] = data['date_inicio']
        ctx['date_fin'] = data['date_fin']
        ctx['search_default_group_by_recibo'] = True
        return {
            'domain': "[('date', '>=', '" + data['date_inicio'] + "'), ('date', '<=', '" + data['date_fin'] + "')]",
            'name': _('Analisis de facturas de venta'),
            'view_type': 'form',
            'view_mode': 'graph',
            'res_model': 'report.sale.invoice',
            'type': 'ir.actions.act_window',
            'context': ctx,
        }

class report_sale_invoice(osv.osv):
    _name = 'report.sale.invoice'
    _auto = False
    _order = 'date asc'

    _columns = {
        'number': fields.char('Numero'),
        'date': fields.date('Fecha'),
        'product_id': fields.many2one('product.product', 'Producto'),
        'categ_id': fields.many2one('product.category', 'Categoria del producto'),
        'quantity': fields.float('Cantidad'),
        'recibo': fields.char('Recibo'),
        'partner_id': fields.many2one('res.partner', 'Cliente'),
        'period_id': fields.many2one('account.period', 'Periodo'),
        'user_id': fields.many2one('res.users', 'Responsable'),
        'recibo': fields.char('Recibo'),
        'nbr': fields.integer('# lineas'),
        'state': fields.selection([
            ('draft','Draft'),
            ('proforma','Pro-forma'),
            ('proforma2','Pro-forma'),
            ('open','Open'),
            ('paid','Paid'),
            ('cancel','Cancelled'),
        ], string='Estado'),
        'date_due': fields.date('Fecha vencimiento'),
        'price_total': fields.float('Total', group_operator='sum', digits=dp.get_precision('Account')),
        'residual': fields.float('Saldo', group_operator='sum', digits=dp.get_precision('Account')),
    }

    def init(self, cr):
        tools.drop_view_if_exists(cr, 'report_sale_invoice')
        cr.execute("""
            CREATE OR REPLACE VIEW report_sale_invoice AS (
              SELECT min(ail.id) AS id,
                ai.number,
                ai.date_invoice AS date,
                ail.product_id,
                pt.x_recibo AS recibo,
                ai.partner_id,
                ai.period_id,
                ai.user_id,
                count(ail.*) AS nbr,
                ai.state,
                pt.categ_id,
                ai.date_due,
                sum(
                CASE
                    WHEN ai.type::text = ANY (ARRAY['out_refund'::character varying::text, 'in_invoice'::character varying::text]) THEN (- ail.quantity) / u.factor
                    ELSE ail.quantity / u.factor
                END) AS quantity,
                sum(
                CASE
                    WHEN ai.type::text = ANY (ARRAY['out_refund'::character varying::text, 'in_invoice'::character varying::text]) THEN - ail.price_subtotal
                    ELSE ail.price_subtotal
                END) AS price_total,
                CASE
                    WHEN ai.type::text = ANY (ARRAY['out_refund'::character varying::text, 'in_invoice'::character varying::text]) THEN - ai.residual
                    ELSE ai.residual
                END /
                CASE
                    WHEN (( SELECT count(l.id) AS count
                       FROM account_invoice_line l
                     LEFT JOIN account_invoice a ON a.id = l.invoice_id
                      WHERE a.id = ai.id)) <> 0 THEN ( SELECT count(l.id) AS count
                       FROM account_invoice_line l
                     LEFT JOIN account_invoice a ON a.id = l.invoice_id
                      WHERE a.id = ai.id)
                    ELSE 1::bigint
                END::numeric AS residual
                FROM account_invoice_line ail
                JOIN account_invoice ai ON ai.id = ail.invoice_id
                JOIN res_partner partner ON ai.partner_id = partner.id
                LEFT JOIN product_product pr ON pr.id = ail.product_id
                LEFT JOIN product_template pt ON pt.id = pr.product_tmpl_id
                LEFT JOIN product_uom u ON u.id = ail.uos_id
                WHERE ai.state in ('open','paid') AND ai.type in ('out_invoice', 'out_refund')
                GROUP BY ail.product_id, pt.x_recibo, ai.date_invoice, ai.id, ai.partner_id, ai.period_id, ai.user_id, ai.type, ai.state, pt.categ_id, ai.date_due, ai.residual, ai.amount_total
            )""")