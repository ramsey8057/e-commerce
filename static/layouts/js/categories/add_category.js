/*jshint esversion: 6 */

$(() => {

    'use strict';

    // hide placeholder on form focus
    $('[placeholder]').focus(() => {

        $(this).attr('data-text', $(this).attr('placeholder'));
        $(this).attr('placeholder', '');

    }).blur(() => {

        $(this).attr('placeholder', $(this).attr('data-text'));

    });

});
