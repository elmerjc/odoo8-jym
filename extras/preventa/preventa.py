# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 S&C ().
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

from openerp import SUPERUSER_ID
from openerp import tools
from openerp import api
from openerp.osv import osv, fields, expression
from openerp.tools.translate import _
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT

from datetime import datetime
from dateutil import parser

class preventa_responsable(osv.osv):
    _name = "preventa.responsable"
    _description = "Responsables de ejecutar las visitas tecnicas"
    _columns = {
        'name': fields.char('Responsable', required=True),
        'celular': fields.char('Celular', required=True),
    }
    _order = 'name'

class preventa_visita(osv.osv):
    _name = 'preventa.visita'
    _description = 'Visitas Tecnicas'


    _columns = {
        'name': fields.char('Numero de Visita', required=True, copy=False, readonly=True, select=True),
        'state': fields.selection([
            ('pending', 'Pendiente'),
            ('cancel', 'Cancelado'),
            ('done', 'Realizado'),
            ], 'Estado', readonly=True, copy=False, help="Estado de la visita tecnica", select=True),
        'date': fields.datetime('Fecha', required=True, readonly=True, select=True, states={'pending': [('readonly', False)]}, copy=False),
        'date_confirm': fields.datetime('Fecha de confirmacion', readonly=True, select=True, help="Fecha de confirmacion de la instalacion.", copy=False),
        'responsable_id': fields.many2one('preventa.responsable', 'Responsable', required=True),
        'user_id': fields.many2one('res.users', 'Vendedor', states={'pending': [('readonly', False)]}, select=True, track_visibility='onchange'),
        'partner_id': fields.many2one('res.partner', 'Cliente', readonly=True, states={'pending': [('readonly', False)]}, required=True, change_default=True, select=True, track_visibility='always'),
        'partner_address': fields.char('Coordenadas', related='partner_id.street2', readonly=True, store=True),
        'note': fields.text('Observaciones'),
        'referencia': fields.char('Proforma'),
    }

    _defaults = {
        'date': fields.datetime.now,
        'date_confirm': fields.datetime.now,
        'state': 'pending',
        'user_id': lambda obj, cr, uid, context: uid,
        'name': lambda obj, cr, uid, context: '-',
    }
    _sql_constraints = [
        ('name_uniq', 'unique(name, id)', 'Una visita es unica'),
    ]
    _order = 'date desc, id desc'

    def create(self, cr, uid, vals, context=None):
        if context is None:
            context = {}
        vals['name'] = self.pool.get('ir.sequence').get(cr, uid, 'preventa.visita')
        return super(preventa_visita, self).create(cr, uid, vals, context=context)

    def action_pendiente(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'pending'})
        return True

    def action_cancel(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'cancel'})
        return True

    def action_done(self, cr, uid, ids, context=None):
    	self.write(cr, uid, ids, {'date_confirm': datetime.now()})
        self.write(cr, uid, ids, {'state': 'done'})
        return True