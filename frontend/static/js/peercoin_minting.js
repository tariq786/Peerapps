function calculateProbStake(days, coins, difficulty) {
    var prob = 0;
    if (days > 30) {
        var maxTarget = Math.pow(2, 224);
        var target = maxTarget / difficulty;
        var dayWeight = Math.min(days, 90) - 30;
        prob = (target * coins * dayWeight) / Math.pow(2, 256);
    }
    return prob;
}

$(document).ready(function() {
    $(document).ready(function() {
        $('#pminting_table').dataTable( {
            "ajax": function (data, callback, settings) {
                jQuery.ajax({
                    type: "GET",
                    url: "/peercoin_minting_data",
                    dataType: "json",
                    success: function(data) {
                        jQuery.each(data.data, function(k,v){
                            v[5] = calculateProbStake(v[4], v[3], data.difficulty);
                        })
                        callback(data);
                    },
                    error: function (e) {
                        console.log("error", e);
                    }
                });
            }

        } );
    } );
});