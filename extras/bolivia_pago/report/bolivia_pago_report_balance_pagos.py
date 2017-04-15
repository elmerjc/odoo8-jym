# -*- encoding: utf-8 -*-

from openerp.report import report_sxw
from openerp.osv import osv

class report_balance_pagos_wizard(report_sxw.rml_parse):
    def __init__(self,cr,uid,name,context=None):
        if context is None:
            context = {}
        super(report_balance_pagos_wizard,self).__init__(cr,uid,name, context=context)
        self.localcontext.update({
            'get_data_balance_pagos':self._get_data_balance_pagos,
            })
        self.context = context

    def _get_data_balance_pagos(self):
        wizard_obj=self.pool.get('wizard.report.balance.pagos')
        wizard_data=wizard_obj.browse(self.cr,self.uid,self.ids)

        filter_partner = ''

        if wizard_data.partner_id:
            filter_partner = 'AND rp.id = %s' % (wizard_data.partner_id.id)

        query = """
            SELECT 
            rp.name AS cliente,
            bp.sale_name AS pedido,
            bp.sale_total AS debe,
            SUM(bp.amount) AS haber
            FROM bolivia_pago bp
            INNER JOIN res_partner rp ON bp.partner_id = rp.id
            INNER JOIN sale_order so ON bp.sale_id = so.id
            WHERE so.date_order >= '%s' AND so.date_order <= '%s' %s
            GROUP BY bp.metodo, bp.sale_name, bp.sale_total, rp.name
        """ % (wizard_data.date_inicio, wizard_data.date_fin, filter_partner)

        self.cr.execute(query)
        _res = self.cr.dictfetchall()
        return _res

class report_balance_pagos(osv.AbstractModel):
    _name="report.bolivia_pago.report_balance_pagos"
    _inherit="report.abstract_report"
    _template="bolivia_pago.report_balance_pagos"
    _wrapped_report_class=report_balance_pagos_wizard
    
    
