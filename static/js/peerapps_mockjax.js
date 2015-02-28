var enable_mockjax = true; //set to false to disable mockjax and use the real server
if (enable_mockjax) {



    $.mockjax({
        url: "/check_peercoin_conf",
        response: function() {
            this.responseText = {
                "status":"success",
                "config":{
                    "gpg_suite_installed": Math.round(Math.random()) ? "good" : "bad",
                    "rpcuser": Math.round(Math.random()) ? "sunnyking" : "",
                    "rpcpassword": Math.round(Math.random()) ? "*******" : "",
                    "server": Math.round(Math.random()) ? "1" : "0",
                    "file_loc":"/Users/supersunny/Library/Application Support/PPCoin/ppcoin.conf",
                    "wallet_connected_status": Math.round(Math.random()) ? "good" : "bad"
                }
            }
        },
    });

    $.mockjax({
        url: "/config_automatic_setup",
        response: function() {
            this.responseText = {
                "status":"success",
                "config":{
                    "wallet_connected_status":"bad",
                    "gpg_suite_installed":"good",
                    "rpcuser":"sunnyking",
                    "rpcpassword":"*******",
                    "file_loc":"/Users/supersunny/Library/Application Support/PPCoin/ppcoin.conf",
                    "server":"1"
                }
            }
        },
    });
}