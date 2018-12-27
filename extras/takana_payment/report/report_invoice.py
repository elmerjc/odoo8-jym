# -*- encoding: utf-8 -*-
from openerp import api
from openerp.report import report_sxw
from openerp.osv import osv

class report_invoice_wizard(report_sxw.rml_parse):
    def __init__(self,cr,uid,name,context=None):
        if context is None:
            context = {}
        super(report_invoice_wizard,self).__init__(cr,uid,name, context=context)
        self.localcontext.update({
            'get_data_invoices':self._get_data_invoices,
            'get_data_guias':self._get_data_guias,
            'selection_value':self._selection_value,
            })
        self.context = context

    def _get_data_guias(self, invoice_id):
        query = """
             SELECT 
                tg.name as number_guia
              FROM takana_invoice_guia_rel tig
              JOIN takana_guia tg ON tig.guia_id = tg.id
              WHERE tig.invoice_id = %s
        """ % (invoice_id)

        self.cr.execute(query)
        _res = self.cr.dictfetchall()
        return _res

    def _get_data_invoices(self):
        wizard_obj=self.pool.get('wizard.report.invoice')
        wizard_data=wizard_obj.browse(self.cr,self.uid,self.ids)

        sql_where = ""

        if wizard_data.partner_id:
        	sql_where = "WHERE ti.date_invoice >= '%s' AND ti.date_invoice <= '%s' AND ti.partner_id = %s" % (wizard_data.date_inicio, wizard_data.date_fin, wizard_data.partner_id.id)
        else:
        	sql_where = "WHERE ti.date_invoice >= '%s' AND ti.date_invoice <= '%s'" % (wizard_data.date_inicio, wizard_data.date_fin)
        
        query = """
          SELECT
            ti.id,
            ti.name,
            ti.date_invoice,
            ti.date_expiration,
            ti.number_invoice,
            ti.partner_id,
            rp.name AS partner,
            rp.x_ruc,
            ti.currency_id,
            ti.amount_untaxed,
            ti.amount_tax,
            ti.amount_total,
            ti.payment_term,
            ti.residual,
            ti.state,
            ti.comment
          FROM takana_invoice ti
          INNER JOIN res_partner rp ON ti.partner_id = rp.id 
          %s
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

class report_invoice(osv.AbstractModel):
    _name="report.takana_payment.report_invoice"
    _inherit="report.abstract_report"
    _template="takana_payment.report_invoice"
    _wrapped_report_class=report_invoice_wizard
    
    
