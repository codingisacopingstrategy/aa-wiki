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


// depends on jquery.ffind.js
// depends on jquery.wrapContent.js


(function( $ ){
    var api = $('link[rel="alternate"][type="application/json"]').attr("href");


    var createAboutButton = function () {
        //return $("<span>").text("@").addClass('about').attr('title', 'Highlight the object this annotation is about');
        return $("<span>").addClass('icon-link').attr('title', 'Highlight the object this annotation is about');
    }

    var createEditButton = function () {
        //return $("<span>").text("✎").addClass('edit').attr('title', 'Edit this annotation in place').on("click", function () {
            //$(this).closest("section").trigger("edit");
        //});
        return $("<span>").addClass("icon-pencil").addClass('edit').attr('title', 'Edit this annotation in place').on("click", function () {
            $(this).closest("section").trigger("edit");
        });
    }

    var createSaveButton = function () {
        return $("<span>").addClass("icon-ok").addClass('save').attr('title', 'Save changes').on("click", function () {
            $(this).closest("section").trigger("save");
        });
    }

    var createCancelButton = function () {
        return $("<span>").addClass("icon-remove").addClass('cancel').attr('title', 'Cancel changes').on("click", function () {
            $(this).closest("section").trigger("cancel");
        });
    }

    /**
     * Makes sure an annotation doesn't get a negative offset
     */
    var constraintAnnotation = function (elt) {
        var pos = $(elt).position();

        if (pos.top < 0) {
            $(elt).css('top', 0);
        }
        if (pos.left < 0) {
            $(elt).css('left', 0);
        }
    }

    var renumberSections = function () {
        $('section').not('[data-section="-1"]').each(function (i) {
            $(this).attr("data-section", (i + 1));
        });
    };

    var quitEditMode = function () {
        $(this).find(":header").first().find(".save").remove();
        $(this).find(":header").first().find(".cancel").remove();
        $(this).find(".section_edit").first().remove();

        $(this).removeClass("editing");
    };

    var onSectionEditTriggered = function (event) {
        event.stopPropagation()

        var height = $(this).first(".wrapper").height();
        var textarea = $("<textarea>").height(height - 4);
        $(this).append($('<div class="section_edit">').append(textarea));

        $(this).find(":header").first().append(createCancelButton());
        $(this).find(":header").first().append(createSaveButton());

        $(this).addClass("editing");

        $.ajax(api + "/section/" + $(this).data("section"), {
            dataType: 'json',
            beforeSend: function () {
                textarea.attr("disabled", "disabled").val("loading...")
            },
            success: function (data) {
                textarea.val(data.content).removeAttr("disabled");
            },
            error: function (xhr, ajaxOptions, thrownError) {
                alert("An error occured: " + xhr.status + " " + thrownError);
            },
            complete: function () {
            }
        });
    }

    var onSectionCancelTriggered = function (event) {
        event.stopPropagation()

        quitEditMode.apply(this);

    }

    var onSectionSaveTriggered = function (event) {
        event.stopPropagation()

        var that = this;
        var textarea = $(this).find(".section_edit").find("textarea");
        var content = textarea.val();

        $.ajax(api + "/section/" + $(this).data("section") + '/', {
            type: 'PUT',
            contentType: 'application/json',
            dataType: 'json',
            data: JSON.stringify({content: content}),
            beforeSend: function () {
                textarea.attr("disabled", "disabled");
            },
            success: function (data) {
                var newSection = $(data.html);
                quitEditMode.apply(that);
                foo.apply(newSection);
                $(that).replaceWith(newSection);
                renumberSections();
            },
            error: function (xhr, ajaxOptions, thrownError) {
                alert("An error occured: " + xhr.status + " " + thrownError);
                textarea.removeAttr("disabled");
            },
            complete: function () {
            }
        });

    }

    var onSectionGeometryChangeTriggered = function (event) {
        event.stopPropagation()

    }

    var onHeaderDblClickTriggered = function (event) {
        event.stopImmediatePropagation();

        var section = $(this).closest("section");

        if (! section.hasClass('editing')) {
            section.toggleClass('collapsed');
            section.trigger("geometrychange");
        }
    }

    var bar = function () {
        console.log(this);
        $(this).ffind("section").wrapContent();

        $(this).find(":header")
        .append(createEditButton);

        $(this).find("h1").attr('title', 'Drag to move. Double-click to open/close.')
        .prepend(createAboutButton);
        $(this).find("h2").attr('title', 'Double-click to open/close.');
    };

    var foo = function () {
        console.log(this);
        bar.apply(this);

        $(this).on("geometrychange", onSectionGeometryChangeTriggered);
        $(this).ffind("section").on("edit", onSectionEditTriggered)
                                .on("save", onSectionSaveTriggered)
                                .on("cancel", onSectionCancelTriggered);
        $(this).find(":header").on("dblclick", onHeaderDblClickTriggered);

        $(this).on('mousedown', function (event) {
            event.stopPropagation(); 
        }).draggable({
            cancel: 'span.edit',
            scroll: true,
            handle: 'h1',
            distance: 20,
            drag: function (event, ui) {
                if (event.ctrlKey) {
                    $("html").addClass("grid");
                    ui.position.left = Math.floor(ui.position.left / 20) * 20;
                    ui.position.top = Math.floor(ui.position.top / 20) * 20;
                } else {
                    $("html").removeClass("grid");
                }
            },
            stop: function () { 
                constraintAnnotation(this);
                $("html").removeClass("grid");
                $(this).trigger('geometrychange');
            }
        }).resizable({
            resize: function (event, ui) {
                if (event.ctrlKey) {
                    ui.size.width = Math.floor(ui.size.width / 20) * 20;
                    ui.size.height = Math.floor(ui.size.height / 20) * 20;
                    $("html").addClass("grid");
                } else {
                    $("html").removeClass("grid");
                }
            },
            stop: function () { 
                $(this).trigger('geometrychange');
             }
        });
    }

    var methods = {
        init : function (options) { 
            var settings = $.extend({
            }, options);

            renumberSections();

            return this.each(function (i) {
                foo.apply(this);
            })
        },
        destroy: function () { 
            return this.each(function(){
                $(this).off("edit");
            })
        }
    };

    $.fn.annotation = function( method ) {
        // Method calling logic
        if (methods[method]) {
            return methods[method].apply(this, Array.prototype.slice.call(arguments, 1));
        } else if (typeof method === 'object' || ! method) {
            return methods.init.apply(this, arguments);
        } else {
            $.error('Method ' + method + ' does not exist on jquery.aa.annotation');
        }        
    };
})( jQuery );
