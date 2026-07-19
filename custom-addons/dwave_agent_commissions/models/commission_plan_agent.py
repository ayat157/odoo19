# -*- coding: utf-8 -*-
from odoo import Command, models, fields, exceptions, _, api


class CommissionPlanAgent(models.Model):
    _name = 'sale.commission.plan.agent'
    _description = 'Commission Plan Agent'
    _order = 'id'

    plan_id = fields.Many2one('sale.commission.plan', required=True, ondelete='cascade')
    agent_id = fields.Many2one(
        'res.partner',
        "Agent",
        required=True,
        domain="[('agent', '=', True)]"
    )
    date_from = fields.Date(
        "From",
        compute='_compute_date_from',
        store=True,
        readonly=False
    )
    date_to = fields.Date("To")
    other_plans = fields.Many2many(
        'sale.commission.plan',
        string="Other Plans",
        compute='_compute_other_plans',
    )

    _sql_constraints = [
        ('agent_uniq', 'unique (plan_id, agent_id)',
         "The agent is already present in the plan"),
    ]

    @api.constrains('date_from', 'date_to')
    def _date_constraint(self):
        for agent in self:
            if agent.date_to and agent.date_from and agent.date_to < agent.date_from:
                raise exceptions.ValidationError(_("Start date must be before end date"))
            if agent.date_from and agent.plan_id.date_from and agent.date_from < agent.plan_id.date_from:
                raise exceptions.ValidationError(_("Agent period cannot start before the plan starts"))
            if agent.date_to and agent.plan_id.date_to and agent.date_to > agent.plan_id.date_to:
                raise exceptions.ValidationError(_("Agent period cannot end after the plan ends"))

    @api.depends('agent_id', 'plan_id.date_from', 'plan_id.date_to', 'date_from', 'date_to')
    def _compute_other_plans(self):
        for agent in self:
            if not agent.agent_id:
                agent.other_plans = [Command.clear()]
                continue

            overlapping = self.search([
                ('agent_id', '=', agent.agent_id.id),
                ('plan_id', '!=', agent.plan_id.id),
                ('plan_id.state', 'in', ['draft', 'approved']),
            ])
            agent.other_plans = [Command.set(overlapping.mapped('plan_id').ids)]

    @api.depends('plan_id')
    def _compute_date_from(self):
        today = fields.Date.today()
        for agent in self:
            if agent.date_from:
                continue
            if not agent.plan_id.date_from:
                continue
            if agent.plan_id.state != 'draft':
                agent.date_from = max(agent.plan_id.date_from, today)
            else:
                agent.date_from = agent.plan_id.date_from
