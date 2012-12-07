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
 *
 *
 * @requires jquery.datetimecode.js
 * @requires jquery.caret.js
 */


(function($) {

var currentTextArea; /* used for timecode pasting */
var timelinesByURL = {};
var $canvas;
var $sidebar;
var embedUrl;
var master;
var showTimeRemaining = false; // TIME DISPLAY STYLE FLAG

function commit_attributes (elt) {
    "use strict";
    /*
     * Updates and posts the annotation attributes
     */
    // TODO: update the regex to match timecodes as well
    // RegExp
    // FIXME: find how \s can not match newlines
    var TIMECODE_RE =    /(^|\n)(\d{2}:\d{2}:\d{2}([.,]\d{1,3})?\s*-->\s*(\d{2}:\d{2}:\d{2}([.,]\d{1,3})?)?.*?)(\n|$)/;
    var HASH_HEADER_RE = /(^|\n)(#{1,2}[^#].*?)#*(\n|$)/;
    var ATTR_RE = /{:[^}]*}/;
    var NON_PERSISTANT_CLASSES = ['section1', 'section2', 'ui-droppable',
            'ui-draggable', 'ui-resizable', 'ui-draggable-dragging', 'editing',
            'highlight', 'drophover', 'active'].join(' ');

    // As we don't want all attributes/values to be persistent we need to
    // perform some cleaning first. In order not to alter the original element
    // we create a clone and perform the cleaning on it instead.
    var $elt = $(elt).clone()
        .removeClass(NON_PERSISTANT_CLASSES)
        .css({
            // we only want the record the visibility if the element is hidden...
            'display': $(elt).is(":visible") ? "" : "none",
            'position': ''
        });

    // Removes extra whitespaces
    var about = $.trim($elt.attr('about'));
    var style = $.trim($elt.attr('style'));
    var class_ = $.trim($elt.attr('class'));

    // Constructs the markdown source
    var attr_chunk = "{: ";
    if (about) { attr_chunk += "about='" + about + "' "; }
    if (style) { attr_chunk += "style='" + style + "' "; }
    if (class_) { attr_chunk += "class='" + class_ + "' "; }
    attr_chunk += "}" ;
    attr_chunk = (attr_chunk == "{: }") ? "" : attr_chunk;  // Removes empty attribute list junk


    var section = $(elt).data("section");
    if (section == -1) {
        // cancel anonymous section save -- BUG: duplicates sections by requesting section -1 (last)
        return;
    }

    $.get("edit/", {
        section: section
    }, function(data) {
        // Searches for Header
        //var header_match = HASH_HEADER_RE.exec(data) ? HASH_HEADER_RE.exec(data) : TIMECODE_RE.exec(data);
        var header_match = HASH_HEADER_RE.exec(data);
        if (header_match) {
            var start, end;
            // Defines the substring to replace
            var attr_match = ATTR_RE.exec(header_match[0]);
            if (attr_match) {
                start = header_match.index + attr_match.index;
                end = start + attr_match[0].length;
            } else {
                start = header_match.slice(1, 3).join('').length;
                end = start;
            }
            var before = data.substring(0, start);
            var after = data.substring(end, data.length);
            
            $.post("edit/", {
                content: before + attr_chunk + after,
                section: section
            });
        }
    });
}

function placeLandmarks () {
    $('#lines').remove();
    var slider_elt = $('#timelineslider');
    var slider_elt_width = slider_elt.width() - 26;
    var left = slider_elt.position().left;
    var right = left + slider_elt.width();
    var duration = master.duration; // $("body").timeline('maxTime');
    var lines = $('<div>').attr('id', 'lines');
    if (typeof(duration) == "object") {
        duration = $.date2secs(duration);
    }
    var j = 0;
    $('section.section1').each(function(i) {
        var section2 = $('section.section2', this);
        if (section2.length) {
            var line = $("<div>").addClass('line');
            section2.each(function() {
                var $this = $(this);
                var extraClass = $(this).has('audio').length ? 'audio ' : 'normal'; 
                var start = $(this).data('start');
                if (typeof(start) == "undefined") {
                    return;
                }
                var end = $(this).data('end');
                if (typeof(end) == "undefined") {
                    return;
                }
                var offset = $.timecode_tosecs(start) / duration;
                var width = ($.timecode_tosecs(end) - $.timecode_tosecs(start)) / duration;
                var foo = $('<a>').attr('href', '#').addClass('landmark').css({
                    'left': (100 * offset) + "%",
                    'width': (100 * width) + "%",
                }).addClass(extraClass).data('position', start)
                    .attr('title', start + " --> " + end)
                    .bind('click', function() {
                        $this.find('span[property="aa:start"]').click();
                    })
                    .appendTo(line);

                $('a[rel="aa:landmark"]', this).each(function() {
                    foo.addClass('foo');
                });
            });

            line.appendTo(lines);
            j += 1;
        }
        lines.appendTo('#timeline');
    });
}


function resetTimelines() {
    /* create timeline */
    
    var sync = $("#timelineslider").data("sync");
    if (sync) { sync.destroy(); } 
    sync = $.aaMediaSync(master, {trace: false});
    $("#timelineslider").data("sync", sync).timeline({
        currentTime: function (elt) {
            return master.currentTime;
        },
        show: function (elt) {
            var modePlay = $canvas.hasClass('play');
            // try { $("audio,video", elt).get(0).play(); }
            // catch (e) {}
            $(elt).addClass("active")
            if (!modePlay) {
                $(elt).closest('section.section1')
                   .find('div.wrapper')
                        .autoscrollable("scrollto", elt);
            };
            $("audio,video", elt).each(function () {
                var msync = $(this).data("aamediasync");
                // console.log("show", this);
                if (msync !== undefined) sync.enter(this);
            });
        },
        hide: function (elt) {
            // try { $("audio,video", elt).get(0).pause(); }
            // catch (e) {}
            $(elt).removeClass("active");
            $("audio,video", elt).each(function () {
                var msync = $(this).data("aamediasync");
                // console.log("hide", this);
                if (msync !== undefined) sync.exit(this);
            });
        } // ,
        // start: function (elt) { return $.timecode_parse($(elt).attr("data-start")); },
        // end: function (elt) { return $.timecode_parse($(elt).attr("data-end")); }
    });

    /* Find/Init/Return a timeline-enabled media element for a given (about) url */
    function timelineForURL(url) {
        if (timelinesByURL[url] === undefined) {
            var driver = $("video[src='" + url + "'], audio[src='" + url + "']").first();
            if (driver.size()) {
                driver = driver.get(0);
                timelinesByURL[url] = driver;
	            var sync = $(driver).data("sync");
                if (sync) {
                   console.log("dropping old sync");
            sync.destroy();
                }
                sync = $.aaMediaSync(driver);
                $(driver).data('sync', sync).timeline({
                    show: function (elt) {
                        $(elt).addClass("active")
                            .closest('section.section1')
                               .find('div.wrapper:first')
                                    .autoscrollable("scrollto", elt);
                        if ($(elt).data("aamediasync") !== undefined) sync.enter(elt);
                    },
                    hide: function (elt) {
                        $(elt).removeClass("active");
                    }
                });
            } else {
                //console.log("WARNING, no media found for about=", url);
            }
        }
        return timelinesByURL[url];
    }

    /* ACTIVATE TEMPORAL HTML! */
    $("[data-start]", $canvas).each(function () {
        var about_url = $.trim($(this).closest("[about]").attr("about")),
            start = $.timecode_parse($(this).attr('data-start')),
            end = $.timecode_parse($(this).attr('data-end')),
            timeline = about_url ? timelineForURL(about_url) : $("#timelineslider").get(0);
        // console.log("temporal section", this, "timeline", timeline);
        if (timeline) {
			// SYNC EMBEDDED MEDIA (needs to happen first to properly "receive" the show/hide event)
			var sync = $(timeline).data("sync");
			$("audio,video", this).each(function() {
                // console.log("adding media", this, start, end);
	    		sync.add(this, start, end);
			});
            // ADD THE SECTION
            $(timeline).timeline("add", this, {start: start, end: end});
        }
    });

    /* Set master.duration or else hide the slider if there are no titles attached to the page timeline */
    var maxTime = $("#timelineslider").timeline("maxTime");
    // console.log("maxTime", maxTime);
    if (maxTime === undefined) {
        $('#timelineslider, #time, #playpause').hide();
    } else {
        master.setDuration(maxTime);
        $('#timelineslider, #time, #playpause').show();
        $("#timelineslider").trigger("timeupdate"); // force time update
    }
}


/*** INIT ***/
$(document).ready(function() {
    master = new VoidPlayer($('#timelineslider').get(0));
    slider_max = 100000;

    $("#playpause, #time").button();
    $("#playpause").click(AA.utils.toggleMaster);

    $("#timelineslider").bind("play", function () {
        $("#playpause").text("pause");
    }).bind("pause", function () {
        $("#playpause").text("play");
    });
    $("#time").click(function () {
        showTimeRemaining = !showTimeRemaining;
        $("#timelineslider").trigger("timeupdate"); // force refresh
    });

    $("#timelineslider").bind("timeupdate", function () {
        var slider_val = (master.currentTime / master.duration) * slider_max;
        $("#timelineslider").slider("option", "value", slider_val);
        if (showTimeRemaining) {
            $("#time").text("-" + (master.duration-master.currentTime).secondsTo("mm:ss") + " / " + master.duration.secondsTo("mm:ss"));
        } else {
            $("#time").text(master.currentTime.secondsTo("mm:ss") + " / " + master.duration.secondsTo("mm:ss"));
        }

    });

    $('#timelineslider').slider({
        max: slider_max,
        slide: function (evt, ui) {
            var ct = master.duration * (ui.value/slider_max);
            master.setCurrentTime(ct);
        }
    });
    
    $("section.section1 > div.wrapper", $canvas).autoscrollable();  // FIXME: quick fix to make autoscrollable work on load

    ////////////////////////////////////////////////////////////////////////
    /* REFRESH */
    // The refresh event gets fired on #canvas initially
    // then on any <section> or other dynamically loaded/created element to "activate" it
    $canvas.bind("refresh", function (evt) {
        var context = evt.target;

        /* Clickable timecodes {{{ */
        $(context).ffind('span[property="aa:start"], span[property="aa:end"]').bind("click", function () {
            var about = $(this).parents('[about]').attr('about');
            var timeline;
            if (about) {
                timeline = timelinesByURL[about];
            } else {
                timeline = $("body").get(0);
            }
            if (timeline) {
                var t = $.timecode_parse($(this).attr("content"));
                $(timeline).timeline("currentTime", t);
            }
            var t = $.timecode_tosecs_attr($(this).attr("content"));
            var player = $('[src="' + about + '"]')[0] 
                      || $('source[src="' + about + '"]').parent('.player')[0];
            if (player) {
                player.currentTime = t;
                player.play();
            }
        });
        /* }}} */

        /* Connect players to timed sections */
        resetTimelines();

        /* }}} */

        if ($('#timelineslider').is(':visible')) {
            placeLandmarks();
        }
    });
});

})(jQuery);

/* vim: set foldmethod=indent: */
