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
from openerp.osv import fields, osv
from openerp.tools.sql import drop_view_if_exists

class padron_list(osv.osv):
    _name = "padron.list"
    _description = "Lista de miembros del sindicato"
    _auto = False
    _order = "apellidos"
    _columns = {
        'id': fields.integer('Padron ID', readonly=True),
        'registro': fields.char('Registro', readonly=True),
        'nombre': fields.char('Nombre', readonly=True),
        'apellidos': fields.char('Apellidos', readonly=True),
        'dni': fields.char('DNI', readonly=True),
        'lugar_trabajo': fields.selection([('TOQUEPALA', 'TOQUEPALA'), ('CUAJONE', 'CUAJONE'), ('ILO', 'ILO')], 'Lugar de trabajo', readonly=True, select=True),
        'tipo_trabajador': fields.selection([('empleado', 'Empleado'), ('obrero', 'Obrero')], 'Tipo de trabajador', readonly=True, select=True),
    }

    def init(self, cr):
        drop_view_if_exists(cr, 'padron_list')
        cr.execute("""
            create or replace view padron_list as (
            select
                p.id as id,
                p.id as padron_id,
                p.registro as registro,
                p.dni as dni,
                p.nombre as nombre,
                p.apellidos as apellidos,
                p.lugar_trabajo as lugar_trabajo,
                p.tipo_trabajador,
                p.estado
            from
                padron_padron p
            )""")

    def get_all_miembros(self):
        self._cr.execute("select * from padron_list where estado = 'activo'")
        _res = self._cr.dictfetchall()
        return _res

class padron_report(osv.osv):
    _name = "padron.report"
    _description = "Trabajadores afiliados"
    _auto = False
    _order = "apellidos"
    _columns = {
        'id': fields.integer('Padron ID', readonly=True),
        'registro': fields.char('Registro', readonly=True),
        'name': fields.char('Trabajador', readonly=True),
        'nombre': fields.char('Nombre', readonly=True),
        'apellidos': fields.char('Apellidos', readonly=True),
        'dni': fields.char('DNI', readonly=True),
        'edad': fields.integer('Edad', readonly=True),
        'email': fields.char('Correo electronico', readonly=True),
        'grado_instruccion': fields.selection([
            ('PRIMARIA', 'PRIMARIA'), 
            ('SECUNDARIA', 'SECUNDARIA'), 
            ('TECNICOSUPERIOR', 'TECNICO SUPERIOR '), 
            ('SUPERIOR', 'SUPERIOR'), 
            ('POSTGRADO', 'POSTGRADO')
            ], 'Grado de Instruccion', readonly=True, select=True),
        'sistema_pension': fields.selection([('AFP', 'AFP'), ('ONP', 'ONP')], 'Sistema de pensión', readonly=True, select=True),
        'lugar_trabajo': fields.selection([('TOQUEPALA', 'TOQUEPALA'), ('CUAJONE', 'CUAJONE'), ('ILO', 'ILO')], 'Lugar de trabajo', readonly=True, select=True),
        'tipo_trabajador': fields.selection([('empleado', 'Empleado'), ('obrero', 'Obrero')], 'Tipo de trabajador', readonly=True, select=True),
        'estado': fields.selection([
            ('retirado', 'Retirado'),
            ('activo', 'Activo'),
            ('finalizado', 'Finalizado'),
            ], 'Estado', readonly=True, select=True),
    }

    def init(self, cr):
        drop_view_if_exists(cr, 'padron_report')
        cr.execute("""
            create or replace view padron_report as (
            select
                p.id as id,
                p.id as padron_id,
                p.registro as registro,
                p.dni as dni,
                p.edad,
                p.nombre as nombre,
                p.apellidos as apellidos,
                p.name,
                p.email,
                p.lugar_trabajo as lugar_trabajo,
                p.tipo_trabajador,
                p.grado_instruccion,
                p.sistema_pension,
                p.estado
            from
                padron_padron p
            )""")

    def get_all_miembros(self):
        self._cr.execute("select * from padron_report")
        _res = self._cr.dictfetchall()
        return _res