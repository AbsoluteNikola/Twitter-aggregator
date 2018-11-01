function setup_handlers() {
    let twit_action_func = function(id, action) {
        $.post(
            "/feed/action",
            {
                'id': id,
                'action': action
            }
        ).done(function(data, status) {
                console.log("Action '" + action + "' on twit " + id + " was successful.", data);
            }
        ).fail(function(data, status) {
            console.error("Action '" + action + "' on twit " + id + " had an error.", data, status);
        });
    };
    $("div.twit").each(function(index) {
        let twit_id = $(this).find("input:hidden").val();
        let like_btn = $(this).find("div.twit-tools-row div.twit-tools div.twit-tools-like");
        let dislike_btn = $(this).find("div.twit-tools-row div.twit-tools div.twit-tools-dislike");
        console.log(twit_id, like_btn, dislike_btn);

        like_btn.on("click", function(event) {
            twit_action_func(twit_id, "like");
        });
        dislike_btn.on("click", function(event) {
            twit_action_func(twit_id, "dislike");
        });
    })
}

function on_window_load() {
    setup_handlers();
}

$(document).ready(on_window_load)
