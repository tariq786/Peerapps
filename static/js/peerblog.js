function unsubscribe(address) {
    jQuery("#"+address+"_unsubscribe").hide();
    jQuery("#"+address+"_loading_unsubscribe").html('<img src="static/images/ajax-loader.gif">');
    jQuery.ajax({
        type: "POST",
        url: "/unsubscribe",
        dataType: "json",
        data: {
            "address": address
        },
        success: function(data) {
            if (data.status == "error") {
                alert(data.msg);
            }
            else {
                get_blogs();
            }
        },
        error: function (e) {
            console.log("error", e);
            alert("Error attempting to unsubscribe.");
            jQuery("#"+address+"_unsubscribe").show();
            jQuery("#"+address+"_loading_unsubscribe").html('');
        }
    });
}

function subscribe(address) {
    jQuery("#"+address+"_subscribe").hide();
    jQuery("#"+address+"_loading_subscribe").html('<img src="static/images/ajax-loader.gif">');
    jQuery.ajax({
        type: "POST",
        url: "/subscribe",
        dataType: "json",
        data: {
            "address": address
        },
        success: function(data) {
            if (data.status == "error") {
                alert(data.msg);
            }
            else {
                get_blogs();
            }
        },
        error: function (e) {
            console.log("error", e);
            alert("Error attempting to subscribe.");
            jQuery("#"+address+"_subscribe").show();
            jQuery("#"+address+"_loading_subscribe").html('');
        }
    });
}

function view_latest(address) {
    jQuery("#"+address+"_view_latest").hide();
    jQuery("#"+address+"_loading_latest").html('<img src="static/images/ajax-loader.gif">');
    jQuery.ajax({
        type: "POST",
        url: "/view_latest_post",
        dataType: "json",
        data: {
            "address": address
        },
        success: function(data) {
            if (data.status == "error") {
                alert(data.msg);
            }
            else {
                alert(data.data);
            }
            jQuery("#"+address+"_view_latest").show();
            jQuery("#"+address+"_loading_latest").html('');
        },
        error: function (e) {
            console.log("error", e);
            alert("Error attempting to view latest.");
            jQuery("#"+address+"_view_latest").show();
            jQuery("#"+address+"_loading_latest").html('');
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
    var message_balance = parseInt(parseFloat(v) / 0.00011); //TODO update to peercoin cost, 0.01
    $("#messages_balance").html("~"+message_balance+" blog posts");
}

function submit_new_blogpost() {

    jQuery("#submit_blogpost_loading").html('<img src="static/images/ajax-loader.gif">');
    jQuery("#submit_blogpost_button").hide();

    jQuery.ajax({
        type: "POST",
        url: "/submit_blogpost",
        dataType: "json",
        data: {
            "message": $('#new_message').val(),
            "from_address": $('#peercoin_address').val(),
            "to_address": $('#new_message_address').val()
        },
        success: function(data) {
            if (data.status == "error") {
                alert(data.msg);
                jQuery("#submit_blogpost_loading").html('');
                jQuery("#submit_blogpost_button").show();
            }
            else {
                jQuery("#submit_blogpost_loading").html('');
                jQuery("#submit_blogpost_button").show();
                $('#new_message').val('');
                $('#new_message_address').val('');
                alert("Post successful!");
            }
        },
        error: function (e) {
            console.log("error", e);
            jQuery("#submit_blogpost_loading").html('');
            jQuery("#submit_blogpost_button").show();
            alert("Error transmitting blog post.");
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

function scan_blogs() {
    jQuery.ajax({
        type: "POST",
        url: "/scan_blogs",
        dataType: "json",
        data: {},
        success: function(data) {
            setTimeout("scan_blogs()", 5000);
        },
        error: function (e) {
            console.log("error", e);
        }
    });
}

function get_blogs() {
    jQuery.ajax({
        type: "POST",
        url: "/get_blogs",
        dataType: "json",
        data: {
            "address": $('#peercoin_address').val()
        },
        success: function(data) {

            //My Blog
            var html = "";
            jQuery.each(data.data.mine, function(k,v){
                v['time'] = moment(v['time']*1000).calendar();
                html += ich.myblog_template(v, true);
            });
            jQuery('#my_blog_posts').html(html);

            //Subscription Blogs
            html = "";
            jQuery.each(data.data.sub, function(k,v){
                v['time'] = moment(v['time']*1000).calendar();
                html += ich.sub_template(v, true);
            });
            jQuery('#sub_blog_posts').html(html);


            //browse_blogs
            html = "";
            jQuery.each(data.data.browse, function(k,v){
                v['latest_post_time'] = moment(v['latest_post_time']*1000).calendar();
                html += ich.browse_template(v, true);
            });
            jQuery('#browse_blogs').html(html);


            setTimeout("get_blogs()", 10000);
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
            get_blogs();
            update_balance_info();
        },
        error: function (e) {
            console.log("error", e);
        }
    });
    scan_blockchain();
    scan_blogs();

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