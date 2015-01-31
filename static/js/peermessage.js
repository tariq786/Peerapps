function address_updated() {
    localStorage.setItem('active_address', $('#peercoin_address').val());
    check_setup_status();
    get_messages();
    update_balance_info();
}

function update_balance_info() {
    var v = address_to_balance[$('#peercoin_address').val()];
    $('#ppc_balance').html(v+" ppc");
    var message_balance = parseInt(parseFloat(v) / 0.00011);
    $("#messages_balance").html("<br>~"+message_balance+" messages"); //TODO update to peercoin cost, 0.01
}

function delete_message(tx_id) {
    if(confirm("Are you sure?")) {
        jQuery.ajax({
            type: "POST",
            url: "/delete_message",
            dataType: "json",
            data: {
                "tx_id": tx_id
            },
            success: function(data) {
                get_messages();
            },
            error: function (e) {
                console.log("error", e);
                alert("Error deleting message.");
            }
        });

    }
}

function reply_to_message(id) {
    $('#new_message_address').val(id);
    $('#new_message').focus();
}

function submit_new_message() {

    jQuery("#submit_message_loading").html('<img src="static/images/ajax-loader.gif">');
    jQuery("#submit_message_button").hide();

    jQuery.ajax({
        type: "POST",
        url: "/transmit_message",
        dataType: "json",
        data: {
            "message": $('#new_message').val(),
            "from_address": $('#peercoin_address').val(),
            "to_address": $('#new_message_address').val()
        },
        success: function(data) {
            if (data.status == "error") {
                alert(data.msg);
                jQuery("#submit_message_loading").html('');
                jQuery("#submit_message_button").show();
            }
            else {
                jQuery("#submit_message_loading").html('');
                jQuery("#submit_message_button").show();
                $('#new_message').val('');
                $('#new_message_address').val('');
                alert("Message sent!");
            }
        },
        error: function (e) {
            console.log("error", e);
            jQuery("#submit_message_loading").html('');
            jQuery("#submit_message_button").show();
            alert("Error transmitting message.");
        }
    });
}

function publish_pk() {
    jQuery("#public_key_status_loading").html('<img src="static/images/ajax-loader.gif">');
    jQuery("#public_key_status_incomplete").hide();
    jQuery("#public_key_status_complete").hide();
    jQuery.ajax({
        type: "POST",
        url: "/publish_pk",
        dataType: "json",
        data: {
            "address": $('#peercoin_address').val()
        },
        success: function(data) {
            if (data.status == "error") {
                jQuery("#public_key_status_loading").html('');
                jQuery("#public_key_status_incomplete").show();
                jQuery("#public_key_status_complete").hide();
                alert(data.message);
            }
            else {
                jQuery("#public_key_status_loading").html('');
                jQuery("#public_key_status_incomplete").hide();
                jQuery("#public_key_status_complete").show();
            }
        },
        error: function (e) {
            jQuery("#public_key_status_loading").html('');
                jQuery("#public_key_status_incomplete").show();
            jQuery("#public_key_status_complete").hide();
            console.log("error", e);
            alert("Error publishing your public key.");
        }
    });
}

function setup_gpg() {
    jQuery("#local_gpg_status_loading").html('<img src="static/images/ajax-loader.gif">');
    jQuery("#local_gpg_status_incomplete").hide();
    jQuery("#local_gpg_status_complete").hide();
    jQuery.ajax({
        type: "POST",
        url: "/setup_gpg",
        dataType: "json",
        data: {
            "address": $('#peercoin_address').val()
        },
        success: function(data) {
            jQuery("#local_gpg_status_loading").html('');
            jQuery("#local_gpg_status_incomplete").hide();
            jQuery("#local_gpg_status_complete").show();
        },
        error: function (e) {
            jQuery("#local_gpg_status_loading").html('Error.');
            jQuery("#local_gpg_status_incomplete").hide();
            jQuery("#local_gpg_status_complete").hide();
            console.log("error", e);
            alert("Error setting up GPG.");
        }
    });
}

function check_setup_status() {
    jQuery.ajax({
        type: "POST",
        url: "/check_setup_status",
        dataType: "json",
        data: {
            "address": $('#peercoin_address').val()
        },
        success: function(data) {
            if(data.public_key_published) {
                jQuery("#public_key_status_loading").html('');
                jQuery("#public_key_status_incomplete").hide();
                jQuery("#public_key_status_complete").show();
            }
            else {
                jQuery("#public_key_status_loading").html('');
                jQuery("#public_key_status_incomplete").show();
                jQuery("#public_key_status_complete").hide();
            }

            if(data.gpg_keys_setup) {
                jQuery("#local_gpg_status_loading").html('');
                jQuery("#local_gpg_status_incomplete").hide();
                jQuery("#local_gpg_status_complete").show();
            }
            else {
                jQuery("#local_gpg_status_loading").html('');
                jQuery("#local_gpg_status_incomplete").show();
                jQuery("#local_gpg_status_complete").hide();
            }
        },
        error: function (e) {
            console.log("error", e);
        }
    });
}

function scan_blockchain() {
    jQuery.ajax({
        type: "POST",
        url: "/scan_blockchain",
        dataType: "json",
        data: {},
        success: function(data) {
            if (data.latest_block) {
                jQuery('#blockchain_status').html('Up to date <span class="glyphicon glyphicon-ok" aria-hidden="true"></span>');
                jQuery('#blockchain_status').css('color', 'green');
                setTimeout("scan_blockchain()", 10000);
            }
            else {
                jQuery('#blockchain_status').html('Scanning '+data.blocks_left+' blocks <span class="glyphicon glyphicon-search" aria-hidden="true"></span>');
                jQuery('#blockchain_status').css('color', 'red');
                setTimeout("scan_blockchain()", 50);
            }
        },
        error: function (e) {
            console.log("error", e);
        }
    });
}

function get_messages() {
    jQuery.ajax({
        type: "POST",
        url: "/get_messages",
        dataType: "json",
        data: {
            "address": $('#peercoin_address').val()
        },
        success: function(data) {
            var html = "";
            if (data.data.length == 0) {
                html += "No messages.";
            }
            else {
                jQuery.each(data.data, function(k,v){
                    v['time'] = moment(v['time']*1000).calendar();
                    html += ich.message_template(v, true);
                });
            }
            jQuery('#your_messages').html(html);
            setTimeout("get_messages()", 10000);
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
        url: "/get_addresses",
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
            check_setup_status();
            get_messages();
            update_balance_info();
        },
        error: function (e) {
            console.log("error", e);
        }
    });
    scan_blockchain();

    $( "#new_message_address" ).autocomplete({
        source: "autocomplete_address/",
        minLength: 0,
        select: function( event, ui ) {
            console.log( ui.item ?
              "Selected: " + ui.item.value + " aka " + ui.item.id :
              "Nothing selected, input was " + this.value );
        }
    }).focus(function() {
        $(this).autocomplete("search", $(this).val());
    });
    $("[data-toggle='tooltip']").tooltip();
});