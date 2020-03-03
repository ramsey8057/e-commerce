/*jshint esversion: 6 */

$(() => {
    'use strict';

    $('.toggle-info').click(function() {

        $(this).toggleClass('selected').parent().next('.panel-body').fadeToggle(100);

        if($(this).hasClass('selected')) {

            $(this).html('<i class="fa fa-minus"></i>');

        } else {

            $(this).html('<i class="fa fa-plus"></i>');

        }

    });

});
