# -*- encoding: utf-8 -*-
from datetime import datetime
from openerp import tools
from openerp.osv import fields, osv
from openerp.report import report_sxw

class report_payment(osv.osv):
    _name = "report.payment"
    _description = "Reporte de letras de pago"
    _auto = False
    _rec_name = 'registro'

    _columns = {
        'registro': fields.char('Registro', readonly=True),
        'partner_id': fields.many2one('res.partner', 'Proveedor', readonly=True),
        'number_invoice': fields.char('Numero', readonly=True),
        'date_invoice': fields.date('Fecha emision', readonly=True),  
        'total': fields.float('Importe', digits=(16,2), readonly=True),
        'numero_cuota': fields.integer('N°', readonly=True),
        'bank': fields.selection([
            ('BCP', 'BCP'), 
            ('IBK', 'IBK'), 
            ('BBVA', 'BBVA'), 
            ('SBK', 'SBK')], 'Banco', readonly=True),
        'letra': fields.char('Letra', readonly=True),
        'date_expiration': fields.date('Fecha vencimiento', readonly=True),
        'period_expiration': fields.char('Periodo vencimiento', readonly=True),
        'amount': fields.float('Importe cuota', digits=(16,2), readonly=True),
        'date_cancel': fields.date('Fecha pago', readonly=True),
        'days_due': fields.integer('Dias de mora', readonly=True),
        'amount_expiration': fields.float('Importe vencimiento', digits=(16,2), readonly=True),
        'amount_due': fields.float('Importe interes', digits=(16,2), readonly=True),
        'amount_commission': fields.float('Importe comision', digits=(16,2), readonly=True),
        'amount_protesto': fields.float('Importe protesto', digits=(16,2), readonly=True),
        'amount_notarial': fields.float('Importe notaria', digits=(16,2), readonly=True),
        'amount_ift': fields.float('ITF', digits=(16,2), readonly=True),
        'amount_total': fields.float('Importe total', digits=(16,2), readonly=True),
    }
    _order = 'date_expiration asc'

    def init(self, cr):
        tools.drop_view_if_exists(cr, self._table)
        cr.execute("""CREATE or REPLACE VIEW %s as (
            SELECT 
                tp.id,
                ti.name as registro,
                ti.partner_id,
                rp.name as partner,
                ti.number_invoice,
                ti.date_invoice,
                ti.amount_total as total,
                tp.numero_cuota,
                tp.bank,
                tp.reference as letra,
                tp.date_expiration,
                tp.amount,
                tp.date_cancel,
                tp.days_due,
                tp.amount_expiration,
                tp.amount_due,
                tp.amount_commission,
                tp.amount_protesto,
                tp.amount_notaria,
                tp.amount_ift,
                tp.amount_total,
                rc.symbol as moneda,
				(SELECT rate FROM res_currency_rate rcr WHERE rcr.name = tp.date_cancel AND rcr.currency_id = ti.currency_id) as rate,
                TO_CHAR(tp.date_expiration, 'MM') AS period_expiration
            FROM takana_payment tp 
            INNER JOIN takana_invoice ti ON tp.invoice_id = ti.id 
            INNER JOIN res_partner rp ON ti.partner_id = rp.id 
            INNER JOIN res_currency rc ON ti.currency_id = rc.id 
            ORDER BY date_expiration asc
            )""" % (self._table))

class report_payment_wizard(report_sxw.rml_parse):
    def __init__(self,cr,uid,name,context=None):
        if context is None:
            context = {}
        super(report_payment_wizard,self).__init__(cr,uid,name, context=context)
        self.localcontext.update({
            'get_data_letras':self._get_data_letras,
            'selection_value':self._selection_value,
            'get_data_period_expiration':self._get_data_period_expiration,
            })
        self.context = context

    def _get_data_letras(self):
        wizard_obj=self.pool.get('wizard.report.payment')
        wizard_data=wizard_obj.browse(self.cr,self.uid,self.ids)

        sql_where = ""
        
        if wizard_data.partner_id:
            sql_where = "WHERE date_expiration >= '%s' AND date_expiration <= '%s' AND partner_id = %s" % (wizard_data.date_inicio, wizard_data.date_fin, wizard_data.partner_id.id)
        else:
            sql_where = "WHERE date_expiration >= '%s' AND date_expiration <= '%s'" % (wizard_data.date_inicio, wizard_data.date_fin)

        query = """
          SELECT 
            *
          FROM report_payment 
          %s
        """ % (sql_where)

        self.cr.execute(query)
        _res = self.cr.dictfetchall()
        return _res

    def _get_data_period_expiration(self):
    	wizard_obj=self.pool.get('wizard.report.payment')
        wizard_data=wizard_obj.browse(self.cr,self.uid,self.ids)

        sql_where = ""

        if wizard_data.partner_id:
            sql_where = "WHERE date_expiration >= '%s' AND date_expiration <= '%s' AND partner_id = %s" % (wizard_data.date_inicio, wizard_data.date_fin, wizard_data.partner_id.id)
        else:
            sql_where = "WHERE date_expiration >= '%s' AND date_expiration <= '%s'" % (wizard_data.date_inicio, wizard_data.date_fin)

        query = """
          SELECT 
            DISTINCT period_expiration
          FROM report_payment 
          %s 
          ORDER BY period_expiration asc 
        """ % (sql_where)

        self.cr.execute(query)
        _res = self.cr.dictfetchall()
        return _res



    def _selection_value(self, model, name, value):
        if value:
            field = self.pool.get(model)._fields[name]
            env = api.Environment(self.cr, self.uid, self.localcontext)
            val = dict(field.get_description(env)['selection'])[value]
            return self._translate(val)
        return ''

class report_payment(osv.AbstractModel):
    _name="report.takana_payment.report_payment"
    _inherit="report.abstract_report"
    _template="takana_payment.report_payment"
    _wrapped_report_class=report_payment_wizard