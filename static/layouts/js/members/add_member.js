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

    // convert password to textfield on click
    const passField = $('.password');
    let visible = false;

    $('.show-password').click(() => {

        if(visible) {

             passField.attr('type', 'text');
            $('.show-password').attr('class', 'show-password fa fa-eye-slash fa-2x');
            visible = false;

        } else {

            passField.attr('type', 'password');
            $('.show-password').attr('class', 'show-password fa fa-eye fa-2x');
            visible = true;

        }

    });

});
