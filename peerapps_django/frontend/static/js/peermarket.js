function create_new_listing(wallet_passphrase) {
    var post_data = {
        "address": $('#peercoin_address').val(),
        "category": jQuery("#new_l_category").val(),
        "item_name": jQuery("#new_l_item_name").val(),
        "item_quantity": jQuery("#new_l_item_quantity").val(),
        "num_lots": jQuery("#new_l_num_of_lots").val(),
        "peercoin_cost": jQuery("#new_l_peercoin_cost").val()
    };

    if (wallet_passphrase) {
        post_data['wallet_passphrase'] = wallet_passphrase;
    }
    jQuery("#submit_newlisting_button").hide();
    jQuery("#submit_newlisting_loading").html('<img src="frontend/static/images/ajax-loader.gif">');
    jQuery.ajax({
        type: "POST",
        url: "/create_listing/",
        dataType: "json",
        data: post_data,
        success: function(data) {
            if (data.status == "error") {
                if ("type" in data && data.type == "wallet_locked") {
                    var wallet_passphrase = window.prompt("Submitting a blog post on the blockchain will cost 0.02 PPC.\n\nTo proceed, please enter your wallet passphrase:");
                    create_new_listing(wallet_passphrase);
                }
                else {
                    alert(data.msg);
                    $('#new_l_category').val('');
                    $('#new_l_item_name').val('');
                    $('#new_l_item_quantity').val('');
                    $('#new_l_num_of_lots').val('');
                    $('#new_l_peercoin_cost').val('');
                    jQuery("#submit_newlisting_loading").html('');
                    jQuery("#submit_newlisting_button").show();
                }
            }
            else {
                jQuery("#submit_newlisting_loading").html('');
                jQuery("#submit_newlisting_button").show();
                $('#new_message').val('');
                $('#new_message_address').val('');
                alert("Listing posted successfully!");
            }
        },
        error: function (e) {
            console.log("error", e);
            alert("Error attempting to unsubscribe.");
            jQuery("#submit_newlisting_button").show();
            jQuery("#submit_newlisting_loading").html('');
        }
    });
}

function address_updated() {
    localStorage.setItem('active_address', $('#peercoin_address').val());
    get_blogs();
    update_balance_info();
}

function update_balance_info() {
    var v = address_to_balance[$('#peercoin_address').val()];
    $('#ppc_balance').html(v+" ppc");
    var message_balance = parseInt(parseFloat(v) / 0.02);
    $("#messages_balance").html("~"+message_balance+" blog posts");
}

function blockchain_scan_status() {
    jQuery.ajax({
        type: "POST",
        url: "/blockchain_scan_status/",
        dataType: "json",
        data: {},
        success: function(data) {
            if (data.latest_block) {
                jQuery('#blockchain_status').html('Up to date <span class="glyphicon glyphicon-ok" aria-hidden="true"></span>');
                jQuery('#blockchain_status').css('color', 'green');
                setTimeout("blockchain_scan_status()", 10000);
            }
            else {
                jQuery('#blockchain_status').html('Scanning '+data.blocks_left+' blocks <span class="glyphicon glyphicon-search" aria-hidden="true"></span>');
                jQuery('#blockchain_status').css('color', 'red');
                setTimeout("blockchain_scan_status()", 3000);
            }
        },
        error: function (e) {
            console.log("error", e);
        }
    });
}

var address_to_balance = {};
$(document).ready(function(){
    jQuery.ajax({
        type: "POST",
        url: "/get_addresses/",
        dataType: "json",
        data: {},
        success: function(data) {
            var html = "";
            jQuery.each(data.data, function(k,v) {
                address_to_balance[v.address] = v.amount;
                var name = v.address;
                if (v.account) {
                    name = v.account + ": " + name
                }

                var last_active = localStorage.getItem('active_address') || null;
                var selected = "";
                if (v.address == last_active) {
                    selected = " selected";
                }
                html += '<option value="'+v.address+'"'+selected+'>'+name+'</option>';
            })
            jQuery("#peercoin_address").html(html);
            update_balance_info();
        },
        error: function (e) {
            console.log("error", e);
        }
    });
    blockchain_scan_status();

    $("[data-toggle='tooltip']").tooltip();
});