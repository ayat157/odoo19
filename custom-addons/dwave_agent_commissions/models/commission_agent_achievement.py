# -*- coding: utf-8 -*-
from odoo import models, fields, _, api


class CommissionAgentAchievement(models.Model):
    _name = 'sale.agent.commission.achievement'
    _description = 'Manual Commission Agent Achievement'
    _order = 'id desc'

    agent_id = fields.Many2one(
        'res.partner',
        "Agent",
        domain="[('agent', '=', True)]",
        required=True
    )
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        required=True,
        readonly=False,
        default=lambda self: self.env.company
    )
    type = fields.Selection([
        ('amount_invoiced', "Amount Invoiced"),
        ('amount_sold', "Amount Sold"),
        ('qty_invoiced', "Quantity Invoiced"),
        ('qty_sold', "Quantity Sold"),
        ('amount_collected', "Amount Collected"),
        ('quantity_collected', "Quantity Collected"),
    ], required=True)
    date = fields.Date(
        "Date",
        default=fields.Date.today,
        required=True
    )
    amount = fields.Monetary(
        "Amount",
        required=True,
        currency_field='currency_id'
    )
    currency_id = fields.Many2one(
        'res.currency',
        default=lambda self: self.env.company.currency_id
    )
    currency_rate = fields.Float(
        "Currency Rate",
        compute='_compute_currency_rate',
        store=True
    )
    note = fields.Char("Note")

    def _compute_display_name(self):
        for achievement in self:
            if achievement.note:
                achievement.display_name = _("Agent Adjustment: %s") % achievement.note
            else:
                achievement.display_name = _("Adjustment #%s") % (achievement.id or '')

    @api.depends('currency_id', 'company_id', 'date')
    def _compute_currency_rate(self):
        for achievement in self:
            if not achievement.currency_id or \
               achievement.currency_id == achievement.company_id.currency_id:
                achievement.currency_rate = 1.0
            else:
                try:
                    achievement.currency_rate = achievement.currency_id._get_conversion_rate(
                        from_currency=achievement.company_id.currency_id,
                        to_currency=achievement.currency_id,
                        company=achievement.company_id,
                        date=achievement.date or fields.Date.context_today(achievement),
                    )
                except Exception:
                    achievement.currency_rate = 1.0
