# -*- coding: utf-8 -*-

from odoo import models, fields, api, tools, _
from odoo.exceptions import AccessError, UserError, ValidationError
import odoo.addons
from datetime import timedelta, date


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
    credito_disponible = fields.Float('Crédito disponible', store=True)

    @api.onchange('credito_limite')
    def credito_onchange(self):
        # ACTUALIZA EL CREDITO DISPONIBLE SI SE MODIFICA EL CREDITO LIMITE
        # ---*---
        # BUSCAR LAS COTIZACIONES VIGENTES
        search_presupuestos = self.env['sale.order'].search([('partner_id', '=', self._origin.id),('state', '=', 'sale')])
        credito = 0
        for i in search_presupuestos:
            print(i.amount_total, i.state)
            credito += i.amount_total
        # SE RESTA EL CREDITO LIMITE CON LA SUMATORIA DEL MONTO DE LAS COTIZACIONES VIGENTES
        self.credito_disponible = self.credito_limite - credito

    estrategico = fields.Boolean('Es estrategico')

    vencida = fields.Boolean('Esta vencido') # INDICA SI HAY FACTURAS VENCIDAS

    dia_gracia_pago = fields.Float('Días de gracia para pagar') # DIAS DE GRACIA

    select_color = [('verde', 'Verde'),
                      ('amarillo', 'Amarillo'),
                      ('rojo', 'Rojo')
                      ]
    estado_color = fields.Selection(select_color,'Estado del credito color') # ESTADO DE COLOR

    def action_partner_suspend(self):
        print('hola')
        fecha_vencimiento_dias_gracia = ''
        buscar_factura = self.env['account.move'].search([('state', '=', 'posted')])
        Date_req = date.today()
        print(Date_req)
        for i in buscar_factura:
            if i.invoice_date_due is False:
                pass
            else:
                fecha_vencimiento_dias_gracia = i.invoice_date_due + timedelta(days=int(i.partner_id.dia_gracia_pago))
                print(i.partner_id.dia_gracia_pago, fecha_vencimiento_dias_gracia, ' FECHA ' ) # ' fecha de vencimiento se le sumaran los dias de gracias para detectar si el cliente  deberia ser suspendido'
                if Date_req > fecha_vencimiento_dias_gracia:
                    print('CAMBIAR ESTADO A SUSPENDIDO')

    def action_partner_audit(self):
        print('holax2')

    '''def abrir_vencimientos(self): # VENTANA QUE ABRE EL BOTON INTELIGENTE VENCIMIENTO
        print(' VENCIMIENTOS ')
        # form = self.env.ref('supervision_obra.concepto_ruta_critica_form')
        return {
            'type': 'ir.actions.act_window',
            'name': 'Vencimiento',
            'res_model': 'res.partner',
            'view_mode': 'form',
            'target': 'current',
            # 'domain': [],
            'view_id': 211,
            # 'context': {},
            # 'views': [ (form.id, 'form'), ],
            # 'res_id': search.id,  # (view.id, 'form')
        }'''


