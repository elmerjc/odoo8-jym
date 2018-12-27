# -*- encoding: utf-8 -*-

import datetime
from datetime import date
import calendar
import pytz
from openerp import tools, api
from openerp.osv import osv, orm, fields
from openerp.tools.translate import _

class report_payment_wizard(osv.osv_memory):
    _name = 'wizard.report.payment'
    _description = 'Reporte de letras de pago por proveedor'
    _columns = {
        'date_inicio': fields.date('Desde', required=True),
        'date_fin': fields.date('Hasta', required=True),
        'date_print': fields.datetime('Fecha de impresion'),
        'partner_id': fields.many2one('res.partner', 'Proveedor'),
    }

    _defaults = {
        'date_inicio': False,
        'date_fin': False,
        'date_print': fields.datetime.now(),
    }

    def print_report(self,cr,uid,ids,context=None):
        report_data = self.browse(cr,uid,ids,context)
        if report_data.date_inicio > report_data.date_fin:
            raise orm.except_orm(_('Error!'),_('La fecha inicio %s no puede ser mayor a la fecha fin %s') % (report_data.date_inicio,report_data.date_fin))
        data = {
            'date_inicio':report_data.date_inicio,
            'date_fin': report_data.date_fin,
            'partner_id': report_data.partner_id.id,
            'date_print': report_data.date_print,
            }
        return self.pool['report'].get_action(cr,uid,[],'takana_payment.report_payment',data=data,context=context)

    def view_report(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        report_data = self.read(cr, uid, ids, context=context)[0]
        ctx = context.copy()
        ctx['date_inicio'] = report_data['date_inicio']
        ctx['date_fin'] = report_data['date_fin']
        #ctx['search_default_group_by_partner_id'] = True
        return {
            'domain': "[('date_invoice', '>=', '" + report_data['date_inicio'] + "'), ('date_invoice', '<=', '" + report_data['date_fin'] + "')]",
            'name': _('Analisis de las letras de pago'),
            'view_type': 'form',
            'view_mode': 'graph',
            'res_model': 'report.payment',
            'type': 'ir.actions.act_window',
            'context': ctx,
        }