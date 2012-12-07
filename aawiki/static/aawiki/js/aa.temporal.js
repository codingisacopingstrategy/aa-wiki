var AA = AA || {};

AA.temporal = (function () {
    /**
     * returns first playing player (unwrapped) element (if one is playing),
     * or just first player otherwise
     */
    function firstPlayer () {
        $(".player", AA.config.elts.canvas).each(function () {
            if (! this.paused) { return this; }
        });
        var vids = $(".player", AA.config.elts.canvas).first();
        if (vids.length) { return vids[0]; }
    }

    function toggleMaster () {
        master.paused ? master.play() : master.pause();
    }

    return {
        "firstPlayer": firstPlayer,
        "toggleMaster": toggleMaster,
    };
}());
