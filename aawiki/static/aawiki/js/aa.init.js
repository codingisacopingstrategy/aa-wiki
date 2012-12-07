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
    AA.$.canvas.bind("refresh", function (evt) {
        /* Draggable + resizable Sections {{{ */
        $("section.section1", AA.$.canvas).bind('mousedown', function(e) {
            e.stopPropagation(); 
        }).draggable({
            cancel: 'span.edit',
            scroll: true,
            handle: 'h1',
            delay: 200,  // NOTE: Prevents unwanted saves 
            stop: function () { 
                AA.fn.constraintAnnotation(this);
                $(this).trigger('geometrychange');
            }
        }).resizable({
            stop: function () { 
                $(this).trigger('geometrychange');
             }
        });
        /* }}} */

        AA.fn.renumberSections();

        // Section edit {{{ */
        // Create & insert edit links in every section's Header that trigger the section's "edit" event
        AA.$.canvas.ffind('section').each(
            AA.fn.decorateSection
        ).bind("geometrychange", function (event) {
            event.stopPropagation();
            if (! $('body').hasClass('locked')) {
                // Prevents anonymous users from recording the changes
                // Prevents recording changes on old revisions
                commit_attributes(this);
            }
        }).bind("edit", AA.fn.editSection
        ).droppable({
            greedy: true,
            accept: ".swatch",
            hoverClass: "drophover",
            drop: function (event, ui) {
                var $select = $(ui.helper).find('select');
                var key = $select.attr("id");
                var value = $select.find('option:selected').val();
                var section = $(this).closest(".section1, .section2");
                section.css(key, value);
                section.trigger('geometrychange');
            }
        });
        /* }}} */

        $("section.section1 > div.wrapper", AA.$.canvas).autoscrollable();
    });

    $canvas.trigger("refresh");
});


/* vim: set foldmethod=indent: */
