giga.define('website_hr_recruitment.tour', function(require) {
    'use strict';

    var tour = require("web_tour.tour");

    tour.register('website_hr_recruitment_tour', {
        test: true,
        url: '/jobs',
    }, [{
        content: "Select Job",
        trigger: ".oe_website_jobs h3 span:contains('A Test Job')"
    }, {
        content: "Apply",
        trigger: ".js_hr_recruitment a:contains('Apply')"
    }, {
        content: "Complete name",
        trigger: "input[name=partner_name]",
        run: "text John Smith"
    }, {
        content: "Complete Email",
        trigger: "input[name=email_from]",
        run: "text john@smith.com"
    }, {
        content: "Complete phone number",
        trigger: "input[name=partner_phone]",
        run: "text 118.218"
    }, {
        content: "Complete Subject",
        trigger: "textarea[name=description]",
        run: "text ### HR RECRUITMENT TEST DATA ###"
    }, { // TODO: Upload a file ?
        content: "Send the form",
        trigger: ".s_website_form_send"
    }, {
        content: "Check the form is submited without errors",
        trigger: ".oe_structure:has(h1:contains('Congratulations'))"
    }]);

    return {};
});
