if (typeof (AA) === 'undefined') AA = {};


AA.annotations = (function ($) {

  // *-* public methods *-*

  var init = function () {
      decorate("section");
      $("section").on("edit", editSection);
  };

  // *-* utility methods *-*

  var wrapSectionContent = function () {
        var content = $(this).children(":not(:header)");
        var wrapped = createWrapper().append(content);
        $(this).append(wrapped);
  }

  var createWrapper = function () {
      return $("<div>").addClass("wrapper");
  }

  var createAboutButton = function () {
      return $("<span>").text("@").addClass('about').attr('title', 'Edit this annotation in place');
  }

  var createEditButton = function () {
      return $("<span>").text("✎").addClass('edit').attr('title', 'Edit this annotation in place').on("click", function () {
        $(this).closest("section").trigger("edit");
      });
  }

  var editSection = function () {
      console.log(this);
  }

  var decorate = function (selector) {
      $(selector).find("h1")
      .append(createEditButton())
      .prepend(createAboutButton());
  }

  // *-* event methods *-*

  //var eventHeaderClicked = function () {
    //doThing(this.attr('id'));
  //};

  // expose public methods
  return {
    init: init
  };
})(jQuery);


jQuery(document).ready(AA.annotations.init());
