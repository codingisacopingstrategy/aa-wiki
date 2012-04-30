(function($) {
    $(document).ready(function() {
        $("#help").accordion({
            autoHeight: false,
            collapsible: true
        });

        $("#accordion").accordion({ fillSpace: true });

        $('body').layout({
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
                    $('#accordion').accordion('resize');
                }
            },
        });

        $('#accordion').accordion('resize');
    });
})(jQuery);
