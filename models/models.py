# -*- coding: utf-8 -*-

from odoo import models, fields, api


class CreditoCliente(models.Model):
    _inherit = 'res.partner'

    select_credito = [('contado', 'De Contado'),
                    ('bien', 'Bien'),
                    ('suspendido', 'Suspendido'),
                    ('auditar', 'Auditar'),
                    ('pendiente', 'Pendiente'),
                    ('legal', 'Legal'),
                    ]
    estado_credito = fields.Selection(select_credito, 'Estado del crédito') # ESTADO DEL CREDITO EN CLIENTES

    # INFORMACION DE CREDITO
    credito_limite = fields.Float('Crédito limite')
    credito_disponible = fields.Float('Crédito disponible')
    estrategico = fields.Boolean('Es estrategico')

    vencida = fields.Boolean('Esta vencido') # INDICA SI HAY FACTURAS VENCIDAS

    dia_gracia_pago = fields.Float('Días de gracia para pagar') # DIAS DE GRACIA

    select_color = [('verde', 'Verde'),
                      ('amarillo', 'Amarillo'),
                      ('rojo', 'Rojo')
                      ]
    estado_color = fields.Selection(select_color,'Estado del credito color') # ESTADO DE COLOR


    def abrir_vencimientos(self):
        print(' VENCIMIENTOS ')



class PresupuestoExtended(models.Model):
    _inherit = 'sale.order'

    credito_limite = fields.Float('Crédito limite', related="partner_id.credito_limite")
    credito_disponible = fields.Float('Crédito disponible', related="partner_id.credito_disponible")
    vencida = fields.Boolean('Esta vencido', related="partner_id.vencida")  # INDICA SI HAY FACTURAS VENCIDAS

    select_credito = [('contado', 'De Contado'),
                      ('bien', 'Bien'),
                      ('suspendido', 'Suspendido'),
                      ('auditar', 'Auditar'),
                      ('pendiente', 'Pendiente'),
                      ('legal', 'Legal'),
                      ]
    estado_credito = fields.Selection(select_credito, 'Estado del crédito', related="partner_id.estado_credito")  # ESTADO DEL CREDITO EN CLIENTES

    select_color = [('verde', 'Verde'),
                    ('amarillo', 'Amarillo'),
                    ('rojo', 'Rojo')
                    ]
    estado_color = fields.Selection(select_color, 'Estado del credito color', related="partner_id.estado_color")