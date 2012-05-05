/**
 * VoidPlayer is released under the GNU Affero GPL version 3.
 * More information at http://www.gnu.org/licenses/agpl-3.0.html
 */

(function($) {

	window.VoidPlayer = function (element, opts) {
        opts = $.extend({
            duration: 3600,
            loop: false
        }, opts);

		this.element = element;
		this.$element = $(element);
        this.paused = true;
        this.duration = opts.duration;
        this.currentTime = 0;
        this.loop = opts.loop;

        /* Void player is always ready ! */
        this.readyState = 4;
        this.seeking = false;

        this.interval_id = undefined;
        // console.log("duration", this.duration);
	}

	VoidPlayer.plugins = {};

    VoidPlayer.prototype.setDuration = function (d) {
        this.duration = d;
    }

    VoidPlayer.prototype.play = function () {
        // console.log("voidplayer.play");
        if (!this.interval_id) {
            // console.log("VoidPlayer.play setInterval,", this.interval_id);
            this.paused = false;
            var that = this;
            this.start = new Date().getTime() - (this.currentTime * 1000);
            this.interval_id = window.setInterval(function () {
                var now = new Date();
                var nextTime = (now - that.start) / 1000;
                if (nextTime > that.duration) {
                    that.currentTime = 0;
                    if (!that.loop) { that.pause(); };
                } else {
                    that.currentTime = nextTime;
                };
                that.$element.trigger("timeupdate");
            }, 250);
            // THIS MUST BE AT THE END (TO AVOID UNSTABLE/RACE CONDITIONS)
            this.$element.trigger("play");
        }
    }

    VoidPlayer.prototype.pause = function () {
        if (this.interval_id) {
            // console.log("VoidPlayer.pause");
            this.paused = true;
            window.clearInterval(this.interval_id)
            this.interval_id = null;
            this.$element.trigger("pause");
        }
    }

    /*
    Firefox event sequence on <video> seek:
        seeking
        timeupdate
        seeked
        canplay
        canplaythrough
    Chrome event sequence on <video> seek:
        seeked
        timeupdate
        seeking
    */


    VoidPlayer.prototype.setCurrentTime = function (t) {
        var browser = $.browser;

        this.currentTime = t;
        this.start = new Date().getTime() - (this.currentTime * 1000);

        if (browser.webkit) {
            this.$element.trigger("seeked");
            this.$element.trigger("timeupdate");
            this.$element.trigger("seeking");
        } else {
            this.$element.trigger("seeking");
            this.$element.trigger("timeupdate");
            this.$element.trigger("seeked");
            this.$element.trigger("canplay");
            this.$element.trigger("canplaythrough");
        };
    }

})(jQuery);



// jQuery.media timecode funcs
/**
 * function String.toSeconds ()
 *
 * Convert any number to seconds
 */
String.prototype.toSeconds = function () {
	var time = this;

	if (/^([0-9]{1,2}:)?[0-9]{1,2}:[0-9]{1,2}(\.[0-9]+)?(,[0-9]+)?$/.test(time)) {
		time = time.split(':', 3);

		if (time.length == 3) {
			var ms = time[2].split(',', 2);
			ms[1] = ms[1] ? ms[1] : 0;

			return ((((parseInt(time[0], 10) * 3600) + (parseInt(time[1], 10) * 60) + parseFloat(ms[0])) * 1000) + parseInt(ms[1], 10)) / 1000;
		}

		var ms = time[1].split(',', 1);
		ms[1] = ms[1] ? ms[1] : 0;

		return ((((parseInt(time[0], 10) * 60) + parseFloat(ms[0])) * 1000) + parseInt(ms[1], 10)) / 1000;
	}

	return parseFloat(time).toSeconds();
}


/**
 * function String.secondsTo (outputFormat)
 *
 * Convert a seconds time value to any other time format
 */
String.prototype.secondsTo = function (outputFormat) {
	return this.toSeconds().secondsTo(outputFormat);
}


/**
 * function Number.toSeconds ()
 *
 * Convert any number to seconds
 */
Number.prototype.toSeconds = function () {
	return Math.round(this * 1000) / 1000;
}


/**
 * function Number.secondsTo (outputFormat)
 *
 * Convert a seconds time value to any other time format
 */
Number.prototype.secondsTo = function (outputFormat) {
	var time = this;

	switch (outputFormat) {
		case 'ms':
			return Math.round(time * 1000);

		case 'mm:ss':
		case 'hh:mm:ss':
		case 'hh:mm:ss.ms':
			var hh = '';

			if (outputFormat != 'mm:ss') {
				hh = Math.floor(time / 3600);
				time = time - (hh * 3600);
				hh += ':';
			}

			var mm = Math.floor(time / 60);
			time = time - (mm * 60);
			mm = (mm < 10) ? ("0" + mm) : mm;
			mm += ':';

			var ss = time;

			if (outputFormat == 'hh:mm:ss' || outputFormat == 'mm:ss') { // MLM: added mm:ss
				ss = Math.round(ss);
			}
			ss = (ss < 10) ? ("0" + ss) : ss;

			return hh + mm + ss;
	}

	return time;
};