class SaleOrder(models.Model):
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

    # ESTE METODO SE ACTIVA CON EL BOTON CONFIRMAR EN EL PRESUPUESTO
    def action_confirm(self):
        if self.amount_total > self.credito_disponible:
            print('NO HAY CREDITO DISPONIBLE')
            raise UserError(_(
                'El cliente ' + self.partner_id.name + ' ha superado el límite de crédito. El crédito disponible para '
                                                       'usar es ' + str(self.credito_disponible)
            ) )
        elif self.partner_id.estado_credito == 'suspendido':
            print('EL CLIENTE TIENE UN VENCIMIENTO O ESTA SUSPENDIDO')
            raise UserError(_(
                ' El pedido de venta ' +
                self.name + ' no puede ser validado por que el estado de crédito del cliente es suspendido'
            ))
        else:

            print('SI HAY CREDITO DISPONIBLE PROSEGUIR')
            if self._get_forbidden_state_confirm() & set(self.mapped('state')):
                raise UserError(_(
                    'It is not allowed to confirm an order in the following states: %s'
                ) % (', '.join(self._get_forbidden_state_confirm())))

            for order in self.filtered(lambda order: order.partner_id not in order.message_partner_ids):
                order.message_subscribe([order.partner_id.id])
            self.write(self._prepare_confirmation_values())

            # Context key 'default_name' is sometimes propagated up to here.
            # We don't need it and it creates issues in the creation of linked records.
            context = self._context.copy()
            context.pop('default_name', None)

            self.with_context(context)._action_confirm()
            if self.env.user.has_group('sale.group_auto_done_setting'):
                self.action_done()
            return True

    @api.model
    def create(self, vals):
        partner = self.env['res.partner'].browse(vals.get('partner_id'))
        # EXEPCION SI EL ESTADO DEL CLIENTE ES LEGAL NO SE PUEDE PROSEGUIR CREANDO LA COTIZACION
        if partner.estado_credito == 'legal':
            # print('EL ESTADO DEL CLIENTE ES LEGAL')
            raise UserError(_(
                ' Advertencia el estado crediticio del cliente es legal '
            ))
        else:
            # SI NO, PROSIGUE CON EL CODIGO NATIVO DE ODOO
            if 'company_id' in vals:
                self = self.with_company(vals['company_id'])
            if vals.get('name', _('New')) == _('New'):
                seq_date = None
                if 'date_order' in vals:
                    seq_date = fields.Datetime.context_timestamp(self, fields.Datetime.to_datetime(vals['date_order']))
                vals['name'] = self.env['ir.sequence'].next_by_code('sale.order', sequence_date=seq_date) or _('New')

            # Makes sure partner_invoice_id', 'partner_shipping_id' and 'pricelist_id' are defined
            if any(f not in vals for f in ['partner_invoice_id', 'partner_shipping_id', 'pricelist_id']):
                # partner = self.env['res.partner'].browse(vals.get('partner_id'))
                addr = partner.address_get(['delivery', 'invoice'])
                vals['partner_invoice_id'] = vals.setdefault('partner_invoice_id', addr['invoice'])
                vals['partner_shipping_id'] = vals.setdefault('partner_shipping_id', addr['delivery'])
                vals['pricelist_id'] = vals.setdefault('pricelist_id', partner.property_product_pricelist.id)
            result = super(SaleOrder, self).create(vals)

            return result

    def action_confirm(self):
        if self._get_forbidden_state_confirm() & set(self.mapped('state')):
            raise UserError(_(
                'It is not allowed to confirm an order in the following states: %s'
            ) % (', '.join(self._get_forbidden_state_confirm())))

        for order in self.filtered(lambda order: order.partner_id not in order.message_partner_ids):
            order.message_subscribe([order.partner_id.id])
        self.write(self._prepare_confirmation_values())

        # Context key 'default_name' is sometimes propagated up to here.
        # We don't need it and it creates issues in the creation of linked records.
        context = self._context.copy()
        context.pop('default_name', None)

        self.with_context(context)._action_confirm()
        if self.env.user.has_group('sale.group_auto_done_setting'):
            self.action_done()

        # ---*---
        # ACTUALIZAR MONTO DEL CREDITO DISPONIBLE CUANDO SE CONFIRMA LA COTIZACION
        datos_credito = {
            'credito_disponible': self.partner_id.credito_disponible - self.amount_total,
        }
        r = self.partner_id.write(datos_credito)
        return True

    def action_cancel(self):
        cancel_warning = self._show_cancel_wizard()
        if cancel_warning:
            return {
                'name': _('Cancel Sales Order'),
                'view_mode': 'form',
                'res_model': 'sale.order.cancel',
                'view_id': self.env.ref('sale.sale_order_cancel_view_form').id,
                'type': 'ir.actions.act_window',
                'context': {'default_order_id': self.id},
                'target': 'new'
            }
        inv = self.invoice_ids.filtered(lambda inv: inv.state == 'draft')
        inv.button_cancel()

        # ---*---
        # ACTUALIZAR MONTO DEL CREDITO DISPONIBLE CUANDO SE CANCELA LA COTIZACION
        datos_credito = {
            'credito_disponible': self.partner_id.credito_disponible + self.amount_total,
        }
        r = self.partner_id.write(datos_credito)
        return self.write({'state': 'cancel'})


    '''elif self.partner_id.property_payment_term_id == 'Pago inmediato' and self.payment_term_id != 'Pago inmediato' \
        or self.partner_id.estado_credito == 'contado' and self.payment_term_id != 'Pago inmediato':
    print('EL CLIENTE TIENE ASIGNADO PAGO INMEDIATO PERO EN EL PRESUPUESTO SE SELECCIONO UN PLAZO DE PAGO ')
    raise UserError(_(
        ' El cliente ' + self.partner_id.name + ' no tiene crédito. Para confirmar la nueva orden de venta el plazo de pago debe ser al contado inmediato'
    ))'''