# -*- coding: utf-8 -*-
# Part of Giga Source ERP. See LICENSE file for full copyright and licensing details.

from giga import models
from giga.addons.l10n_be_hr_payroll.models.hr_dmfa import format_amount


class HrDMFAReport(models.Model):
    _inherit = 'l10n_be.dmfa'

    def _get_rendering_data(self):
        return dict(
            super()._get_rendering_data(),
            group_insurance_cotisation=format_amount(self._get_group_insurance_contribution()),
        )

    def _get_group_insurance_contribution(self):
        regular_payslip = self.env.ref('l10n_be_hr_payroll.hr_payroll_structure_cp200_employee_salary')
        payslips_sudo = self.env['hr.payslip'].sudo().search([
            ('date_to', '>=', self.quarter_start),
            ('date_to', '<=', self.quarter_end),
            ('state', 'in', ['done', 'paid']),
            ('struct_id', '=', regular_payslip.id),
            ('company_id', '=', self.company_id.id),
        ])
        onss_amount = payslips_sudo._get_line_values(
            ['GROUPINSURANCE'], compute_sum=True
        )['GROUPINSURANCE']['sum']['total']
        return round(onss_amount, 2)

    def _get_global_contribution(self, employees_infos, double_onss):
        # https://www.socialsecurity.be/employer/instructions/dmfa/fr/latest/instructions/special_contributions/extralegal_pensions.html#h24
        # En DMFA, la cotisation sur les avantages extra-légaux se déclare globalement par catégorie
        # d’employeur dans le bloc 90002 « cotisation non liée à une personne physique» sous les codes
        # travailleur 864, 865 ou 866 selon le cas.

        # 864 : pour les versements effectués directement au travailleur pensionné ou à ses ayants
        #       droit
        # 865 : pour les versements destinés au financement d'une pension complémentaire dans le cadre
        #       d'un plan d'entreprise
        # 866 : pour les versements destinés au financement d'une pension complémentaire dans le cadre
        #       d'un plan sectoriel
        # ! à partir du 1/2014, cotisation 866 déclarée uniquement par l'organisateur du régime
        #   sectoriel (catégorie X99)
        # Jusqu'au 3ème trimestre 2011 inclus, le code travailleur 851 était d'application mais il
        # n'est plus autorisé pour les trimestres ultérieurs.

        # La base de calcul qui correspond à la somme des avantages octroyés pour l’entreprise par
        # type de versement doit être mentionnée.

        # Lorsque la DMFA est introduite via le web, la base de calcul de cette cotisation doit être
        # mentionnée dans les cotisations dues pour l’ensemble de l’entreprise et la cotisation est
        # calculée automatiquement.
        amount = super()._get_global_contribution(employees_infos, double_onss)
        return amount + self._get_group_insurance_contribution()
