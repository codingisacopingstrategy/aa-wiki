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
    AA.$.help.accordion({
        autoHeight: false,
        collapsible: true
    });

    AA.$.accordion.accordion({fillSpace: true});

    AA.$.body.layout({
        applyDefaultStyles: false,
        enableCursorHotkey: false,
        west: {
            size: "220",
            fxName: "none",
            fxSpeed: "fast",
            initClosed: false,
            enableCursorHotkey: false,
            slidable: false,
            closable: true,
            resizable: false,
            togglerAlign_closed : 5,
            togglerAlign_open : 5,
            togglerContent_open: '&times;',
            togglerContent_closed: '+',
            spacing_closed: 13,
            spacing_open: 13,
            togglerLength_open: 9,
            togglerLength_closed: 9,
            showOverflowOnHover: false,
            onresize: function () {
                AA.$.accordion.accordion('resize');
            }
        },
    });

    AA.$.accordion.accordion('resize');
});
