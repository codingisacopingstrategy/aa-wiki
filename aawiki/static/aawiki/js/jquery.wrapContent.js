/*
 * Copyright 2011 Alexandre Leray <http://stdin.fr/>
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


(function($) {
    /**
     * function jQuery.fn.wrapContent (selector)
     *
     * Wraps all the children of an element but the headers. 
     *    
     *    >>> $('section').wrapContent('<section class="wrapper">');
     */
    $.fn.wrapContent = function(selector) {  
        var selector = selector || '<div class="wrapper">';

        return $(this).each(function() {
            $(this).children(":not(:header)").wrapAll(selector);
        });
    };
})(jQuery);
