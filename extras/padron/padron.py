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
import math
import re
import time

from openerp import SUPERUSER_ID
from openerp import tools
from openerp import api
from openerp.osv import osv, fields, expression
from openerp.tools.translate import _
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
import psycopg2
from datetime import datetime
from dateutil import parser

from openerp.tools.float_utils import float_round, float_compare

class trabajo_departamento(osv.osv):
    _name = "trabajo.departamento"
    _description = "Area de trabajo"
    _columns = {
        'name': fields.char('Departamento', required=True),
    }
    _order = 'name'

class trabajo_seccion(osv.osv):
    _name = "trabajo.seccion"
    _description = "Seccion de trabajo"
    _columns = {
        'departamento_id': fields.many2one('trabajo.departamento', 'Departamento', required=True),
        'lugar_trabajo': fields.selection([('TOQUEPALA', 'TOQUEPALA'), ('CUAJONE', 'CUAJONE'), ('ILO', 'ILO')], 'Lugar de trabajo', required=True),
        'name': fields.char('Seccion', required=True),
    }
    _order = 'name'
    _defaults = {
        'lugar_trabajo': 'TOQUEPALA',
    }

class padron_padron(osv.osv):
    _name = 'padron.padron'
    _description = 'Padron de miembros'
    _order = 'name,apellidos'
    def _get_image(self, cr, uid, ids, name, args, context=None):
        result = dict.fromkeys(ids, False)
        for obj in self.browse(cr, uid, ids, context=context):
            result[obj.id] = tools.image_get_resized_images(obj.image, avoid_resize_medium=True)
        return result

    def _set_image(self, cr, uid, id, name, value, args, context=None):
        return self.write(cr, uid, [id], {'image': tools.image_resize_image_big(value)}, context=context)

    _columns = {
        'name': fields.char('Nombre completo'),
        'registro': fields.char('Registro', size=5, required=True),
        'fecha_inscripcion': fields.date('Fecha de afiliacion', required=True),
        'dni': fields.char('DNI', size=8, required=True),
        'nombre': fields.char('Nombre', required=True),
        'apellidos': fields.char('Apellidos', required=True),
        'email': fields.char('Correo electronico'),
        'lugar_nac': fields.char('Lugar de nacimiento', required=True),
        'fecha_nac': fields.date('Fecha de nacimiento', required=True),
        'edad': fields.integer('Edad', compute='_compute_getedad', store=True),
        'sexo': fields.selection([('HOMBRE', 'HOMBRE'), ('MUJER', 'MUJER')], 'Sexo', required=True, default='HOMBRE'),
        'estado_civil': fields.selection([('SOLTERO', 'SOLTERO'), ('CASADO', 'CASADO'), ('DIVORCIADO', 'DIVORCIADO'), ('VIUDO', 'VIUDO')], 'Estado Civil', required=True, default='CASADO'),
        'direccion1': fields.char('Direccion campamento', required=True),
        'direccion2': fields.char('Direccion fuera del campamento'),
        'grado_instruccion': fields.selection([('PRIMARIA', 'PRIMARIA'), ('SECUNDARIA', 'SECUNDARIA'), ('TECNICOSUPERIOR', 'TECNICO SUPERIOR '), ('SUPERIOR', 'SUPERIOR'), ('POSTGRADO', 'POSTGRADO')], 'Grado de Instruccion', required=True, default='TECNICOSUPERIOR'),
        'profesion': fields.char('Profesion', required=True),
        'telefono': fields.char('Telefono'),
        'celular1': fields.char('Celular 1', required=True),
        'celular2': fields.char('Celular 2'),
        'image': fields.binary("Foto", help="Ingresar una imagen de la herramienta no superior a 1024x1024px."),
        'image_medium': fields.function(
            _get_image,
            fnct_inv=_set_image,
            string="Imagen medium", type="binary", multi="_get_image",
            store={
                'padron.padron': (lambda self, cr, uid, ids, c={}: ids, ['image'], 10),
            }
        ),
        'image_small': fields.function(
            _get_image,
            fnct_inv=_set_image,
            string="Imagen small", type="binary", multi="_get_image",
            store={
                'padron.padron': (lambda self, cr, uid, ids, c={}: ids, ['image'], 10),
            }
        ),
        'tipo_trabajador': fields.selection([('empleado', 'Empleado'), ('obrero', 'Obrero')], 'Tipo de trabajador', required=True, default='empleado'),
        'categoria_empleado': fields.char('Categoria'),
        'categoria_obrero': fields.char('Categoria'),
        'sueldo': fields.char('Sueldo'),
        'fecha_trabajo': fields.date('Fecha de ingreso a la empresa', required=True),
        'lugar_trabajo': fields.selection([('TOQUEPALA', 'TOQUEPALA'), ('CUAJONE', 'CUAJONE'), ('ILO', 'ILO')], 'Lugar de trabajo', required=True, default='CUAJONE'),
        'departamento_id': fields.many2one('trabajo.departamento','Departamento de trabajo', change_default=True, required=True),
        'seccion_id': fields.many2one('trabajo.seccion','Seccion de trabajo', change_default=True, required=True),
        'telefono_trabajo': fields.char('Telefono del trabajo'),
        'cargo': fields.char('Cargo actual', required=True),
        'comentarios': fields.text('Comentarios'),
        'sistema_pension': fields.selection([('AFP', 'AFP'), ('ONP', 'ONP')], 'Sistema de pensión', required=True, default='AFP'),
        'familia_ids': fields.one2many('padron.familia', 'miembro_id', 'Familiares'),
        'estado': fields.selection([
            ('retirado', 'Retirado'),
            ('activo', 'Activo'),
            ('finalizado', 'Finalizado'),
            ], 'Estado', readonly=True, copy=False, help="El estado de la afiliacion del miembro del sindicato.", select=True),
    }

    _defaults = {
        'fecha_inscripcion': fields.datetime.now,
        'fecha_trabajo': fields.datetime.now,
        'fecha_nac': fields.datetime.now,
        'estado': 'activo',
    }

    _sql_constraints = [
        ('uniq_name',
         'unique(name)',
         'Registro unico'),
        ('uniq_dni',
         'unique(dni)',
         'DNI unico'),
    ]

    def create(self, cr, uid, vals, context=None):
        if context is None:
            context = {}
        vals['name'] = vals['apellidos'] + " " + vals['nombre']
        return super(padron_padron, self).create(cr, uid, vals, context=context)

    def action_retirado(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'estado': 'retirado'})
        return True

    def action_activo(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'estado': 'activo'})
        return True

    def action_finalizar(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'estado': 'finalizado'})
        return True

    def onchange_nombre(self, cr, uid, ids, nombre, apellidos, context=None):
        val = {}
        if nombre and apellidos:
            val = {
                'name' : apellidos + " " + nombre
            }
        return {'value': val}

    def onchange_getage_id(self,cr,uid,ids,fecha_nac,context=None):
        current_date = datetime.now()
        current_year = current_date.year
        birth_date = parser.parse(fecha_nac)
        current_age = current_year - birth_date.year
        val = {
            'edad' : current_age
        }
        return {'value' : val}

    @api.depends('fecha_nac')
    def _compute_getedad(self):
        current_date = datetime.now()
        current_year = current_date.year
        current_month = current_date.month
        current_day = current_date.day

        birth_date = parser.parse(self.fecha_nac)
        current_age = current_year - birth_date.year

        if current_month <= birth_date.month and current_day <= birth_date.day:
             current_age += 1
        self.edad = current_age

