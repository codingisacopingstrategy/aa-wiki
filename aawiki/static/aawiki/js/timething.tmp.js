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


var master;


(function ($) {
    var timelines = {},
        $canvas;
        //master,
        //showTimeRemaining = false; // TIME DISPLAY STYLE FLAG


    function resynchronize (elt) {
        var sync;

        sync = $(elt).data("sync");

        if (sync) { sync.destroy(); }

        sync = $.aaMediaSync(elt);
        $(elt).data('sync', sync);
    }


    function timelineForURL(url) {
        if (! timelines[url]) {
            var driver = $("video, audio").filter("[src='" + url + "']");

            if (driver.size()) {
                driver = driver.get(0);
                timelines[url] = driver;

                resynchronize(driver);

                $(driver).timeline({
                    show: function (elt) {
                        $(elt).addClass("active");
                        //.closest('section.section1').find('div.wrapper:first').autoscrollable("scrollto", elt);
                        if ($(elt).data("aamediasync")) {
                            sync.enter(elt);
                        };
                    },
                    hide: function (elt) {
                        $(elt).removeClass("active");
                    }
                });
            }
        }
        return timelines[url];
    }


    function resetTimelines() {
        resynchronize(master);

        $canvas.timeline({
            currentTime: function (elt) {
                return master.currentTime;
            },
            show: function (elt) {
                $(elt).trigger("show");

                $("audio,video", elt).each(function () {
                    var msync = $(this).data("aamediasync");
                    if (msync) { sync.enter(this); };
                });
            },
            hide: function (elt) {
                $(elt).trigger("hide");

                $("audio,video", elt).each(function () {
                    var msync = $(this).data("aamediasync");
                    if (msync) { sync.exit(this); }
                });
            }
        });

        $("[data-start]", $canvas).each(function () {
            var start = $(this).data('start').toSeconds(),
                end = $(this).data('end').toSeconds(),
                about = $(this).closestAttr("about"),
                timeline = about ? timelineForURL(about) : $canvas.get(0),
                sync = $(timeline).data("sync");

            $("audio,video", this).each(function() {
                sync.add(this, start, end);
            });

            $(timeline).timeline("add", this, {start: start, end: end});
        });

        var maxTime = $canvas.timeline("maxTime");

        if (maxTime === undefined) {
            //$('body, #time, #playpause').hide();
        } else {
            master.setDuration(maxTime);
            //$('body, #time, #playpause').show();
            //$canvas.trigger("timeupdate"); // force time update
        }
    }


    function onAnnotationShow () {
        //var modePlay = $canvas.hasClass('play');

        $(this).addClass("active");
        $(this).attr("data-active", '').trigger('dataChange');

        //if (! modePlay) {
            //$(this).closest('section.section1').find('div.wrapper').autoscrollable("scrollto", this);
        //};
    }


    function onAnnotationHide () {
        $(this).removeClass("active");
        $(this).removeAttr("data-active").trigger('dataChange');
    }


    $(document).ready(function() {
        $canvas = $("body");
        master = new VoidPlayer($canvas.get(0));

        $("[data-start]", $canvas)
            .on("show", onAnnotationShow)
            .on("hide", onAnnotationHide)
            .on("dataChange", function () {
                console.log("ça marche!");
            });

        //$("#playpause, #time").button();
        //$("#playpause").click(function () {
            //master.paused ? master.play() : master.pause();
        //});
        //$canvas.bind("play", function () {
            //$("#playpause").text("pause");
        //}).bind("pause", function () {
            //$("#playpause").text("play");
        //});
        //$("#time").click(function () {
            //showTimeRemaining = !showTimeRemaining;
            //$canvas.trigger("timeupdate"); // force refresh
        //});

        //var slider_max = 100000;

        //$canvas.bind("timeupdate", function () {
            //var slider_val = (master.currentTime / master.duration) * slider_max;

            //$canvas.slider("option", "value", slider_val);

            //if (showTimeRemaining) {
                //$("#time").text("-" + (master.duration - master.currentTime).secondsTo("mm:ss") + " / " + master.duration.secondsTo("mm:ss"));
            //} else {
                //$("#time").text(master.currentTime.secondsTo("mm:ss") + " / " + master.duration.secondsTo("mm:ss"));
            //}

        //});

        //$('body').slider({
            //max: slider_max,
            //slide: function (evt, ui) {
                //var ct = master.duration * (ui.value / slider_max);
                //master.setCurrentTime(ct);
            //}
        //});

        $(window).on("hashchange", function(){
            var paramsHash = $.deparam.fragment();
            t = paramsHash.t.split(",")
            master.setCurrentTime(t[0]);
        })
        
        $canvas.bind("refresh", resetTimelines);
        resetTimelines()
    });
})(jQuery);

/* vim: set foldmethod=indent: */
