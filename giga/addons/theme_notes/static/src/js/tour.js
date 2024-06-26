/** @giga-module */

import wTourUtils from 'website.tour_utils';

const core = require("web.core");
const _t = core._t;

const snippets = [
    {
        id: 's_carousel',
        name: 'Carousel',
    },
    {
        id: 's_masonry_block',
        name: 'Masonry',
    },
    {
        id: 's_text_image',
        name: 'Text - Image',
    },
    {
        id: 's_product_catalog',
        name: 'Pricelist',
    },
    {
        id: 's_media_list',
        name: 'Media List',
    },
    {
        id: 's_company_team',
        name: 'Team',
    },
];

wTourUtils.registerThemeHomepageTour("notes_tour", [
    wTourUtils.dragNDrop(snippets[0]),
    wTourUtils.clickOnText(snippets[0], 'h1'),
    wTourUtils.goBackToBlocks(),
    wTourUtils.dragNDrop(snippets[1]),
    wTourUtils.dragNDrop(snippets[2]),
    wTourUtils.clickOnSnippet(snippets[2]),
    wTourUtils.changeOption('ContainerWidth', 'we-button-group.o_we_user_value_widget', _t('width')),
    wTourUtils.goBackToBlocks(),
    wTourUtils.dragNDrop(snippets[3]),
    wTourUtils.dragNDrop(snippets[4]),
    wTourUtils.dragNDrop(snippets[5]),
]);
