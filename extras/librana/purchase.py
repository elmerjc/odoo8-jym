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

from openerp.osv import fields,osv

class purchase_order(osv.osv):
    _name = 'purchase.order'
    _inherit = 'purchase.order'
    
    _columns = {
    	'codigo_cliente': fields.char('Codigo Cliente', related='partner_id.codigo_cliente', readonly=True, store=True),
    	'chofer_id': fields.many2one('librana.chofer', 'Chofer', required=True),
    	'chofer_brevete': fields.char('Brevete', related='chofer_id.brevete', readonly=True, store=True),
        'vehiculo_id': fields.many2one('librana.vehiculo', 'Vehiculo', required=True),
    }