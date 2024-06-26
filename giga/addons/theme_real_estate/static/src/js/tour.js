giga.define("theme_real_estate.tour.real_estate", function (require) {
"use strict";

const wTourUtils = require("website.tour_utils");
var tour = require("web_tour.tour");

const snippets = [
    {
        id: 's_banner',
        name: 'Banner',
    },
    {
        id: 's_text_block',
        name: 'Text',
    },
    {
        id: 's_text_image',
        name: 'Text - Image',
    },
    {
        id: 's_image_text',
        name: 'Image - Text',
    },
    {
        id: 's_title',
        name: 'Title',
    },
    {
        id: 's_three_columns',
        name: 'Columns',
    },
    {
        id: 's_title:last-child',
        name: 'Title',
    },
    {
        id: 's_masonry_block',
        name: 'Masonry',
    },
    {
        id: 's_numbers',
        name: 'Numbers',
    },
    {
        id: 's_quotes_carousel',
        name: 'Quotes',
    },
];

wTourUtils.registerThemeHomepageTour("real_estate_tour", [
    wTourUtils.dragNDrop(snippets[0]),
    wTourUtils.clickOnText(snippets[0], 'h1'),
    wTourUtils.goBackToBlocks(),
    wTourUtils.dragNDrop(snippets[1]),
    wTourUtils.dragNDrop(snippets[2]),
    wTourUtils.dragNDrop(snippets[3]),
    wTourUtils.dragNDrop(snippets[4]),
    wTourUtils.clickOnSnippet(snippets[4]),
    wTourUtils.changeBackgroundColor(),
    wTourUtils.selectColorPalette(),
    wTourUtils.goBackToBlocks(),
    wTourUtils.dragNDrop(snippets[5]),
    wTourUtils.dragNDrop(snippets[6]),
    wTourUtils.dragNDrop(snippets[7]),
    wTourUtils.dragNDrop(snippets[8]),
    wTourUtils.dragNDrop(snippets[9]),
]);
});
