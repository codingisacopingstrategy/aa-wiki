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
    ////////////////////////////////////////////////////////////////////////
    /* REFRESH */
    // The refresh event gets fired on #canvas initially
    // then on any <section> or other dynamically loaded/created element to "activate" it
    var embedUrl = $('link[rel="aa-embed"]').attr("href");

    //$("body").bind("refresh", function (evt) {
        $("[rel='aa:embed']").each(function () {
            var that = this;
            function poll () {
                $.ajax(embedUrl, {
                    data: {
                        url: $(that).attr("href"),
                        filter: $(that).data("filter")
                    },
                    success: function (data) {
                        if (data.ok) {
                            // NEW: december 16 (Alex)
                            // In addition to content there are three new keys:
                            // - extra_css: loads extra link rel="stylesheet"
                            // - extra_js: load extra script
                            // - script: extra javascript code to execute
                            var toGo = data.extra_css.length + data.extra_js.length;
                            var html = $(data.content);

                            $(that).replaceWith(html);
                            html.trigger("refresh");

                            $.each(data.extra_css, function(index, value) { 
                                $.getCSS(value, function() {
                                    //console.log('loaded css: ' + value);   
                                    toGo -= 0;
                                    doit();
                                });
                            });

                            $.each(data.extra_js, function(index, value) { 
                                $.getScript(value, function() {
                                    //console.log('loaded js: ' + value);   
                                    toGo -= 0;
                                    doit();
                                });
                            });

                            function doit () {
                                if (toGo == 0) {
                                    $.globalEval(data.script);
                                } else {
                                    toGo -= 1;
                                }
                            }

                            doit();
                        } else {
                            if (data.content) {
                                $(that).html(data.content);
                            }
                            window.setTimeout(poll, 2500);
                        }
                    },
                    error: function (a, b, c) {
                        // console.log("error", a, b, c);
                    }
                });
            }
            poll();
        });

        // Embed Links show/hide on rollover 
        $("body").ffind("div.aa_embed").each(function () {
            $(this).mouseover(function () {
                $(".links", this).show();
            }).mouseout(function () {
                $(".links", this).hide();
            });
        });

        // DIRECTLINKs
        // Make directlinks draggable
        $("a.directlink").each(function () {
            $(this).draggable({
                helper: function () {
                    return $(this).clone().appendTo("body");
                }
            });
        });

        // h1's are droppable to set about
        $("body").ffind(".section1").find("h1").droppable({
            accept: ".directlink",
            hoverClass: "drophover",
            drop: function (evt, ui) {
                var href = $(ui.helper).attr("href");
                var s1 = $(this).closest(".section1");
                s1.attr("about", href);
                commit_attributes(s1);
                resetTimelines();
            }
        });
    //})
});

/* vim: set foldmethod=indent: */
