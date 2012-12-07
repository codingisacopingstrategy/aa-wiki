/**
 * Time format utils, taken from $media jQuery plugin (v.2.0.0)
 *
 * 2012. Created by Oscar Otero (http://oscarotero.com / http://anavallasuiza.com)
 *
 * $media is released under the GNU Affero GPL version 3.
 * More information at http://www.gnu.org/licenses/agpl-3.0.html
 */


/**
 * Extends the String object to convert any number to seconds
 *
 * '00:34'.toSeconds(); // 34
 *
 * @return float The value in seconds
 */
String.prototype.toSeconds = function () {
	'use strict';

	var time = this, ms;

	if (/^([0-9]{1,2}:)?[0-9]{1,2}:[0-9]{1,2}(\.[0-9]+)?(,[0-9]+)?$/.test(time)) {
		time = time.split(':', 3);

		if (time.length === 3) {
			ms = time[2].split(',', 2);
			ms[1] = ms[1] || 0;

			return ((((parseInt(time[0], 10) * 3600) + (parseInt(time[1], 10) * 60) + parseFloat(ms[0])) * 1000) + parseInt(ms[1], 10)) / 1000;
		}

		ms = time[1].split(',', 1);
		ms[1] = ms[1] || 0;

		return ((((parseInt(time[0], 10) * 60) + parseFloat(ms[0])) * 1000) + parseInt(ms[1], 10)) / 1000;
	}

	return parseFloat(time).toSeconds();
};



/**
 * Extends the String object to convert any number value to seconds
 *
 * '34'.secondsTo('mm:ss'); // '00:34'
 *
 * @param string outputFormat One of the avaliable output formats ('ms', 'ss', 'mm:ss', 'hh:mm:ss', 'hh:mm:ss.ms')
 *
 * @return string The value in the new format
 */
String.prototype.secondsTo = function (outputFormat) {
	'use strict';

	return this.toSeconds().secondsTo(outputFormat);
};



/**
 * Extends the Number object to convert any number to seconds
 *
 * (23.34345).toSeconds(); // 23.343
 *
 * @return float The value in seconds
 */
Number.prototype.toSeconds = function () {
	'use strict';

	return Math.floor(this * 1000) / 1000;
};


/**
 * Extends the Number object to convert any number value to seconds
 *
 * 34.secondsTo('mm:ss'); // '00:34'
 *
 * @param string outputFormat One of the avaliable output formats ('ms', 'ss', 'mm:ss', 'hh:mm:ss', 'hh:mm:ss.ms')
 *
 * @return string The value in the new format
 */
Number.prototype.secondsTo = function (outputFormat) {
	'use strict';

	var time = this;

	switch (outputFormat) {
		case 'ms':
			return Math.floor(time * 1000);

		case 'ss':
			return Math.floor(time);

		case 'mm:ss':
		case 'hh:mm:ss':
		case 'hh:mm:ss.ms':
			var hh = '';

			if (outputFormat !== 'mm:ss') {
				hh = Math.floor(time / 3600);
				time = time - (hh * 3600);
				hh += ':';
			}

			var mm = Math.floor(time / 60);
			time = time - (mm * 60);
			mm = (mm < 10) ? ("0" + mm) : mm;
			mm += ':';

			var ss = time;

			if (outputFormat.indexOf('.ms') === -1) {
				ss = Math.floor(ss);
			} else {
				ss = Math.floor(ss*1000)/1000;
			}
			ss = (ss < 10) ? ("0" + ss) : ss;

			return hh + mm + ss;
	}

	return time;
};
