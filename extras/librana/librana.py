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

class librana_chofer(osv.osv):
    _name = "librana.chofer"
    _description = "Choferes de las unidades de transporte"
    _columns = {
        'name': fields.char('Chofer', required=True),
        'brevete': fields.char('Brevete', required=True),
    }
    _order = 'name'
    _sql_constraints = [
        ('brevete_uniq', 'unique(brevete, id)', 'Brevete unico del chofer'),
    ]

class librana_vehiculo(osv.osv):
    _name = "librana.vehiculo"
    _description = "Vehiculos de transporte"
    _columns = {
        'name': fields.char('Placa del tracto', required=True),
        'tipo_contenedor': fields.selection([('cisterna', 'Cisterna'), ('carreta', 'Carreta')], 'Tipo de contenedor', default='cisterna'),
        'contenedor': fields.char('Placa del contenedor'),
        'descripcion': fields.char('Descripcion', required=True),
        'capacidad': fields.char('Capacidad'),
    }
    _order = 'name'
    _sql_constraints = [
        ('name_uniq', 'unique(name, id)', 'Placa unica del vehiculo'),
    ]

    def create(self, cr, uid, vals, context=None):
        if context is None:
            context = {}
        vals['name'] = vals['name'] + " / " + vals['contenedor']
        new_id = super(librana_vehiculo, self).create(cr, uid, vals, context=context)
        return new_id