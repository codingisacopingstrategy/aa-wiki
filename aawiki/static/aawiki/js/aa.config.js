var AA = AA || {};

AA.$ = (function () {
    return {
        "help": $("#help"),
        "accordion": $("#accordion"),
        "body": $("body"),
        "center": $("#center"),
        "canvas": $("#canvas"),
        "addSection": $("#add"),
        "saveRevision": $("#save"),
        "sidebar": $("#sidebar")
    };
}());

AA.url = (function () {
    return {
        "embed": $("link[rel='aa-embed']").attr("href")
    };
}());