class padron_familia(osv.osv):
    _name = 'padron.familia'
    _description = 'Familia de los miembros'
    _order = 'name'

    _columns = {
        'miembro_id': fields.many2one('padron.padron', 'ID', readonly=True, required=True),
        'name': fields.char('DNI'),
        'nombre': fields.char('Nombre', required=True),
        'apellidos': fields.char('Apellidos', required=True),
        'parentesco': fields.selection([('CONYUGE', 'CONYUGE'), ('HIJO', 'HIJO'), ('PADRE', 'PADRE'), ('MADRE','MADRE')], 'Parentesco', default='HIJO'),
        'fecha_nac': fields.date('Fecha de nacimiento', required=True),
        'edad': fields.integer('Edad', compute='_compute_getedad', readonly=True, store=True),
        'ocupacion': fields.char('Ocupacion'),
        'celular': fields.char('Celular'),
    }

    _defaults = {
        'fecha_nac': fields.datetime.now,
    }

    _sql_constraints = [
        ('uniq_name',
         'unique(name)',
         'DNI unico'),
    ]

    @api.depends('fecha_nac')
    def _compute_getedad(self):
        current_date = datetime.now()
        current_year = current_date.year
        current_month = current_date.month
        current_day = current_date.day

        birth_date = parser.parse(self.fecha_nac)
        current_age = current_year - birth_date.year

        if current_month <= birth_date.month and current_day <= birth_date.day:
             current_age += 1
        self.edad = current_age