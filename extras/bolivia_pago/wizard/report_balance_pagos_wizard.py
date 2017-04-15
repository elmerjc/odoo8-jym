import datetime
from datetime import date
import calendar
import pytz
from openerp import tools, api
from openerp.osv import osv, orm, fields
from openerp.tools.translate import _

class wizard_report_balance_pagos(osv.osv_memory):
    _name = 'wizard.report.balance.pagos'
    _description = 'Reporte del balance de pagos'
    _columns = {
        'date_inicio': fields.date('Desde', required=True),
        'date_fin': fields.date('Hasta', required=True),
        'partner_id': fields.many2one('res.partner', string='Cliente', change_default=True),
    }

    _defaults = {
        'date_inicio': date(date.today().year,1,1),
        'date_fin': datetime.datetime.now(pytz.timezone('America/Lima')),
    }

    def print_report(self,cr,uid,ids,context=None):
        report_data = self.browse(cr,uid,ids,context)
        if report_data.date_inicio > report_data.date_fin:
            raise orm.except_orm(_('Error en la seleccion de fechas'),_('La fecha inicio %s no puede ser mayor a la fecha fin %s') % (report_data.date_inicio,report_data.date_fin))
        data = {
            'date_inicio':report_data.date_inicio,
            'date_fin': report_data.date_fin,
            'partner_id': report_data.partner_id.id,
            }
        return self.pool['report'].get_action(cr,uid,[],'bolivia_pago.report_balance_pagos',data=data,context=context)