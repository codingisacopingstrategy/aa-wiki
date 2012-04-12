(function ($) {
//////////////////////////////
// SYNCING CODE

// var when_all_ready_callbacks = [];

// SEEKING:    Become the driver (if no one else is already), remember my playstate, pause all
// SEEKED:     If I am the driver, (pause yourself -- ff hack), when_all_ready: relinquish driver role, play all (if I was playing when seeking began)
// TIMEUPDATE: If I am the driver, this is a "scrub": Set other elements' currentTime accordingly
// PLAY:       Become the driver (if no one else is already), (pause self -- ff hack?): when_all_ready: play all -- relinquish driver role (with some delay!?)
// allow request for play to work together with a scrub

function aaMediaSync (element, opts) {
    var that = {element: element},
        allmedia = [element],
        syncedmedia = [element],
        uid = 0,
        driver = null,
        initiatingGroupPlay = false,
        driver_scrubstart_paused = undefined;
    
    opts = $.extend({
        trace: false
    }, opts);


    // console.log("aaMediaSync", element);

    bindevents(element);

    function remove (array, elt) {
        for (var i=0, l=array.length; i<l; i++) {
            if (array[i] === elt) { array.splice(i, 1); return i; }
        }
    }

    function add(elt, start, end) {
        var id = ++uid;
        allmedia.push(elt);
        syncedmedia.push(elt);
        // console.log("aamediasync.add", elt, start, end);
        $(elt).data("aamediasync", {start: start, end: end});
        bindevents(elt);
    }
    that.add = add;

    function get_all_ready () {
        var i, l, m;
        for (i=0, l=syncedmedia.length; i<l; i++) {
            m = syncedmedia[i];
            // if (!is_visible(m)) { continue; }
            if (! ((m.readyState >= 3) && !m.seeking) ) {
                return false;
            }
        }
        return true;
    }

    function when_all_ready (callback) {
        // abstract me (use syncedmedia array)
        // Does this need to be written to work with the EVENTS SYSTEM (to stay properly in sync ?!)
        if (opts.trace) console.log("when_all_ready", syncedmedia.length);
        if (get_all_ready() === true) { callback(); } else {
            window.setTimeout(function () { when_all_ready(callback) }, 100);
            // when_all_ready_callbacks.push(callback);
        }
    }

    function get_start_time (elt) {
        if (elt === element)
            return 0;
        else {
            var data = $(elt).data("aamediasync");
            return data.start || 0;
        }
    }

    function setCurrentTime(elt, t) {
        // if (!is_visible(elt)) return;
        if (elt.setCurrentTime) {
            elt.setCurrentTime(t);
        } else {
            try {
                elt.currentTime = t;
            } catch (e) {
                //console.log("error setting time", elt, t);
            }
        }
    }

    function getRelativeTime(ref, forElt) {
        // ref.currentTime is used as reference forElt
        // returns currentTime for forElt, given ref.currentTime
        var reftime = (ref === syncedmedia[0]) ? ref.currentTime : ref.currentTime + get_start_time(ref);
        return (reftime - get_start_time(forElt));
    }

    function bind (elt, msg, callback) {
        if (elt.element !== undefined) {
            // Bind to DOM element, Arrange for callback to have the JS object as this (a.l.d. element)
            $(elt.element).bind(msg, function () {
                callback.call(elt)
            });
        } else {
            // Bind as normal
            $(elt).bind(msg, callback);
        }
    }

    function is_visible (elt) {
        if (elt.element !== undefined) {
            return $(elt.element).is(":visible");
        } else {
            return $(elt).is(":visible");
        }
    }

    function enter (elt) {
        // console.log("enter", elt);
        // sync elt time to timeline
        var rt = getRelativeTime(element, elt);
        if (opts.trace) console.log("enter", elt, rt);
        setCurrentTime(elt, rt);
        syncedmedia.push(elt);
        if (!element.paused) {
            // if (trace) console.log("enter: trigger group play");
            element.pause();
            element.play();
        }
    }
    that.enter = enter;

    function exit (elt) {
        // console.log("exit", elt);
        if (opts.trace) console.log("exit");
        remove(syncedmedia, elt);
        elt.pause();
    }
    that.exit = exit;

    function groupplay (triggering_elt) {
        if (opts.trace) console.log("initiate groupplay");
        if (get_all_ready()) {
            $(syncedmedia).each(function () {
                if (this != triggering_elt) { //  && is_visible(this)) {
                    this.play() 
                }
            });
            return;
        }
        initiatingGroupPlay = true;
        if (triggering_elt) triggering_elt.pause();
        when_all_ready(function () {
            if (opts.trace) console.log("ready, calling play");
            // timeline.play();
            $(syncedmedia).each(function () {
                // if (is_visible(this)) {
                    this.play() 
                //}
            });
            window.setTimeout(function () {
                initiatingGroupPlay = false;
            }, 500);
        });
    }

    function bindevents (elt) {
        bind(elt, "seeking.aamediasync", function () {
            if (opts.trace) console.log("seeking", this);
            if (driver === null) {
                driver = this;
                driver_scrubstart_paused = this.paused;
                // PAUSE ALL
                // timeline.pause();
                $(syncedmedia).each(function () { this.pause(); });
            }
        });
        bind(elt, "seeked.aamediasync", function () {
            if (driver === this) {
                // driver = null;
                this.pause(); // HACK TO OVERRIDE (firefox) scrub resuming play
                when_all_ready(function () {
                    // console.log("driver = null", driver_scrubstart_paused);
                    driver = null;
                    // restore play state
                    if (!driver_scrubstart_paused) {
                        // console.log("restore play state audio");
                        // timeline.play();
                        $(syncedmedia).each(function () {
                            // if (is_visible(this)) { this.play(); }
                            this.play(); 
                        });
                    }
                });
            }
        })
        bind(elt, "timeupdate.aamediasync", function () {
            var media = $(this).data("media");
            if (driver === this) {
                // SCRUB (timeupdate while buffering = scrub event ?!)
                if (opts.trace) console.log("scrub", this.currentTime, this);
                // SET OTHER TIMES BASED OFF OF THIS ELEMENT
                //timeline.setCurrentTime(get_start_time(this) + this.currentTime);
                var eventreceiver = this;
                $(syncedmedia).each(function () {
                    if (this !== eventreceiver) {
                        var newtime = getRelativeTime(eventreceiver, this);
                        // console.log("getRelativeTime", eventreceiver, this, newtime);
                        setCurrentTime(this, newtime);
                        // var time = timeline.currentTime - get_start_time(this);
                        // if (time >= 0) { this.currentTime = time; }
                    }
                });
            }
        });
        bind(elt, "play.aamediasync", function () {
            // console.log(elt, "play");
            if (initiatingGroupPlay === false) {
                groupplay(this);
            }
        });
        bind(elt, "pause.aamediasync", function () {
            // console.log(elt, "pause");
            var eventreceiver = this;
            // if (is_visible(this) && initiatingGroupPlay === false && driver === null) {
            if (initiatingGroupPlay === false && driver === null) {
                // TRIGGER GROUP PAUSE
                // timeline.pause();
                $(syncedmedia).each(function () {
                    if (this !== eventreceiver) {
                        this.pause();
                    }
                });
            }
        });
    }
    function destroy () {
        // NB: destroy should be called if a sync element is dropped or replaced.
        // It unbinds all events to avoid future (often duplicate) reception of the events
        $(allmedia).each(function () {
            if (this.element) {
                $(this.element).unbind('.aamediasync');
            } else {
                $(this).unbind(".aamediasync");
            }
        });
        // maybe not strictly necessary, but...
        allmedia = null;
        syncedmedia = null;
    }
    that.destroy = destroy;

    return that;
}
$.aaMediaSync = aaMediaSync;

})(jQuery);

