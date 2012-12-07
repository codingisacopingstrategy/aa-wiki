var AA = AA || {};

AA.canvas = (function () {
    function getButtonSetValues(elt) {
        var classes = [];

    }


    /**
    * Applies a class to the body
    *
    * @this HTMLDomElement
    */
    function switchMode () {
        var classes = [],
            mode = $(this).val();

        $(this).parent().find('input').each(function(i, selected) {
            classes[i] = $(selected).val();
        });

        classes = classes.join(' ').replace(mode, '');

        $canvas.removeClass(classes).addClass(mode);

        if (mode == "cinematic") {
            $("body").layout().close("west");
        } else {
            $("body").layout().open("west");
        }
    }

    function createSection () {
        $('#section-tpl').html()
        .prependTo('article')
        .trigger('refresh')
        .trigger('edit');
    };

    function tagRevision () {
        var message = window.prompt("Summary", "A nice configuration");

        if (message) {
            $.get("flag/", {
                message: "[LAYOUT] " + message
            });
        }

        return false;
    }

    //$.fn.addEditLink = function() {  
        //return this.each(function() {
        //});
    //};

    function decorateSection () {
        var $h1 = $("h1", this);

        $("<span>✎</span>")
        .addClass("edit")
        .attr('title', 'Edit this annotation in place')
        .click(function () {
            $(this).closest("section").trigger("edit");
        }).prependTo($(":header:first", this));
        
        var about = $(this).closest("section.section1").attr('about');

        $("<span>@</span>")
        .addClass("about")
        .hover(function () {
            $('.player[src="' + about + '"], section[about="' + about + '"]', $canvas)
            .addClass('highlight');
        }, function() {
            $('.player[src="' + about + '"], section[about="' + about + '"]', $canvas)
            .removeClass('highlight');
        }).prependTo($h1);
        
        $(this).find("h1, h2")
        .bind('dblclick', function(event) {
            event.stopImmediatePropagation();
            var section = $(this).closest("section");
            if (! section.hasClass('editing')) {
                section.toggleClass('collapsed');
                section.trigger("geometrychange");
            }
        })
        .filter('h1')
            .attr('title', 'Drag to move. Double-click to open/close.')
        .end()
        .filter('h2')
            .attr('title', 'Double-click to open/close.');

        var nonhead = $(this).children(":not(:header)");
        var wrapped = $('<div class="wrapper"></div>').append(nonhead);
        
        $(this).append(wrapped);
    }

    /**
     * Makes sure an annotation doesn't get a negative offset
     */
    function constraintAnnotation (elt) {
        var pos = $(elt).position();

        if (pos.top < 0) {
            $(elt).css('top', 0);
        }
        if (pos.left < 0) {
            $(elt).css('left', 0);
        }
    }

    function renumberSections () {
        $('section', AA.$.canvas)
        .not('[data-section="-1"]')
            .each(function(i) {
                $(this).attr("data-section", (i + 1));
            });
    }

    function editSection (event) {
        function edit (data) {
            var position = $(that).css("position");
            var section_height = Math.min($(window).height() - 28, $(that).height());
            var use_height = (position == "absolute") ? section_height : section_height;
            var f = $("<div>").addClass("section_edit").appendTo(that);
            var textarea = $("<textarea>").css({height: use_height + "px"}).text(data).appendTo(f);
            $(that).addClass("editing");
            var ok = $("<span>✔</span>").addClass("save").attr('title', 'Save').click(function () {
                $.ajax("edit/", {
                    type: 'post',
                    data: {
                        section: $(that).data("section"),
                        content: textarea.val()
                    },
                    success: function (data) {
                        var new_content = $(data);
                        $(that).replaceWith(new_content);
                        new_content.trigger("refresh");
                    }
                });
            }).prependTo($(that).find(':header:first'));
            $("<span>✘</span>").addClass("cancel").attr('title', 'Cancel').click(function () {
                if (new_section) {
                    // removes the annotation
                    $(that).remove(); 
                    $(this).remove(); 
                    ok.remove(); 
                } else {
                    f.remove();
                    $(this).remove(); 
                    ok.remove(); 
                    $(that).removeClass("editing");
                }
            }).prependTo($(that).find(':header:first'));
        }

        evt.stopPropagation();

        var that = this;
        var new_section = false;

        if ($(this).data('section') == -1) {
            // Directly enter edit mode
            new_section = true;
            edit("# New");
        } else {
            // Initiate the edit by GETting the markdown source
            $.ajax("edit/", {
                data: {
                    section: $(this).data("section")
                },
                success: edit
            });
        }
    }

    AA.$.addSection.click(AA.fn.createSection);
    AA.$.saveRevision.click(AA.fn.tagRevision);

    $("#mode").buttonset();
    $("#mode input").change(AA.utils.switchMode);

    return {
        "createSection": createSection,
        "tagRevision": tagRevision,
        "decorateSection": decorateSection,
        "constraintAnnotation": constraintAnnotation,
        "renumberSections": renumberSections
    };
}());
