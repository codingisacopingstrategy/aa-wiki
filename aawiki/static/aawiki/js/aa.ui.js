/**
 * This file is part of Active Archives.
 * Copyright 2006-2012 the Active Archives contributors (see AUTHORS)
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU Affero General Public License as
 * published by the Free Software Foundation, either version 3 of the
 * License, or (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU Affero General Public License for more details.
 *
 * You should have received a copy of the GNU Affero General Public License
 * along with this program.  If not, see <http://www.gnu.org/licenses/>.
 * Also add information on how to contact you by electronic and paper mail.
 */


$(function() {
    AA.$.center.layout({
        applyDefaultStyles: false,
        enableCursorHotkey: false,
        slidable: false,
        resizable: false,
        closable: false,
        north: {
            fxName: "none",
            enableCursorHotkey: false,
            togglerAlign_closed : 5,
            togglerAlign_open : 5,
            togglerAlign_closed : 'right',
            togglerAlign_open : 'right',
            togglerContent_open: '&times',
            togglerContent_closed: '+',
            spacing_closed: 13,
            spacing_open: 13,
            togglerLength_open: 13,
            togglerLength_closed: 13,
            showOverflowOnHover: false
        },
        south: {
            size: "250",
            fxName: "none",
            fxSpeed: "fast",
            initClosed: true,
            enableCursorHotkey: false,
            slidable: true,
            closable: true,
            resizable: true,
            togglerAlign_closed : 5,
            togglerAlign_open : 5,
            togglerAlign_closed : 'right',
            togglerAlign_open : 'right',
            togglerContent_open: '&times',
            togglerContent_closed: '+',
            spacing_closed: 13,
            spacing_open: 13,
            togglerLength_open: 13,
            togglerLength_closed: 13,
            showOverflowOnHover: false
        }
    });

    $("body").not('.locked').find('#tab-help').accordion({
        autoHeight: false,
        collapsible: true
    });

    $('#tab-layers').aalayers({
        selector: 'section.section1',
        post_reorder: function(event, ui, settings) {
            var $this = settings.$container;
            $this.find('li')
                .reverse()
                .each(function(i) {
                    $($(this).find('label a').attr('href'))
                        .css('z-index', i)
                        .trigger('geometrychange');
                });
        },
        post_toggle: function(event, settings, target) {
            target.toggle().trigger('geometrychange');
        }
    });

    $("#tab-styles span.swatch").each(function () {
        $(this).draggable({
            helper: function () {
                /* Fixes the the clone select value being reset */
                var $this = $(this),
                    $clone = $this.clone();

                $clone.find('select').first().val($this.find('select').first().val());
                return $clone.appendTo("body");
            }
        });
    });

    $('#tab-layers a[href^="#"]').live('click', function() {
        var $target,
            offset;
    
        $target = $($(this).attr('href'));

        if (! $target.parents("#canvas").length) {
            return true;
        }

        offset = $target.position();
        
        $canvas.animate({
            scrollTop: $canvas.scrollTop() + offset.top - 20,
            scrollLeft: $canvas.scrollLeft() + offset.left - 20
        }, 1000);

        $target.removeClass('collapsed');
        return false;
    });
});

/* vim: set foldmethod=indent: */
