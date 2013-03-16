/*
 * Taken from
 * <http://stackoverflow.com/questions/2048720/get-all-attributes-from-a-html-element-with-javascript-jquery>
 */


(function($) {
    /**
     * function jQuery.fn.getAttributes ()
     *
     * Returns an hash of the element attributes
     *    
     *    >>> $('#foo').getAttributes();
     */
    $.fn.getAttributes = function() {
        var attributes = {}; 

        if (this.length) {
            $.each(this[0].attributes, function(index, attr) {
                attributes[attr.name] = attr.value;
            }); 
        }

        return attributes;
    };
})(jQuery);
